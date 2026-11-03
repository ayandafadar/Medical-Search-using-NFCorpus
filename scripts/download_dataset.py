import json
from pathlib import Path
from datasets import load_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "nfcorpus"
QRELS_DIR = DATA_DIR / "qrels"

DATA_DIR.mkdir(parents=True, exist_ok=True)
QRELS_DIR.mkdir(parents=True, exist_ok=True)

print("Downloading NFCorpus dataset from Hugging Face Hub...")
corpus = load_dataset("BeIR/nfcorpus", "corpus", split="corpus")
queries = load_dataset("BeIR/nfcorpus", "queries", split="queries")

print("Structuring local files...")

corpus_path = DATA_DIR / "corpus.jsonl"
with open(corpus_path, "w", encoding="utf-8") as f:
    for item in corpus:
        f.write(json.dumps({"_id": item["_id"], "title": item["title"], "text": item["text"]}) + "\n")
print(f"Saved: {corpus_path}")

queries_path = DATA_DIR / "queries.jsonl"
with open(queries_path, "w", encoding="utf-8") as f:
    for item in queries:
        f.write(json.dumps({"_id": item["_id"], "text": item["text"]}) + "\n")
print(f"Saved: {queries_path}")

split_mapping = {
    "train": "train",
    "dev": "validation",
    "test": "test",
}

for output_name, hf_split in split_mapping.items():
    print(f"\nLoading {output_name} qrels...")
    qrels = load_dataset("BeIR/nfcorpus-qrels", "default", split=hf_split)
    qrels_path = QRELS_DIR / f"{output_name}.tsv"

    with open(qrels_path, "w", encoding="utf-8") as f:
        f.write("query-id\tcorpus-id\tscore\n")
        for item in qrels:
            f.write(f"{item['query-id']}\t{item['corpus-id']}\t{item['score']}\n")

    print(f"Saved {len(qrels)} relevance judgments to {qrels_path}")
