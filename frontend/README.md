# AI Interview Analyzer - Frontend

This frontend is plain HTML/CSS/JavaScript and connects to the Flask backend.

## 1. Start backend first

From the backend folder:

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

Backend must be available at:

```text
http://127.0.0.1:5000
```

The frontend defaults to:

```text
http://127.0.0.1:5000/api
```

## 2. Open frontend

Open `index.html` in VS Code using a local development server such as Live Server.

## 3. Features

- Landing page
- Registration
- Login with JWT
- Separate admin login page
- Interview setup
- Role selection
- Difficulty selection
- Question-by-question interview
- Voice interview with spoken questions and microphone answers
- Answer submission to Flask
- AI analysis loading state
- Score report
- Strengths
- Weaknesses
- Suggestions
- Question-by-question feedback
- Dashboard
- Interview history
- Admin panel with user and interview monitoring
- Responsive design

## 4. Backend URL

If your backend is hosted somewhere else, open browser console and run:

```js
setApiBase("https://YOUR-BACKEND-DOMAIN/api")
```

Or edit the `API_BASE` default in `js/api.js`.

## 5. Admin setup

Set `ADMIN_EMAIL` in the backend `.env` file to the email of the administrator account. The account must register with that same email, then log in again to receive admin access.

## 6. Important

Never put an AI API key in frontend JavaScript. The key belongs only in the Python backend `.env`.
