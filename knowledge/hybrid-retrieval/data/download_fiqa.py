"""
One-time fetch of the FiQA-2018 benchmark from the HuggingFace BeIR repos.

FiQA is a financial question answering benchmark: real finance questions
('Where should I park my rainy-day fund?') retrieved against forum posts and
opinion articles. 57,638 corpus docs, 648 test queries, ~2.6 relevant docs
per query. It is the closest stand-in BEIR has for a business knowledge base.

More info: https://sites.google.com/view/fiqa
"""

from pathlib import Path
from datasets import load_dataset

DATA_DIR = Path(__file__).parent / "fiqa"
DATA_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------------
# Step 1: Pull the three pieces of a BEIR dataset
# --------------------------------------------------------------

# Every BEIR benchmark ships in the same shape:
#   - corpus: the documents to search over
#   - queries: the user queries
#   - qrels: the ground-truth (query_id, doc_id, relevance) triples

corpus = load_dataset("BeIR/fiqa", "corpus", split="corpus")
queries = load_dataset("BeIR/fiqa", "queries", split="queries")
qrels = load_dataset("BeIR/fiqa-qrels", split="test")


# --------------------------------------------------------------
# Step 2: Cache as parquet so the other files load instantly
# --------------------------------------------------------------

corpus.to_parquet(DATA_DIR / "corpus.parquet")
queries.to_parquet(DATA_DIR / "queries.parquet")
qrels.to_parquet(DATA_DIR / "qrels.parquet")


if __name__ == "__main__":
    print(f"Corpus:  {len(corpus):>6} docs    -> {DATA_DIR / 'corpus.parquet'}")
    print(f"Queries: {len(queries):>6} queries -> {DATA_DIR / 'queries.parquet'}")
    print(f"Qrels:   {len(qrels):>6} judgments -> {DATA_DIR / 'qrels.parquet'}")
