import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
import gradio as gr

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"
EMBED_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 5

# This is the grounding instruction. "Only" and "Do not" are load-bearing words —
# softer phrasing like "prefer to use" leaves the model room to fill gaps with
# training knowledge, which defeats the purpose of RAG.
SYSTEM_PROMPT = """\
You are a question-answering assistant for student reviews of KSU Computer Science professors.

Rules you must follow:
1. Answer ONLY using information explicitly stated in the provided context documents.
2. Do NOT draw on outside knowledge or general facts from your training data.
3. If the context does not contain enough information to answer the question, \
respond with exactly: "I don't have enough information in the provided reviews to answer that."
4. Do not speculate or infer beyond what the context directly states.
5. Do not mention professors who do not appear in the context.
6. When citing information, use this format inline: \
"according to student reviews of [Professor Name] (source: [filename])"."""

# Load once at startup so every query reuses the same objects.
model = SentenceTransformer(EMBED_MODEL)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """Embed the query, fetch k nearest chunks, then deduplicate to one chunk per
    professor (keeping the closest match). This prevents one professor from
    monopolising context slots on broad comparison queries."""
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    all_chunks = [
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
    # Keep only the best-ranked chunk per professor (results are already distance-sorted).
    seen: set[str] = set()
    deduped = []
    for chunk in all_chunks:
        if chunk["professor"] not in seen:
            seen.add(chunk["professor"])
            deduped.append(chunk)
    return deduped


def generate(query: str, chunks: list[dict]) -> str:
    """Send the retrieved chunks + query to the LLM and return its answer."""
    context = "\n\n".join(
        f"[Source: {c['source']} — {c['professor']}]\n{c['text']}"
        for c in chunks
    )
    user_message = (
        f"Context documents:\n\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer using only the context documents above."
    )
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,  # zero temperature = fully deterministic, minimises hallucination
    )
    return response.choices[0].message.content


def answer_question(query: str) -> tuple[str, str]:
    """Full RAG pipeline: retrieve → generate → attach sources."""
    if not query.strip():
        return "", ""

    chunks = retrieve(query)
    llm_answer = generate(query, chunks)

    # Source attribution is built here in Python, not requested from the LLM.
    # This guarantees sources always appear even if the model forgets to cite them.
    sources = []
    seen_sources = set()
    for c in chunks:
        key = c["source"]
        if key not in seen_sources:
            seen_sources.add(key)
            sources.append(f"- **{c['professor']}** (`{c['source']}`, distance: {c['distance']})")
    sources_text = "**Retrieved from:**\n" + "\n".join(sources)

    return llm_answer, sources_text


# ── Gradio interface ──────────────────────────────────────────────────────────

with gr.Blocks(title="KSU CS Professor Reviews") as app:
    gr.Markdown("## KSU CS Professor Review Assistant")
    gr.Markdown(
        "Ask questions about KSU Computer Science professors. "
        "Answers are grounded in student reviews from RateMyProfessors."
    )

    query_box = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about homework in Selena He's class?",
        lines=2,
    )
    submit_btn = gr.Button("Ask", variant="primary")
    answer_box = gr.Textbox(label="Answer", lines=10, interactive=False)
    sources_box = gr.Markdown(label="Sources")

    submit_btn.click(fn=answer_question, inputs=query_box, outputs=[answer_box, sources_box])
    query_box.submit(fn=answer_question, inputs=query_box, outputs=[answer_box, sources_box])


if __name__ == "__main__":
    app.launch()
