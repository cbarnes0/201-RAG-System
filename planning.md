# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Student Reviews of CS Professors at Kennesaw State University. It isn't very likely for an official school source to have their professors rated. I chose this domain because I use it quite freqently when deciding my classes and find it very useful.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professor | Selena He | https://www.ratemyprofessors.com/professor/2236628#ratingsList |
| 2 | Rate My Professor | Victor Clincy | https://www.ratemyprofessors.com/professor/272248 |
| 3 | Rate My Professor | Umama Tasnim | https://www.ratemyprofessors.com/professor/2936300 |
| 4 | Rate My Professor | Dmitri Nunes | https://www.ratemyprofessors.com/professor/2908234 |
| 5 | Rate My Professor | Hisham Haddad | https://www.ratemyprofessors.com/professor/272340 |
| 6 | Rate My Professor |  Enda Sullivan | https://www.ratemyprofessors.com/professor/2185776 |
| 7 | Rate My Professor | Tu Nguyen | https://www.ratemyprofessors.com/professor/2721496 |
| 8 | Rate My Professor | Obioku Obotette | https://www.ratemyprofessors.com/professor/2935457 |
| 9 | Rate My Professor | Ermias Mamo | https://www.ratemyprofessors.com/professor/2286818 |
| 10 | Rate My Professor | Ruvini Jayamaha | https://www.ratemyprofessors.com/professor/3037659 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

The starting chunk size will be 350 characters as a starting point. I chose this to start because Rate My Professor has a 350 character limit for comments. This should allow any given comment to be completely captured in context. 

**Overlap:**

I believe, given that we will be able to capture the complete size of every review, there will be no need for overlap. This may change later in the project. 

**Reasoning:**

Because we are using context from a character limited review website, it made the most sense for starting out to capture the full length of each review. It's not a terribly large chunk size, either. A nice middle ground as a starting point.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

I'm planning on using all-MiniLM-L6-v2 via sentence-transformers. It is easy and straight forward, good for the level of this project.

**Top-k:**

I plan on using top-k@3. I believe this is a large enough size to capture relevent reviews to the query without being too diluted or strict.

**Production tradeoff reflection:**

If this was production, there would be significantly more data points. It may be more useful to use hybrid search in that instance because of the use of proper nouns (names of professors) to speed up the retrival of certain results.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Obioku Obotette's class? | Students strongly warn against taking him. He's described as a tough grader with a test-heavy, homework-heavy load, and he assigns an automatic 50 if he suspects AI use. Lowest-rated in the set at 1.3/5, ~8% would take again. |
| 2 | What do students like about Dmitri Nunes as a professor? | Clear lectures, answers all questions, values student feedback, very understanding, accessible outside class, tests that are easy if you prepare, and strong use of examples plus real-world references. Rated ~5.0/5, ~100% would take again. |
| 3 | Which professor has the lowest "would take again" percentage? | Obioku Obotette, at ~8% (below Selena He's ~10%). |
| 4 | What do students say about the homework load in Selena He's classes? | A very heavy homework load, with everything run through TurnItIn (including math-based work), and the course feeling like roughly two classes' worth of work. |
| 5 | Why do students rate Enda Sullivan so highly? | He's knowledgeable, gives great lectures, prepares the class well for exams, is caring, and his office hours are very useful when struggling. Rated ~4.9/5; some firmness on policy (no makeup quizzes) is offset by dropping the lowest grade. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
  Rate My Professor (.txt files)
  [scraped via Claude + web search]
              |
              v
+---------------------------+
|   1. Document Ingestion   |
|   Plain text files, one   |
|   per professor (x10)     |
+---------------------------+
              |
              v
+---------------------------+
|      2. Chunking          |
|  350-char chunks, no      |
|  overlap (one review =    |
|  one chunk)               |
+---------------------------+
              |
              v
+---------------------------+
|  3. Embedding +           |
|     Vector Store          |
|  all-MiniLM-L6-v2         |
|  (sentence-transformers)  |
+---------------------------+
              |
        User Query
              |
              v
+---------------------------+
|      4. Retrieval         |
|  Cosine similarity search |
|  top-k = 3 chunks         |
+---------------------------+
              |
              v
+---------------------------+
|      5. Generation        |
|  Retrieved chunks +       |
|  query → Groq API →       |
|  natural language answer  |
+---------------------------+
              |
              v
         User Answer
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

For ingestion of the information, I used a simple Claude chat window to help my scrape Rate My Professors information using web search. A text file was made for each professor. The information was then reviewed for accuracy by me.

For checking, I plan on using Claude code within VSC to assist in implementing the funcitonality to chunk these documents as laid out in my plan. It's anticipated for these to produce accurate and appropriate chunks, which will be manually verified before moving forward.

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
