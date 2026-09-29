# family-health-ai
Multi-agent family health system using Nebius and NVIDIA
# Family Health Intelligence System
## Nebius x NVIDIA Global AI Hackathon Submission (Week 1 Prototype)

An autonomous health assistant that reasons about family health records using multi-agent AI, powered by **Nebius Token Factory** and **NVIDIA Nemotron models**.

### 🎯 What It Does

- **Stores health records privately** — medications, lab results, doctor notes, conditions
- **Semantic search** — finds relevant past information even with fuzzy queries
- **Multi-agent reasoning** — Router, Medication Manager, and Question Reasoner agents collaborate
- **Drug interaction checking** — alerts on potential medication conflicts
- **Chain-of-thought reasoning** — agents show their logic step by step

### 🏗️ Architecture (Week 1)

```
User Query
    ↓
[Router Agent] ← Nemotron Nano (fast routing)
    ↓ decides which agents to invoke
    ├→ [Medication Manager Agent] ← Nemotron Ultra (reasoning)
    │   ├ Checks interactions
    │   ├ Searches memory
    │   └ Returns: answer + alerts
    │
    ├→ [Question Reasoner Agent] ← Nemotron Ultra
    │   ├ Semantic search on records
    │   ├ Reasons step by step
    │   └ Returns: answer + confidence
    │
    └→ [Coordinator]
        ├ Synthesizes results
        └ Returns final answer
    
[Memory Store] ← SQLite + embeddings (sentence-transformers)
    ├ People profiles
    ├ Health records (type: medication, lab, condition, note)
    ├ Feedback log (for learning)
    └ Semantic embeddings for each record
```

### 🚀 Quick Start

#### 1. Install dependencies
```bash
pip install -r requirements.txt
```

#### 2. Set up Nebius API
- Go to https://nebius.ai
- Create an account and get API key from Token Factory
- Create `.env` file:
```
NEBIUS_API_KEY=your_key_here
NEBIUS_API_ENDPOINT=https://api.nebius.ai/v1/messages
NEMOTRON_NANO=nemotron-4-nano
NEMOTRON_ULTRA=nemotron-4-ultra
```

(Check Nebius docs for exact model names and endpoint.)

#### 3. Run the demo
```bash
python main.py
```

Then type:
```
demo
```

#### 4. Try it yourself
```
add-person Mom Mother 68
add-record Mom medication "Lisinopril 10mg daily"
add-record Mom lab "Blood pressure 138/88"
ask Mom "Is Mom's blood pressure controlled?"
```

### 🧠 How It Works

**Router Agent (Nemotron Nano):**
- Reads user query
- Decides which agents to invoke (medication_manager, question_reasoner, etc.)
- Routes urgency level (low/medium/high)

**Medication Manager Agent (Nemotron Ultra):**
- Retrieves all medications for the person
- Searches memory for relevant interactions/notes
- Checks if queried drugs interact
- Uses chain-of-thought reasoning: "What drugs are involved? → Are there interactions? → What's the risk?"
- Returns answer + alerts

**Question Reasoner Agent (Nemotron Ultra):**
- Does semantic search on all health records
- Retrieves top-5 most relevant records
- Reasons through them step by step
- Returns answer + confidence level

**Coordinator:**
- Orchestrates agent execution
- Synthesizes results from multiple agents
- Builds final coherent answer

**Memory (SQLite + Embeddings):**
- Stores people and health records
- Creates embeddings with `sentence-transformers`
- Enables semantic search: "dizzy spells" finds records about dizziness, balance, vertigo, etc.
- Saves all feedback for continuous learning (Week 2)

### 📊 Current Capabilities (Week 1)

✅ Add family members and health records
✅ Ask questions and get reasoned answers
✅ Check medication interactions
✅ Semantic search over records
✅ Multi-agent routing and execution
✅ Chain-of-thought reasoning
✅ Alert generation

### 🗓️ Roadmap

**Week 2:** 
- Add Appointment Scheduler Agent
- Add Health Trend Analyzer Agent
- Implement feedback loop for learning

**Week 3:**
- Nebius Serverless Jobs integration (background tasks, weekly digests)
- Web interface
- Scheduled reminders

**Week 4:**
- Polish and demo video
- Public repo with MIT license
- Deployment preparation

### 📝 How to Use

```bash
# View all commands
help

# Add a family member
add-person Mom Mother 68

# Add health records
add-record Mom medication "Lisinopril 10mg daily"
add-record Mom lab "Blood glucose 145 mg/dL"
add-record Mom condition "Type 2 Diabetes"

# Ask questions (agents handle it)
ask Mom "What medications is Mom on?"
ask Mom "Could Mom's dizziness be from her BP medication?"
ask Mom "What did the last lab test show?"

# List records
list-records Mom

# Run demo
demo
```

### 🛠️ Technical Details

**Language:** Python 3.10+

**Dependencies:**
- `requests` — Nebius API calls
- `sentence-transformers` — embeddings for semantic search
- `sqlite3` — local memory store
- `numpy` — vector operations

**API Calls:**
- Nemotron Nano for routing (cheap, fast)
- Nemotron Ultra for reasoning (slower, smarter)
- Each query triggers multiple API calls (be mindful of Nebius credits)

**Privacy:**
- All data stored locally in SQLite
- Only prompts + necessary context sent to Nebius API
- Users control what data gets uploaded

### 📄 Feedback

This is Week 1 of the Nebius x NVIDIA hackathon. Feedback on Nebius Token Factory, Nemotron models, and this system's performance is welcome!

### 📜 License

MIT License (required for hackathon submission)

---

**Built for the Nebius x NVIDIA Global AI Hackathon**
