# Task Status Bot v1.0

## Overview

A conversational AI assistant that helps teams find task status information when team members are away. Upload your task list once, share the link with your team, and they can ask questions about task status, deadlines, and blockers.

**Built with:** Python, Flask, Groq API, ChromaDB, Embeddings

---

## Features

- ✅ Chat interface (no login needed)
- ✅ Understands task questions ("What's status of T001?")
- ✅ Provides context ("What's blocking us?")
- ✅ Automatic name recognition
- ✅ Friendly, conversational responses
- ✅ Zero database required

---

## Problem Solved

When you're on vacation/leave:
- Team members need task status
- They wait for your reply (hours/days)
- Work gets blocked

**Solution:** Upload task file once. Team asks bot. Instant answers.

---

## How It Works

1. **You:** Upload `task_status.csv` + optional `task_status.txt` to `tasks/` folder
2. **Deploy:** Push to GitHub, deploy to Render
3. **Team:** Opens chatbot, types name
4. **Team:** Asks task questions
5. **Bot:** Searches task database using embeddings, returns answer
6. **Result:** Instant information, unblocked work

---

## Setup & Installation

### Prerequisites
- Python 3.8+
- Groq API key (free tier)

### Installation

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/TaskStatusBot
cd TaskStatusBot

# Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Get Groq API key:**
   - Go to https://console.groq.com
   - Sign up (free)
   - Create API key

2. **Create `.env` file:**
   ```
   GROQ_API_KEY=your_key_here
   ```

3. **Prepare task file:**
   - Create `tasks/task_status.csv` (required)
   - Optionally create `tasks/task_status.txt` (for richer context)

### Running Locally

```bash
python app.py
```

Visit: `http://localhost:5000`

---

## Task File Format

### CSV Format (Required)

```csv
task_id,project,title,status,due_date,dependencies,notes,last_updated
T001,ProjectX,API Integration,In Progress,2024-05-05,T002,Waiting on DB schema,2024-05-02
T002,ProjectY,Database Setup,Blocked,2024-05-03,None,Needs DevOps approval,2024-05-02
T003,ProjectX,Testing,Not Started,2024-05-10,T001,Can start after API,2024-05-01
```

### TXT Format (Optional - for richer context)

```
TASK: API Integration (T001)
PROJECT: ProjectX
STATUS: In Progress
DUE: 2024-05-05
DEPENDENCIES: T002
NOTES: Database schema expected from DevOps by 2024-05-04
LAST_UPDATED: 2024-05-02

---

TASK: Database Setup (T002)
...
```

**Both files are optional. Use CSV for structure, TXT for detailed notes.**

---

## Usage Example

```
Visitor: "Hi, I'm Raj"
Bot: "Nice to meet you, Raj! 👋 What would you like to know?"

Visitor: "What's the status of T001?"
Bot: "Hi Raj, API Integration (T001) is in progress. Due on 2024-05-05. 
     Dependencies: T002 (Database Setup). Waiting on DB schema from DevOps."

Visitor: "What's blocking us?"
Bot: "Hi Raj, Task T002 (Database Setup) is blocked. Needs DevOps approval 
     for production database. Approval is pending from security team."
```

---

## Architecture

```
Backend:
- Flask app loads task CSV/TXT on startup
- DocumentProcessor chunks & embeds task data
- Groq API generates conversational answers
- Embeddings handle semantic search

Frontend:
- Chat interface only (no upload UI)
- Asks visitor name first
- Supports natural language questions
- Responsive design (mobile + desktop)
```

---

## Deployment

### Deploy to Render (Free)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Task Status Bot v1.0"
   git push origin main
   ```

2. **Connect to Render:**
   - Go to https://render.com
   - Create new Web Service
   - Connect GitHub repo
   - Set environment variable: `GROQ_API_KEY=your_key`
   - Deploy

3. **Share link:**
   - Your app is live at `taskstatusbot.onrender.com`
   - Share with team

---

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Groq API (free LLM inference)
- **Embeddings:** SentenceTransformers
- **Search:** ChromaDB (vector database)
- **Frontend:** HTML, CSS, JavaScript
- **Hosting:** Render (free tier)

---

## Cost

- **Development:** $0 (free tiers)
- **Deployment:** $0 (Render free tier)
- **API calls:** $0 (Groq free tier: 500 calls/month)
- **Total:** $0 forever (for portfolio/demo use)

---

## Files Required

| File | Purpose |
|------|---------|
| `app.py` | Flask backend, session management, API routes |
| `document_processor.py` | CSV/TXT processing, chunking, embeddings |
| `qa_engine.py` | Groq integration, prompt engineering |
| `requirements.txt` | Python dependencies |
| `.env` | Groq API key (don't commit) |
| `.gitignore` | Ignore sensitive files |
| `templates/base.html` | HTML base layout |
| `templates/index.html` | Chat interface |
| `static/css/style.css` | Styling |
| `static/js/chat.js` | Frontend logic |
| `tasks/task_status.csv` | Your task list |
| `tasks/task_status.txt` | Optional: detailed notes |

---

## v1.0 Scope (MVP)

**Included:**
- ✅ Chat interface
- ✅ CSV + TXT file support
- ✅ Name collection
- ✅ Task question answering
- ✅ Friendly responses

**Not included (Future):**
- ❌ Authentication
- ❌ Database
- ❌ Logging/Audit
- ❌ Admin dashboard
- ❌ Multiple users

---

## Future Roadmap

**v2.0 (PM Dashboard):**
- Team member login
- Daily status updates
- Admin controls
- Audit logging

**v3.0 (Advanced):**
- Multiple projects
- Dependency visualization
- Automated notifications
- Analytics

---

## Learning Outcomes

After building this, you'll understand:
- ✅ Conversational AI (intent detection, context)
- ✅ Embeddings & vector search
- ✅ File processing (CSV, TXT)
- ✅ Flask backend architecture
- ✅ Frontend-backend communication
- ✅ Deployment & DevOps
- ✅ Real-world AI application design

---

## Troubleshooting

**"Tasks not loaded"**
- Check `tasks/` folder exists
- Verify `task_status.csv` exists
- Check file encoding (UTF-8)

**"GROQ_API_KEY not found"**
- Create `.env` file with API key
- Set environment variable before running

**"Can't find embeddings model"**
- First run takes 30 seconds (downloading model)
- Wait for download to complete

**"Port 5000 already in use"**
- Change port in `app.py`: `app.run(port=5001)`

---

## License

MIT License - Free to use, modify, and distribute

---

## Author

Built as a portfolio project demonstrating:
- Full-stack development
- AI/RAG systems
- Production thinking
- Clean code practices
