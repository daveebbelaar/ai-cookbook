"""
Reranking: take the top-50 candidates from RRF and reorder them with a
cross-encoder. Return the top-10.

A bi-encoder (the dense retriever from 3-embed.py) embeds the query and the
document separately, then compares with cosine. A cross-encoder feeds the
query and document INTO the same model and returns a single relevance score.
Cross-encoders are slower, but the joint attention catches subtleties that
two independent embeddings miss.

We use Cohere rerank-v4.0-fast.

More info: https://docs.cohere.com/docs/rerank-overview
"""

import os
import cohere
from dotenv import load_dotenv
from utils.fusion import hybrid_candidates
from utils.retrievers import BM25Retriever, DenseRetriever, load_corpus

load_dotenv()
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
RERANK_MODEL = "rerank-v4.0-fast"


# --------------------------------------------------------------
# Step 1: Load retrievers and corpus
# --------------------------------------------------------------

bm25 = BM25Retriever()
dense = DenseRetriever()
corpus_by_id = load_corpus().set_index("_id")


# --------------------------------------------------------------
# Step 2: Rerank with a cross-encoder
# --------------------------------------------------------------


def search_reranked(
    query: str, k: int = 10, candidate_k: int = 50
) -> list[tuple[str, float]]:
    candidates = hybrid_candidates(query, bm25, dense, candidate_k=candidate_k)
    candidate_ids = [doc_id for doc_id, _ in candidates]
    candidate_texts = [corpus_by_id.loc[d, "text"] for d in candidate_ids]

    response = co.rerank(
        model=RERANK_MODEL,
        query=query,
        documents=candidate_texts,
        top_n=k,
    )

    return [(candidate_ids[r.index], r.relevance_score) for r in response.results]


# --------------------------------------------------------------
# Step 3: Compare hybrid vs hybrid + rerank
# --------------------------------------------------------------


def show(label: str, results: list[tuple[str, float]]) -> None:
    print(f"\n{label}")
    for i, (doc_id, score) in enumerate(results[:5], 1):
        text = corpus_by_id.loc[doc_id, "text"]
        print(f"  {i}. [{score:.4f}] {doc_id}  {text[:70]}")


if __name__ == "__main__":
    query = "Where should I park my rainy-day fund?"
    print(f"Query: {query}")

    show("Hybrid (RRF) only", hybrid_candidates(query, bm25, dense, candidate_k=50)[:5])
    show("Hybrid + Cohere rerank-v4.0-fast", search_reranked(query, k=5))
