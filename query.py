import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"
EMBED_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 3  # matches planning.md

model = SentenceTransformer(EMBED_MODEL)


def get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)


def retrieve(collection: chromadb.Collection, query: str, k: int = TOP_K) -> list[dict]:
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "text": doc,
            "professor": meta["professor"],
            "source": meta["source"],
            "distance": round(dist, 4),
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def generate(query: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[Source: {c['professor']}]\n{c['text']}" for c in chunks
    )
    prompt = (
        "You are a helpful assistant answering questions about KSU Computer Science "
        "professors based on student reviews from RateMyProfessors.\n"
        "Answer using only the provided context. "
        "If the context does not contain enough information to answer fully, say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return response.choices[0].message.content


def ask(collection: chromadb.Collection, query: str) -> None:
    print(f"Question: {query}")
    print("=" * 70)

    chunks = retrieve(collection, query)
    print("Retrieved chunks:")
    for i, c in enumerate(chunks, 1):
        print(f"  [{i}] distance={c['distance']}  [{c['professor']}]")
        print(f"       {c['text'][:180]}{'...' if len(c['text']) > 180 else ''}")
    print()

    answer = generate(query, chunks)
    print("Answer:")
    print(answer)
    print()


def main():
    collection = get_collection()

    # 3 questions from the evaluation plan in planning.md
    questions = [
        "What do students say about Obioku Obotette's class?",
        "What do students like about Dmitri Nunes as a professor?",
        "Which professor has the lowest 'would take again' percentage?",
    ]

    for q in questions:
        ask(collection, q)
        print("-" * 70)
        print()


if __name__ == "__main__":
    main()
