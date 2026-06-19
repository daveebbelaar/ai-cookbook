"""
The payoff. NDCG@10 across BM25, dense, hybrid (RRF), and hybrid + rerank,
on the FiQA-2018 test set.

Normalized Discounted Cumulative Gain at 10 (NDCG@10) is the standard retrieval metric.
It rewards putting relevant docs high in the top-10 and penalizes putting them low.
Perfect ranking = 1.0.

We evaluate on 50 randomly sampled test queries so all four methods stay
within Cohere's free tier (10 calls/minute, 1,000/month for trial keys).
Set RERANK_SAMPLE_SIZE = None to run all 648 queries (paid tier or patience).

Public BEIR baselines for FiQA NDCG@10:
    BM25                       ~24
    text-embedding-3-small     ~31
    + cross-encoder rerank     ~40+

The wide spread between BM25 and reranked hybrid is the point: BM25 alone struggles on
paraphrase-heavy questions, and every stage of the pipeline earns its keep.

More info: https://github.com/beir-cellar/beir/wiki/Leaderboard
"""

import math
from collections import defaultdict
import numpy as np
import pandas as pd
from tqdm import tqdm
from utils.retrievers import DATA_DIR, BM25Retriever, DenseRetriever, load_corpus
from utils.fusion import hybrid_candidates
from utils.reranker import rerank_with_cohere

RERANK_SAMPLE_SIZE = 50
SEED = 42


# --------------------------------------------------------------
# Step 1: NDCG@k in pure numpy
# --------------------------------------------------------------


def ndcg_at_k(predicted_ids: list[str], relevant: dict[str, int], k: int = 10) -> float:
    """Normalized discounted cumulative gain for a single query."""
    dcg = sum(
        relevant.get(doc_id, 0) / math.log2(rank + 2)
        for rank, doc_id in enumerate(predicted_ids[:k])
    )
    ideal_rels = sorted(relevant.values(), reverse=True)[:k]
    idcg = sum(rel / math.log2(rank + 2) for rank, rel in enumerate(ideal_rels))
    return dcg / idcg if idcg > 0 else 0.0


# --------------------------------------------------------------
# Step 2: Load queries + ground truth, pick the sample
# --------------------------------------------------------------

queries = pd.read_parquet(DATA_DIR / "queries.parquet")
qrels_df = pd.read_parquet(DATA_DIR / "qrels.parquet")

qrels: dict[str, dict[str, int]] = defaultdict(dict)
for _, row in qrels_df.iterrows():
    qrels[str(row["query-id"])][str(row["corpus-id"])] = int(row["score"])

queries_with_qrels = queries[queries["_id"].astype(str).isin(qrels.keys())].copy()
sample = queries_with_qrels.sample(n=RERANK_SAMPLE_SIZE, random_state=SEED)
print(f"Evaluating on {len(sample)} queries (sampled from {len(queries_with_qrels)})")


# --------------------------------------------------------------
# Step 3: Wire up the retrieval methods
# --------------------------------------------------------------

bm25 = BM25Retriever()
dense = DenseRetriever()
corpus_by_id = load_corpus().set_index("_id")


def hybrid_topk(query: str, candidate_k: int = 50) -> list[str]:
    return [
        d for d, _ in hybrid_candidates(query, bm25, dense, candidate_k=candidate_k)
    ]


def reranked_topk(query: str, candidate_k: int = 50, k: int = 10) -> list[str]:
    candidates = hybrid_topk(query, candidate_k=candidate_k)
    return [d for d, _ in rerank_with_cohere(query, candidates, corpus_by_id, k=k)]


# --------------------------------------------------------------
# Step 4: Score every method on the sample
# --------------------------------------------------------------

results: dict[str, list[float]] = defaultdict(list)
for _, row in tqdm(sample.iterrows(), total=len(sample), desc="Evaluating"):
    query_id = str(row["_id"])
    query_text = row["text"]
    relevant = qrels[query_id]

    results["BM25"].append(
        ndcg_at_k([d for d, _ in bm25.search(query_text, k=10)], relevant)
    )
    results["Dense"].append(
        ndcg_at_k([d for d, _ in dense.search(query_text, k=10)], relevant)
    )
    results["Hybrid (RRF)"].append(ndcg_at_k(hybrid_topk(query_text)[:10], relevant))
    results["Hybrid + Rerank"].append(ndcg_at_k(reranked_topk(query_text), relevant))


# --------------------------------------------------------------
# Step 5: Print the table
# --------------------------------------------------------------

if __name__ == "__main__":
    print(f"\nNDCG@10 x100 on FiQA ({len(sample)} sampled test queries)")
    print("-" * 42)
    for method, scores in results.items():
        print(f"  {method:<22} {np.mean(scores) * 100:.2f}")
