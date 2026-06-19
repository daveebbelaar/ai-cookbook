"""
Reciprocal Rank Fusion (RRF). Combine BM25 and dense retrieval into one
ranked list.

The naive idea is 'average the scores', but BM25 scores are unbounded and
cosine similarities sit in [0, 1]. The fix is to fuse RANKINGS, not scores.

    rrf_score(d) = sum over each retriever r of 1 / (k + rank_r(d))

k is a smoothing constant, conventionally 60. The original 2009 paper called
it 'simple but effective' and that is still the consensus in 2026.

More info: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
"""

from collections import defaultdict
from utils.retrievers import BM25Retriever, DenseRetriever, load_corpus

K_RRF = 60


# --------------------------------------------------------------
# Step 1: The fusion function
# --------------------------------------------------------------


def reciprocal_rank_fusion(
    rankings: list[list[str]], k: int = K_RRF
) -> list[tuple[str, float]]:
    """Fuse multiple ranked lists of doc_ids into one ranked list."""
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# --------------------------------------------------------------
# Step 2: Load both retrievers
# --------------------------------------------------------------

bm25 = BM25Retriever()
dense = DenseRetriever()
corpus = load_corpus()


# --------------------------------------------------------------
# Step 3: Search both, fuse, compare
# --------------------------------------------------------------


def search_hybrid(
    query: str, k: int = 10, candidate_k: int = 50
) -> list[tuple[str, float]]:
    """Retrieve top candidate_k from each retriever, fuse, return top k."""
    bm25_ids = [doc_id for doc_id, _ in bm25.search(query, k=candidate_k)]
    dense_ids = [doc_id for doc_id, _ in dense.search(query, k=candidate_k)]
    return reciprocal_rank_fusion([bm25_ids, dense_ids])[:k]


def show(label: str, results: list[tuple[str, float]]) -> None:
    print(f"\n{label}")
    for i, (doc_id, score) in enumerate(results[:5], 1):
        text = corpus.loc[corpus["_id"] == doc_id, "text"].iloc[0]
        print(f"  {i}. [{score:.4f}] {doc_id}  {text[:70]}")


if __name__ == "__main__":
    query = "Where should I park my rainy-day fund?"
    print(f"Query: {query}")

    show("BM25 only", bm25.search(query, k=5))
    show("Dense only", dense.search(query, k=5))
    show("Hybrid (RRF)", search_hybrid(query, k=5))
