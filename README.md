# The Unofficial Guide — Project 1

---

## Domain

Student reviews of KSU Computer Science professors from RateMyProfessors. This knowledge is valuable because official course descriptions describe what a class covers, not what it is actually like to take it. Ratings, teaching style, grading difficulty, and homework load are not available through any official KSU channel — students typically find this information through word-of-mouth or by searching RateMyProfessors on their own, with no way to query across multiple professors at once.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | RateMyProfessors — Selena He | Scraped .txt | documents/01_selena_he.txt |
| 2 | RateMyProfessors — Victor Clincy | Scraped .txt | documents/02_victor_clincy.txt |
| 3 | RateMyProfessors — Umama Tasnim | Scraped .txt | documents/03_umama_tasnim.txt |
| 4 | RateMyProfessors — Dmitri Nunes | Scraped .txt | documents/04_dmitri_nunes.txt |
| 5 | RateMyProfessors — Hisham Haddad | Scraped .txt | documents/05_hisham_haddad.txt |
| 6 | RateMyProfessors — Enda Sullivan | Scraped .txt | documents/06_enda_sullivan.txt |
| 7 | RateMyProfessors — Tu Nguyen | Scraped .txt | documents/07_tu_nguyen.txt |
| 8 | RateMyProfessors — Obioku Obotette | Scraped .txt | documents/08_obioku_obotette.txt |
| 9 | RateMyProfessors — Ermias Mamo | Scraped .txt | documents/09_ermias_mamo.txt |
| 10 | RateMyProfessors — Ruvini Jayamaha | Scraped .txt | documents/10_ruvini_jayamaha.txt |

---

## Chunking Strategy

**Chunk size:** 350 characters. RateMyProfessors enforces a 350-character limit per review, so a 350-character chunk is designed to capture one complete review without splitting it.

**Overlap:** None. Because each review is a self-contained opinion, there is no meaningful continuation across review boundaries. Overlap would only duplicate content without adding context.

**Why these choices fit your documents:** The documents are collections of short, independent review paragraphs rather than long continuous prose. Splitting on paragraph (blank-line) boundaries first, with a 350-character hard cap as a fallback, means most chunks correspond to exactly one student review. Preprocessing removed YAML frontmatter, markdown headings, bold/italic markers, and bare source URLs before chunking to prevent structural noise from ending up in the vector store.

**Final chunk count:** 59 chunks across 10 documents.

---

## Sample Chunks

Five representative chunks drawn from the final `chunks.json`, each self-contained and answerable on its own.

**Chunk 1** — `01_selena_he.txt` (index 0, 293 chars)
> Selena He is a Computer Science professor at Kennesaw State University (Kennesaw campus). Her RateMyProfessors profile is strongly negative overall (about 1.4 out of 5 across roughly 20 ratings, with around 10% of students saying they would take her again and a high difficulty rating of 4.3).

**Chunk 2** — `02_victor_clincy.txt` (index 4, 294 chars)
> Review 2 (about Victor Clincy): A student's main complaint about Victor Clincy is that his presentations combine a lot of material and assume students can connect it, while the textbook offers only a few worked examples; they felt students get blamed for low grades, which produces high curves.

**Chunk 3** — `04_dmitri_nunes.txt` (index 4, 231 chars)
> Review 1 (about Dmitri Nunes): A student calls Dmitri Nunes the best professor to have for the course: he answers all questions, gives clear lectures, values student feedback, is very understanding, and earns a 100% recommendation.

**Chunk 4** — `06_enda_sullivan.txt` (index 2, 281 chars)
> Professor: Enda Sullivan (Faculty, Computer Science & Engineering (CSE), Kennesaw State University, Marietta campus). Overall quality: very high (~4.9 / 5) based on multiple ratings. Would take again: high. Level of difficulty: moderate. Courses noted: CSE1321L; CSE1322L; CSE1322.

**Chunk 5** — `08_obioku_obotette.txt` (index 2, 348 chars)
> Professor: Obioku Obotette (Limited Term Instructor, Computer Science / Software Engineering, Kennesaw State University, Kennesaw campus). Overall quality: 1.3 / 5 based on ~13 ratings. Would take again: ~8%. Level of difficulty: 3.9 / 5. Courses noted: 3153. Recurring themes in reviews: tough grader; test heavy; lots of homework; group projects.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. It runs fully locally with no API key and produces 384-dimensional vectors. It is fast, well-documented, and performs well on short English text — a good match for 350-character review chunks.

**Production tradeoff reflection:** For a production system with significantly more professors or review text, a larger model like `all-mpnet-base-v2` would produce more accurate embeddings at the cost of higher latency and memory. Multilingual support would not be a concern for this corpus since all reviews are in English. Hybrid search (combining dense embeddings with BM25 keyword matching) would be worth adding because professor names are proper nouns that do not always embed reliably — a student typing "Clincy" exactly should match Victor Clincy's reviews even if the cosine distance is marginal. API-hosted models like OpenAI's `text-embedding-3-small` would offer higher accuracy but introduce cost and a network dependency.

---

## Retrieval Test Results

**Query 1:** "What do students say about the worst rated professor?"

| Rank | Distance | Professor | Chunk preview |
|------|----------|-----------|---------------|
| 1 | 0.3632 | Selena He | Review 3 (about Selena He): A student describes Selena He as the worst professor they had had, citing unclear grading guidelines and a sense that she did not care to teach. |
| 2 | 0.4814 | Tu Nguyen | He has few RateMyProfessors ratings, but reviews praise his technical depth. Exams are take-home but somewhat difficult. |
| 3 | 0.4929 | Dmitri Nunes | Review 1 (about Dmitri Nunes): A student calls Dmitri Nunes the best professor to have for the course... |
| 4 | 0.5073 | Enda Sullivan | Review 3 (about Enda Sullivan): A student calls Enda Sullivan a great lecturer whose office hours are very useful... |
| 5 | 0.5261 | Hisham Haddad | Reviews describe a strict grader whose material is delivered mainly in lecture, with strict assignment rules. |

*Why results 1 is relevant:* Result 1 (Selena He, distance 0.36) is a strong match — it's a review that literally describes her as "the worst professor." The distance of 0.36 reflects high semantic similarity. Results 2–5 are weaker matches that share general professor-review language but don't contain the specific "worst" framing; they appear because the query's embedding partially overlaps with any review text.

---

**Query 2:** "What do students say about the homework load in Selena He's classes?"

| Rank | Distance | Professor | Chunk preview |
|------|----------|-----------|---------------|
| 1 | 0.2241 | Selena He | Review 1 (about Selena He): A student reports that Selena He assigns a very heavy homework load and runs everything through TurnItIn, including math-based work... |
| 2 | 0.4061 | Selena He | Students most often cite a heavy homework load, the use of TurnItIn on all submissions, subjective grading on group projects, and rigidly timed tests and quizzes. |
| 3 | 0.4170 | Selena He | Review 3 (about Selena He): A student describes Selena He as the worst professor they had had, citing unclear grading guidelines... |
| 4 | 0.4296 | Selena He | Review 2 (about Selena He): A student calls it one of the worst classes at KSU under Selena He: grading guidelines are unclear... |
| 5 | 0.5401 | Selena He | Recurring themes in reviews: heavy homework load; TurnItIn used on all work; subjective grading; timed tests and quizzes. |

*Why results are relevant:* All 5 results are Selena He chunks with distances between 0.22 and 0.54. Naming both the professor and the topic ("homework load") in the query anchors retrieval tightly to her documents. The top result at 0.22 is a very strong match — it contains the exact phrase "very heavy homework load" as well as the TurnItIn detail. Per-professor deduplication is not active here because the query is professor-specific, so multiple Selena He chunks correctly fill the context window.

---

**Query 3:** "Why do students rate Enda Sullivan so highly?"

| Rank | Distance | Professor | Chunk preview |
|------|----------|-----------|---------------|
| 1 | 0.3189 | Enda Sullivan | Review 1: A student describes Enda Sullivan as a very good, knowledgeable programming teacher; prepared the class well, would highly recommend. |
| 2 | 0.3558 | Enda Sullivan | Review 3: A student calls Enda Sullivan a great lecturer whose office hours are very useful when struggling, and caring. |
| 3 | 0.3661 | Enda Sullivan | Review 2: A student praised Enda Sullivan's amazing lectures and willingness to answer questions. |
| 4 | 0.4014 | Enda Sullivan | Enda Sullivan is a CSE instructor at KSU who teaches intro programming. His RateMyProfessors profile is very positive (around 4.9/5). |
| 5 | 0.4642 | Enda Sullivan | Professor: Enda Sullivan — Overall quality: very high (~4.9/5). Would take again: high. Level of difficulty: moderate. |

---

## Grounded Generation

**System prompt grounding instruction:** The model is given a strict system prompt with five rules using hard verbs — "Answer ONLY", "Do NOT", "Do not speculate". Softer language like "prefer to use the context" leaves room for the model to fill gaps with training knowledge. A specific fallback phrase is quoted in the prompt ("I don't have enough information in the provided reviews to answer that.") so the model has an exact string to pattern-match when the context is insufficient. Temperature is set to 0.0 for fully deterministic output.

**How source attribution is surfaced in the response:** Source attribution is appended programmatically in Python after generation — it is never left to the model to include. The retrieved chunks list is iterated and each unique professor name and filename is added to a formatted sources block regardless of what the model wrote. The model is also instructed via rule 6 to use an inline citation format (`"according to student reviews of [Professor] (source: [filename])"`) so attribution appears in the body of the answer as well.

---

## Example Responses

**Response 1 — Grounded, specific professor query**

*Query:* What do students say about Obioku Obotette's class?

*Answer:* According to student reviews of Obioku Obotette (source: 08_obioku_obotette.txt), his class has a strongly negative RateMyProfessors profile with a rating of about 1.3 out of 5 across roughly 13 ratings, with around 8% would-take-again and difficulty 3.9.

*Retrieved from:*
- **Obioku Obotette** (`08_obioku_obotette.txt`, distance: 0.286)

---

**Response 2 — Grounded, positive professor query**

*Query:* What do students like about Dmitri Nunes as a professor?

*Answer:* According to student reviews of Dmitri Nunes (source: 04_dmitri_nunes.txt), students like that he is a nice professor, makes everything accessible outside of class, uses strong examples and real-world references to explain topics, and that his tests and quizzes are easy if you prepare.

*Retrieved from:*
- **Dmitri Nunes** (`04_dmitri_nunes.txt`, distance: 0.1666)

---

**Response 3 — Out-of-scope refusal**

*Query:* What is the best place to eat near the KSU campus?

*Answer:* I don't have enough information in the provided reviews to answer that.

*Retrieved from:*
- **Selena He** (`01_selena_he.txt`, distance: 0.7348)
- **Tu Nguyen** (`07_tu_nguyen.txt`, distance: 0.7610)

The high distance scores (0.73–0.76) confirm that no relevant chunks were found. The model correctly returned the fallback phrase rather than drawing on general knowledge.

---

## Query Interface

The interface is a Gradio web app launched by running `python app.py`. It opens at `http://127.0.0.1:7860` in a browser.

**Input:** A multi-line text box labeled "Your question" with a placeholder example. Pressing Enter or clicking Ask submits the query.

**Output — Answer:** A read-only text area showing the LLM's grounded response with inline citations in the format *"according to student reviews of [Professor] (source: [filename])"*.

**Output — Sources:** A Markdown panel below the answer listing the retrieved source files and their cosine distances.

**Sample interaction transcript:**

```
User:    Why do students rate Enda Sullivan so highly?

Answer:  According to student reviews of Enda Sullivan
         (source: 06_enda_sullivan.txt), students rate him
         highly because he is a very good and knowledgeable
         programming teacher who prepared the class well
         for exams and quizzes.

Sources: Retrieved from:
         - Enda Sullivan (06_enda_sullivan.txt, distance: 0.3189)
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Obioku Obotette's class? | Tough grader, test-heavy, homework-heavy, automatic 50 for AI use, 1.3/5, ~8% would take again | Correctly identified strongly negative profile (1.3/5, 8% would take again, difficulty 3.9), but did not surface the AI policy or the specific student warnings | Relevant | Partially accurate |
| 2 | What do students like about Dmitri Nunes as a professor? | Clear lectures, answers all questions, values feedback, very understanding, accessible, easy tests, strong examples | Captured accessible outside class, strong examples, easy tests if prepared — missed clear lectures, answers questions, values feedback explicitly | Relevant | Partially accurate |
| 3 | Which professor has the lowest "would take again" percentage? | Obioku Obotette at ~8% (below Selena He's ~10%) | Incorrectly named Selena He at ~10% — Obioku Obotette's profile chunk ranked 13th in similarity and was not retrieved with k=5 | Partially relevant | Inaccurate |
| 4 | What do students say about the homework load in Selena He's classes? | Very heavy homework load, TurnItIn on everything including math, feels like two classes' worth of work | Confirmed "very heavy homework load" but gave no detail on TurnItIn, math submissions, or workload scale | Relevant | Partially accurate |
| 5 | Why do students rate Enda Sullivan so highly? | Knowledgeable, great lectures, prepares class well, caring, useful office hours, 4.9/5, no-makeup-quiz policy offset by dropping lowest grade | Correctly identified knowledgeable and prepared the class well — missed caring, office hours, and the policy detail | Relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** The system answered 4 of 5 questions from the correct source documents. The most common issue was thinness — the responses were directionally correct but less specific than the expected answers because only one chunk per professor reached the context window, leaving review-level details out. The one outright failure (Q3) was a retrieval failure caused by k=5 not reaching Obioku Obotette's profile chunk, which ranked 13th in cosine similarity for that query.

---

## Failure Case Analysis

**Question that failed:** Which professor has the lowest "would take again" percentage?

**What the system returned:** "According to student reviews of Selena He (source: 01_selena_he.txt), she has the lowest 'would take again' percentage at ~10%." — This is wrong. Obioku Obotette has ~8%, which is lower.

**Root cause (tied to a specific pipeline stage):** The failure is in the retrieval stage. The query "which professor has the lowest would take again percentage" produces a semantic embedding that matches the phrase "would take again" most strongly in Selena He's profile chunk, which ranks 1st. Obioku Obotette's profile chunk — which also contains "Would take again: ~8%" — ranks 13th in cosine similarity because its surrounding text (tough grader, test heavy, group projects) is semantically less aligned with the query phrasing. With k=5 and per-professor deduplication, only 4–5 unique professors reach the context window, so the model never sees Obioku Obotette's percentage and cannot make the correct comparison.

**What you would change to fix it:** Raising k to 15 and keeping per-professor deduplication brings all 10 professor profiles into context for comparison queries, which produced the correct answer during development. The tradeoff is a larger context window for every query, including specific single-professor questions that don't need it. A cleaner long-term fix would be a hybrid approach: detect comparison-style queries (keywords like "lowest", "highest", "most", "least") and increase k dynamically, while keeping k=5 for single-professor lookup questions.

---

## Spec Reflection

**One way the spec helped you during implementation:** Specifying 350 characters as the chunk size before writing any code made the chunking decision straightforward — it gave a concrete number to implement and a clear reason to check (RateMyProfessors' own character limit). Without that, a generic default like 500 or 1000 tokens would have been used, which would have merged multiple reviews into a single chunk and reduced retrieval precision.

**One way your implementation diverged from the spec, and why:** The spec planned top-k=3 for retrieval. During testing, k=3 was not enough for comparison questions spanning all 10 professors — the relevant chunk for one professor ranked 13th and was never retrieved. k was increased and per-professor deduplication was added so that comparison queries can surface information from every professor in the corpus. The spec was a correct starting point for single-professor queries but underestimated the retrieval depth needed for cross-professor comparisons. Finally, k was set @ 5 for a good balance, though some answers detracted as noted above.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Documents section and Chunking Strategy section from planning.md, along with the pipeline diagram from the Architecture section.
- *What it produced:* `ingest.py` — a script that loads `.txt` files from the documents directory, strips YAML frontmatter, cleans HTML entities and markdown formatting, splits on paragraph boundaries with a 350-character fallback, and saves chunks to `chunks.json`.
- *What I changed or overrode:* The initial version hard-split paragraphs at exactly 350 characters, creating mid-word fragments. After inspecting the output, I directed the AI to fix the chunker to split at word boundaries and then at sentence boundaries, and to drop tail fragments shorter than 50 characters. I also identified and fixed a cleaning bug where bare source URL lines were escaping the regex because they had no leading newline.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md, the pipeline diagram, and the saved `chunks.json` output from the ingestion step.
- *What it produced:* `embed.py` and `app.py` — the embedding script that indexes chunks into ChromaDB using all-MiniLM-L6-v2, a retrieval function, a Groq generation call with a grounding system prompt, and a Gradio interface.
- *What I changed or overrode:* The initial system prompt used softer grounding language. After testing with an out-of-scope question that produced a vague but non-empty response, I directed the AI to tighten the rules to use hard verbs ("ONLY", "Do NOT") and add an exact fallback phrase. I also identified that source attribution was left to the LLM, and directed the AI to move it into Python so it is guaranteed regardless of model output.

## Demo Video

[Click here for demo video](https://drive.google.com/file/d/1S5yY1j3obpEKf_ifw8yDsmN7ib_kAFsN/view?usp=sharing)