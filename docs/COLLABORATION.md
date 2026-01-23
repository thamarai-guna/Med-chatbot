# Collaboration Workflow

## For You (Primary Developer)

### First Time Setup
```bash
python system_loader.py
```
Commit after building shared vector store:
```bash
git add "vector store/shared/" "Document-pdfs/" requirements.txt
# add code files as needed
git commit -m "Add shared vector store"
git push
```

### Daily Work
```bash
git add .
git commit -m "Description"
git push
```

Note: `.gitignore` commits vector stores and code; ignores `.venv/`, `.env`, `patient_records/`, `*.db`.

---

## For Your Partner

### First Time Only
```bash
git clone https://github.com/thamarai-guna/Med-chatbot.git
cd Med-chatbot
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env     # add GROQ_API_KEY
cd frontend && npm install && cd ..
```

### Daily (No Reinstall Needed)
```bash
git pull
python quick_update.py  # only installs if needed
uvicorn backend_api:app --reload
cd frontend && npm run dev
```

Reinstall only when `requirements.txt` or `frontend/package.json` changes.

---

## Shared via Git
- `vector store/shared/`
- `Document-pdfs/`
- Source code
- `requirements.txt`
- `.env.example`

## Local Only
- `.venv/`
- `.env`
- `patient_records/`
- `*.db`

---

## Quick Commands
- Push: `git add . && git commit -m "msg" && git push`
- Pull & sync: `git pull && python quick_update.py`

---

## Troubleshooting
- Missing vector store: `git pull` or `python system_loader.py`
- Package errors: `pip install -r requirements.txt`
- Missing env: copy `.env.example` and add `GROQ_API_KEY`
- Patient data sync: intentionally ignored for privacy
