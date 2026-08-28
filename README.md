# 🌾 KrishiMitra AI

**Multilingual (Tamil / Hindi / English) Agricultural Query Assistant**

A farmer types or speaks a crop question in Tamil, Hindi, or English.
The system detects the language, translates to English, retrieves
relevant vetted agricultural knowledge with RAG, generates a grounded
answer with an LLM, applies safety rules (no invented pesticide names
or dosages, expert-escalation for high-risk/low-confidence cases), and
translates the answer back into the farmer's language.

Built entirely on **free** tools — no paid API/billing setup required
to get started:

| Layer              | Tool                                                            |
| ------------------ | --------------------------------------------------------------- |
| Vector DB / RAG    | ChromaDB (local, free, built-in embeddings)                     |
| Language detection | `langdetect` (offline, free)                                    |
| Translation        | `deep-translator` (free, no API key)                            |
| LLM                | **Groq** (free tier, Llama 3.3 70B) _or_ **Gemini** (free tier) |
| UI                 | Streamlit                                                       |

> This replaces the original draft's Anthropic Claude + Google Cloud
> Translate stack, both of which require a paid/billing-enabled
> account even on their "free tier." Everything here works with a
> free-tier API key (Groq/Gemini) or no key at all (translation,
> detection, vector DB).

---

## 1. Project structure

```text
krishimitra/
│
├── app.py            # Streamlit UI — the main entry point
├── farming_kb.py      # Builds/loads the ChromaDB knowledge base
├── translator.py       # Free language detection + translation
├── retriever.py         # RAG retrieval (query ChromaDB, build context)
├── llm.py                # Calls Groq or Gemini (free), grounded on context
├── safety.py               # Guardrails: high-risk keywords, confidence, escalation
│
├── data/
│   └── farming_knowledge.txt   # (placeholder — knowledge currently lives in farming_kb.py)
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 2. Setup

### Step 1 — Install Python dependencies

```bash
cd krishimitra
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Get a free LLM API key

Pick **one**:

- **Groq (recommended — fast, generous free tier)**
  1. Go to https://console.groq.com/keys
  2. Sign up (free) and create an API key.

- **Gemini**
  1. Go to https://aistudio.google.com/apikey
  2. Sign up (free) and create an API key.

No credit card is required for either provider's free tier.

### Step 3 — Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
LLM_PROVIDER=groq          # or "gemini"
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here   # only if using gemini
```

### Step 4 — Build the knowledge base

```bash
python farming_kb.py
```

Expected output:

```text
Knowledge base ready: 8 documents
```

### Step 5 — Run the app

```bash
streamlit run app.py
```

Your browser will open the KrishiMitra interface.

---

## 3. How it works (pipeline)

```text
                 🌾 FARMER
                     │
                     ▼
              Streamlit UI
                     │
                     ▼
       Language Detection (langdetect)
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Tamil       Hindi     English
          │          │          │
          └──────────┼──────────┘
                     ▼
        deep-translator (free)
                     │
                     ▼
               English Query
                     │
                     ▼
                 ChromaDB
                     │
                     ▼
             Top 3 Documents
                     │
                     ▼
                Safety Check
                     │
                     ▼
              Groq / Gemini LLM
                     │
                     ▼
              English Answer
                     │
                     ▼
        deep-translator (free)
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        தமிழ்       हिंदी     English
                     │
                     ▼
                 👨‍🌾 FARMER
```

---

## 4. Test it

**Tamil:**

```text
என் நெல் இலைகள் மஞ்சளாக மாறுகிறது. என்ன செய்ய வேண்டும்?
```

**Hindi:**

```text
मेरे धान के पत्ते पीले हो रहे हैं। मुझे क्या करना चाहिए?
```

**English:**

```text
Why are my rice leaves turning yellow?
```

**Safety system (should trigger expert escalation, not invent a chemical):**

```text
Which pesticide should I use and what dosage should I spray?
```

---

## 5. Switching LLM providers

Just change one line in `.env`:

```env
LLM_PROVIDER=groq
```

or

```env
LLM_PROVIDER=gemini
```

Both are wired up in `llm.py` (`_ask_groq` / `_ask_gemini`) behind a
single `ask_llm()` function — the rest of the app doesn't need to know
which provider is active.

---

## 6. Important notes before any real submission

- **The agricultural content in `farming_kb.py` is starter/demo data
  only.** Replace it with verified content (e.g. ICAR, state
  agriculture department advisories, KVK material) before any public
  or hackathon submission where accuracy matters.
- The safety layer is a simple MVP (keyword match + document-count
  confidence). For production use, replace `assess_confidence()` in
  `safety.py` with a real retrieval-score-based metric, and expand
  `HIGH_RISK_KEYWORDS` with a more complete multilingual list.
- `deep-translator`'s Google backend is a free, unofficial wrapper —
  fine for a demo/hackathon, but it can rate-limit under heavy use.
  For production-scale traffic, consider a paid translation API.

---

## 7. Next steps (Day 2+)

- Expand the knowledge base with real, verified crop data.
- Add voice input/output (speech-to-text / text-to-speech) for
  low-literacy users.
- Add an IVR (phone call) layer for farmers without smartphones.
- Replace the MVP confidence score with a real retrieval-score metric.
- Add weather API integration for context-aware advice.
