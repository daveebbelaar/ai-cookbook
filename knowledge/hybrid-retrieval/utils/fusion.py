"""
Polished version of the Reciprocal Rank Fusion logic built in 4-rrf.py. The
later files import from here so each one can focus on the new idea it
introduces (reranking, evaluation) instead of re-defining fusion.
"""

from collections import defaultdict
from utils.retrievers import BM25Retriever, DenseRetriever


def reciprocal_rank_fusion(
    rankings: list[list[str]], k: int = 60
) -> list[tuple[str, float]]:
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


def hybrid_candidates(
    query: str,
    bm25: BM25Retriever,
    dense: DenseRetriever,
    candidate_k: int = 50,
) -> list[tuple[str, float]]:
    bm25_ids = [doc_id for doc_id, _ in bm25.search(query, k=candidate_k)]
    dense_ids = [doc_id for doc_id, _ in dense.search(query, k=candidate_k)]
    return reciprocal_rank_fusion([bm25_ids, dense_ids])[:candidate_k]
