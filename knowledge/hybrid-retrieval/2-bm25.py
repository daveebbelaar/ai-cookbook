"""
Sparse retrieval with BM25. Builds an index over the FiQA corpus, persists
it to disk, and runs a query.

BM25 is keyword-based: it scores documents by term frequency, weighted against
how rare each term is across the corpus. No model, no embeddings, no GPU. It
nails exact terms and rare words. It loses on paraphrase.

We use bm25s, a pure-Python implementation that is ~500x faster than the older
rank_bm25 and has built-in save/load.

More info: https://github.com/xhluca/bm25s
"""

from pathlib import Path
import bm25s
import pandas as pd

DATA_DIR = Path(__file__).parent / "data" / "fiqa"
INDEX_DIR = Path(__file__).parent / "indexes" / "bm25"


# --------------------------------------------------------------
# Step 1: Load the corpus
# --------------------------------------------------------------

# FiQA docs are forum posts; the 'title' column is empty for every row,
# so we index on 'text' directly.
corpus = pd.read_parquet(DATA_DIR / "corpus.parquet")
doc_ids = corpus["_id"].tolist()
doc_texts = corpus["text"].tolist()

print(f"Indexing {len(doc_texts)} documents with BM25...")


# --------------------------------------------------------------
# Step 2: Tokenize and build the index
# --------------------------------------------------------------

# bm25s.tokenize lowercases, strips punctuation, and removes English stopwords.
# The result is a Tokenized object that you hand straight to BM25.index().
tokens = bm25s.tokenize(doc_texts, stopwords="en")

print(tokens.ids[:1])  # list[list[int]] -- one inner list per doc
print(list(tokens.vocab.items())[:10])  # dict[str, int] -- token string -> integer ID

retriever = bm25s.BM25()  # method='lucene' by default
retriever.index(tokens)


# --------------------------------------------------------------
# Step 3: Persist the index to disk
# --------------------------------------------------------------

# Save the index plus the doc_ids in matching order, so we can map back later.
INDEX_DIR.mkdir(parents=True, exist_ok=True)
retriever.save(str(INDEX_DIR))
(INDEX_DIR / "doc_ids.txt").write_text("\n".join(doc_ids))


# --------------------------------------------------------------
# Step 4: Run a query
# --------------------------------------------------------------


def search_bm25(query: str, k: int = 10) -> list[tuple[str, float]]:
    """Return the top-k (doc_id, score) pairs for a query."""
    query_tokens = bm25s.tokenize([query], stopwords="en")
    indices, scores = retriever.retrieve(query_tokens, k=k)
    # indices[0] is a numpy array of integer positions in doc_ids.
    return [
        (doc_ids[i], float(scores[0][j])) for j, i in enumerate(indices[0].tolist())
    ]


if __name__ == "__main__":
    query = "Where should I park my rainy-day fund?"
    print(f"\nQuery: {query}\n")
    for i, (doc_id, score) in enumerate(search_bm25(query, k=5), 1):
        text = corpus.loc[corpus["_id"] == doc_id, "text"].iloc[0]
        print(f"{i}. [{score:6.2f}] {doc_id}  {text[:80]}")
