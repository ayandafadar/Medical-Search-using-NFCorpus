import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "nfcorpus"

with open(DATA_DIR / "corpus.jsonl", encoding="utf-8") as f:
    first_document = json.loads(next(f))

print("FIRST DOCUMENT")
print(first_document)

with open(DATA_DIR / "queries.jsonl", encoding="utf-8") as f:
    first_query = json.loads(next(f))

print("\nFIRST QUERY")
print(first_query)

qrels_path = DATA_DIR / "qrels" / "test.tsv"

with open(qrels_path, encoding="utf-8") as f:
    for _ in range(4):
        line = f.readline()
        if not line:
            break
        print(line.rstrip())

print("\nFILE COUNTS")

for filename in ["corpus.jsonl", "queries.jsonl"]:
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        count = sum(1 for _ in f)
    print(f"{filename}: {count} records")
