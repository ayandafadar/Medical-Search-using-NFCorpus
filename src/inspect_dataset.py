
import json
from pathlib import Path

DATA_DIR = Path("data/nfcorpus")

# Inspect corpus
with open(DATA_DIR / "corpus.jsonl", encoding="utf-8") as f:
    first_document = json.loads(next(f))

print("FIRST DOCUMENT")
print(first_document)

# Inspect queries
with open(DATA_DIR / "queries.jsonl", encoding="utf-8") as f:
    first_query = json.loads(next(f))

print("\nFIRST QUERY")
print(first_query)

# Inspect qrels
qrels_path = DATA_DIR / "qrels" / "test.tsv"

with open(qrels_path, encoding="utf-8") as f:
    for _ in range(4):
        line = f.readline()
        if not line:
            break
        print(line.rstrip())

# Count documents and queries
print("\nFILE COUNTS")

for filename in ["corpus.jsonl", "queries.jsonl"]:
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        count = sum(1 for _ in f)
    print(f"{filename}: {count} records")
