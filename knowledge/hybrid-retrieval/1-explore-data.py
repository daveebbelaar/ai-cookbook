"""
Explore the FiQA-2018 benchmark: what the corpus looks like, what queries
look like, and what 'relevance' actually means in retrieval.

FiQA is financial question answering. A query is a finance question
('Where should I park my rainy-day fund?'), a document is a forum post or
opinion article, and a qrel says 'this document answers that question'.

More info: https://github.com/beir-cellar/beir
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data" / "fiqa"


# --------------------------------------------------------------
# Step 1: Load and inspect the three parquet files
# --------------------------------------------------------------

corpus = pd.read_parquet(DATA_DIR / "corpus.parquet")
print(corpus["text"].iloc[0])

queries = pd.read_parquet(DATA_DIR / "queries.parquet")
print(queries["text"].iloc[0])

qrels = pd.read_parquet(DATA_DIR / "qrels.parquet")
print(qrels.iloc[0])

# --------------------------------------------------------------
# Step 2: Filter the queries to only include the test queries
# --------------------------------------------------------------

test_query_ids = set(qrels["query-id"].astype(str))
test_queries = queries[queries["_id"].astype(str).isin(test_query_ids)]
print(f"Queries (test, with qrels): {len(test_queries)}")

# --------------------------------------------------------------
# Step 3: Inspect one query and its relevant docs
# --------------------------------------------------------------

query = test_queries.iloc[0]
print("\nExample query")
print(f"  _id:  {query['_id']}")
print(f"  text: {query['text']}")

relevant = qrels[qrels["query-id"].astype(str) == str(query["_id"])]
print(f"\n  Relevant docs for this question: {list(relevant['corpus-id'])}")
