# AI Interview Analyzer - Complete Full Stack Project

## Structure

```text
AI-Interview-Analyzer/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── .env.example
├── models/
├── routes/
├── services/
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── README.md
└── README.md
```

## Run Backend

Open PowerShell in this project folder:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Backend:
http://127.0.0.1:5000

## Run Frontend

Install VS Code Live Server, then right-click:

```text
frontend/index.html
```

and choose:

```text
Open with Live Server
```

The frontend is configured to use:

```text
http://127.0.0.1:5000/api
```

## AI

Keep the AI API key only in the backend `.env` file. Never put it in frontend JavaScript.
