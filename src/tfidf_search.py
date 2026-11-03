import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.services.retrieval_service import RetrievalService


def main():
    print("Initializing Medical Search Service...")
    service = RetrievalService(settings)
    service.initialize()

    print("\nTF-IDF search engine is ready!")

    while True:
        query = input("\nEnter a medical query (or type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break

        res = service.search(query=query, model_name="tfidf", top_k=10)
        results = res["results"]

        if not results:
            print("No matching documents found.")
            continue

        print(f"\nTop {len(results)} results:\n")
        for rank, result in enumerate(results, start=1):
            title = result["title"] or result["id"]
            print(f"{rank}. {title}")
            print(f"   Document ID: {result['id']}")
            print(f"   Similarity:  {result['score']:.4f}")
            preview = result["text"][:300].replace("\n", " ")
            print(f"   Preview: {preview}...")
            print("-" * 70)


if __name__ == "__main__":
    main()
