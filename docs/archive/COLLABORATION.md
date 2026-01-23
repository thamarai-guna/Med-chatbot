# Collaboration Workflow

## For You (Primary Developer)

### First Time Setup
```bash
# 1. Create and commit vector store
python system_loader.py

# 2. Check what will be committed
git status

# 3. Commit vector stores and code
git add "vector store/shared/"
git add "Document-pdfs/"
git add requirements.txt
git add backend_api.py rag_engine.py  # etc.
git commit -m "Add shared medical knowledge vector store"
git push
```

### Daily Work - Commit Changes
```bash
# After making changes
git add .
git commit -m "Your change description"
git push
```

**Note**: `.gitignore` is configured to:
- ✅ **COMMIT**: vector stores, requirements.txt, source code
- ❌ **IGNORE**: .venv/, .env, patient_records/, *.db

---

## For Your Partner (Collaborator)

### First Time Setup (One-time only)
```bash
# 1. Clone the repo
git clone https://github.com/thamarai-guna/Med-chatbot.git
cd Med-chatbot

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install packages (one time)
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env and add GROQ_API_KEY

# 5. Frontend setup (one time)
cd frontend
npm install
cd ..
```

### Daily Work - Pull & Use (No reinstall needed!)
```bash
# 1. Activate environment
.venv\Scripts\activate  # Windows

# 2. Pull latest changes
git pull

# 3. Quick update (smart - only if needed)
python quick_update.py

# 4. Run servers
# Terminal 1:
uvicorn backend_api:app --reload

# Terminal 2:
cd frontend
npm run dev
```

---

## When to Reinstall Packages

Your partner only needs to reinstall when:
- ✅ `requirements.txt` changes (new/updated packages)
- ✅ `frontend/package.json` changes

Otherwise, just `git pull` and run!

---

## Shared Resources (Auto-synced via Git)

These are committed and pulled automatically:

1. **Vector Stores**
   - `vector store/shared/` - Medical knowledge (FAISS indexes)
   - Partner gets this automatically on pull!

2. **Source Documents**
   - `Document-pdfs/` - Medical books
   - No need to rebuild vector store

3. **Code & Config**
   - All `.py` files
   - `requirements.txt` (locked versions)
   - `.env.example` (template)

---

## Private/Local Only (Not shared)

These stay on each person's machine:

- `.venv/` - Python virtual environment (rebuild per machine)
- `.env` - API keys and secrets
- `patient_records/` - Patient data (privacy)
- `*.db` - Database files (local data)

---

## Quick Commands

### For You (Push changes)
```bash
git add .
git commit -m "Description"
git push
```

### For Partner (Get changes)
```bash
git pull
python quick_update.py  # Smart sync
```

---

## Benefits

✅ **No repeated installs** - Packages stay until requirements.txt changes  
✅ **Vector stores shared** - No need to rebuild (saves time!)  
✅ **Smart updates** - `quick_update.py` only installs if needed  
✅ **Clean separation** - Private data stays local  
✅ **Version locked** - Same package versions = no conflicts  

---

## Troubleshooting

**Q: Partner sees "vector store not found"**  
A: You forgot to commit it. Run: `git add "vector store/shared/" && git commit && git push`

**Q: Package errors after pull**  
A: `requirements.txt` changed. Run: `pip install -r requirements.txt`

**Q: Environment variables missing**  
A: Each person needs their own `.env` file with their GROQ_API_KEY

**Q: Patient data not syncing**  
A: Correct! `patient_records/` is in `.gitignore` for privacy
