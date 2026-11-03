import json
from pathlib import Path
from datasets import load_dataset

# Set up the data directory structure exactly as the old ZIP file did
DATA_DIR = Path("data/nfcorpus")
DATA_DIR.mkdir(parents=True, exist_ok=True)
QRELS_DIR = DATA_DIR / "qrels"
QRELS_DIR.mkdir(exist_ok=True)

print("Downloading NFCorpus dataset from Hugging Face Hub...")
print("(This may take a moment depending on your internet connection)")

# Download the corpus and queries
corpus = load_dataset("BeIR/nfcorpus", "corpus", split="corpus")
queries = load_dataset("BeIR/nfcorpus", "queries", split="queries")

print("Structuring local files...")

# 1. Write corpus.jsonl
corpus_path = DATA_DIR / "corpus.jsonl"
with open(corpus_path, "w", encoding="utf-8") as f:
    for item in corpus:
        f.write(json.dumps({"_id": item["_id"], "title": item["title"], "text": item["text"]}) + "\n")
print(f"Saved: {corpus_path}")

# 2. Write queries.jsonl
queries_path = DATA_DIR / "queries.jsonl"
with open(queries_path, "w", encoding="utf-8") as f:
    for item in queries:
        f.write(json.dumps({"_id": item["_id"], "text": item["text"]}) + "\n")
print(f"Saved: {queries_path}")

# 3. Write qrels (Relevance judgments for train, dev, and test splits)


# 3. Download qrels (relevance judgments)
print("\nDownloading relevance judgments...")

split_mapping = {
    "train": "train",
    "dev": "validation",
    "test": "test",
}

for output_name, hf_split in split_mapping.items():
    print(f"\nLoading {output_name} qrels...")

    qrels = load_dataset(
        "BeIR/nfcorpus-qrels",
        "default",
        split=hf_split
    )

    qrels_path = QRELS_DIR / f"{output_name}.tsv"

    with open(qrels_path, "w", encoding="utf-8") as f:
        f.write("query-id\tcorpus-id\tscore\n")

        for item in qrels:
            f.write(
                f"{item['query-id']}\t"
                f"{item['corpus-id']}\t"
                f"{item['score']}\n"
            )

    print(
        f"Saved {len(qrels)} relevance judgments "
        f"to {qrels_path}"
    )


# Print out the created file tree matching your original script's behavior
for path in DATA_DIR.rglob("*"):
    if path.is_file():
        print(path)