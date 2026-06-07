import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb

CHUNKS_FILE = Path("chunks.json")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# Load the embedding model once at module level so both build and retrieve share it.
# The model runs locally — no API key, no network calls after the first download.
model = SentenceTransformer(EMBED_MODEL)


def build_index(chunks: list[dict]) -> chromadb.Collection:
    """Embed every chunk and store it in ChromaDB with source metadata."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Drop and recreate so re-runs don't accumulate duplicate entries.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine distance matches how sentence-transformers works
    )

    texts = [c["text"] for c in chunks]

    # model.encode() converts each text string into a dense vector of 384 floats.
    # Texts that mean similar things end up as vectors pointing in similar directions.
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    # ChromaDB requires a unique string ID per entry.
    ids = [f"{c['source']}::{c['chunk_index']}" for c in chunks]

    # Metadata travels alongside the embedding so retrieval results can tell you
    # which professor and file each chunk came from.
    metadatas = [
        {
            "source": c["source"],
            "professor": c["professor"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,   # ChromaDB stores the original text so you can read results
        metadatas=metadatas,
    )
    print(f"Indexed {len(texts)} chunks into '{COLLECTION_NAME}'.\n")
    return collection


def retrieve(collection: chromadb.Collection, query: str, k: int = TOP_K) -> list[dict]:
    """Return the k chunks whose embeddings are closest to the query embedding."""

    # Embed the query using the same model so it lives in the same vector space.
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    # results["documents"] is a list-of-lists because ChromaDB supports batch queries.
    # We sent one query, so we take index [0] from each.
    return [
        {
            "text": doc,
            "source": meta["source"],
            "professor": meta["professor"],
            "distance": round(dist, 4),
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def print_results(query: str, results: list[dict]) -> None:
    print(f"Query: {query}")
    print("-" * 70)
    for i, r in enumerate(results, 1):
        snippet = r["text"][:220] + ("..." if len(r["text"]) > 220 else "")
        print(f"  [{i}] distance={r['distance']}  [{r['professor']}]")
        print(f"       {snippet}")
    print()


def main():
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks.\n")

    collection = build_index(chunks)

    # Test with 3 evaluation-plan queries (from planning.md)
    test_queries = [
        "What do students say about the worst rated professor?",
        "What do students say about the homework load in Selena He's classes?",
        "Why do students rate Enda Sullivan so highly?",
    ]
    for query in test_queries:
        results = retrieve(collection, query)
        print_results(query, results)


if __name__ == "__main__":
    main()
