import json
import re
import html
from pathlib import Path

DOCUMENTS_DIR = Path("documents")
CHUNK_SIZE = 350
CHUNKS_OUTPUT = Path("chunks.json")


def load_documents(docs_dir: Path) -> list[dict]:
    docs = []
    for path in sorted(docs_dir.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        docs.append({"source": path.name, "raw": raw})
    return docs


def strip_frontmatter(text: str) -> tuple[str, dict]:
    """Extract YAML-style --- frontmatter into a metadata dict, return the body."""
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return text, {}
    metadata = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            metadata[key.strip()] = val.strip()
    return text[match.end():], metadata


def clean_text(text: str) -> str:
    text = html.unescape(text)                                      # &amp; &#39; &nbsp; etc.
    text = re.sub(r"<[^>]+>", " ", text)                           # stray HTML tags
    text = re.sub(r"^#{1,6}\s.*$", "", text, flags=re.MULTILINE)   # markdown headings — no retrieval value
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)          # bold/italic markers
    text = re.sub(r"[ \t]+", " ", text)                            # collapse horizontal whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)                         # collapse 3+ blank lines to one
    return text.strip()


def _word_split(text: str, chunk_size: int) -> list[str]:
    """Split at word boundaries when a single sentence exceeds chunk_size."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        boundary = text.rfind(" ", start, end)
        end = boundary if boundary > start else end
        chunks.append(text[start:end].strip())
        start = end + 1
    return [c for c in chunks if c]


def _split_paragraph(para: str, chunk_size: int) -> list[str]:
    """Combine sentences greedily up to chunk_size; word-split only when unavoidable.
    Fragments shorter than MIN_FRAGMENT chars are dropped — they have no standalone meaning."""
    MIN_FRAGMENT = 50
    sentences = re.split(r"(?<=[.!?])\s+", para)
    result = []
    current = ""
    for sentence in sentences:
        if len(sentence) > chunk_size:
            if current:
                result.append(current)
                current = ""
            result.extend(_word_split(sentence, chunk_size))
        elif not current:
            current = sentence
        elif len(current) + 1 + len(sentence) <= chunk_size:
            current += " " + sentence
        else:
            result.append(current)
            current = sentence
    if current:
        result.append(current)
    return [c for c in result if len(c) >= MIN_FRAGMENT]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks = []
    for para in paragraphs:
        if len(para) <= chunk_size:
            chunks.append(para)
        else:
            chunks.extend(_split_paragraph(para, chunk_size))
    return chunks


def main():
    txt_files = list(DOCUMENTS_DIR.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {DOCUMENTS_DIR}/. Add your professor files and re-run.")
        return

    documents = load_documents(DOCUMENTS_DIR)
    print(f"Loaded {len(documents)} document(s).\n")

    all_chunks = []
    for doc in documents:
        body, metadata = strip_frontmatter(doc["raw"])
        cleaned = clean_text(body)
        chunks = chunk_text(cleaned)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "professor": metadata.get("professor_name", ""),
                "chunk_index": i,
                "text": chunk,
            })

    # Print the first document body after cleaning so you can spot leftover junk
    first_body, _ = strip_frontmatter(documents[0]["raw"])
    first_cleaned = clean_text(first_body)
    print("=== FIRST DOCUMENT AFTER CLEANING (first 800 chars) ===")
    print(first_cleaned[:800])
    print("...\n")

    # Print 5 evenly spaced chunks for inspection
    print("=== 5 SAMPLE CHUNKS ===")
    step = max(1, len(all_chunks) // 5)
    samples = [all_chunks[min(i * step, len(all_chunks) - 1)] for i in range(5)]
    for i, chunk in enumerate(samples, 1):
        print(f"--- Chunk {i} [{chunk['source']} | {chunk['professor']} | index {chunk['chunk_index']}] ---")
        print(chunk["text"])
        print(f"(length: {len(chunk['text'])} chars)\n")

    print(f"Total chunks: {len(all_chunks)}")
    if len(all_chunks) < 50:
        print("  WARNING: fewer than 50 chunks — chunks may be too large or files may be missing.")
    elif len(all_chunks) > 2000:
        print("  WARNING: more than 2000 chunks — chunks may be too small.")

    CHUNKS_OUTPUT.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved to {CHUNKS_OUTPUT}")


if __name__ == "__main__":
    main()
