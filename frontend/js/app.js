const app = document.getElementById("app");

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[char]));
}

function toast(message) {
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2800);
}

function user() {
  try { return JSON.parse(localStorage.getItem("user") || "null"); }
  catch (_) { return null; }
}

function loggedIn() {
  return Boolean(localStorage.getItem("token"));
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  location.hash = "#login";
}

function nav() {
  return `
    <nav class="navbar">
      <div class="container" style="display:flex;justify-content:space-between;align-items:center;width:100%">
        <div class="brand"><div class="logo">AI</div> Interview Analyzer</div>
        <div class="nav-actions">
          ${loggedIn() ? `
            <button class="btn btn-secondary" onclick="location.hash='#dashboard'">Dashboard</button>
            <button class="btn btn-danger" onclick="logout()">Logout</button>
          ` : `
            <button class="btn btn-secondary" onclick="location.hash='#login'">Login</button>
            <button class="btn btn-primary" onclick="location.hash='#register'">Get Started</button>
          `}
        </div>
      </div>
    </nav>
  `;
}

function render() {
  const route = location.hash || "#home";
  if (route === "#home") home();
  else if (route === "#login") login();
  else if (route === "#register") register();
  else if (route === "#setup") setup();
  else if (route === "#interview") interview();
  else if (route.startsWith("#result")) result(route.split("/")[1]);
  else if (route === "#dashboard") dashboard();
  else home();
}

function home() {
  app.innerHTML = `
    ${nav()}
    <main class="container hero">
      <div class="hero-grid">
        <section>
          <span class="badge">✦ AI-powered interview practice</span>
          <h1>Practice smarter.<br><span class="gradient">Interview better.</span></h1>
          <p>
            Take realistic mock interviews, answer role-specific questions,
            and get instant AI-powered feedback on your technical knowledge,
            communication, relevance and confidence.
          </p>
          <div class="hero-buttons">
            <button class="btn btn-primary" onclick="location.hash='${loggedIn() ? "#setup" : "#register"}'">Start AI Interview →</button>
            ${loggedIn() ? `<button class="btn btn-secondary" onclick="location.hash='#dashboard'">View Dashboard</button>` : ""}
          </div>
        </section>
        <section class="hero-card">
          <div class="ai-orb">✦</div>
          <h3 style="text-align:center">AI Interview Analysis</h3>
          <div class="mini-score"><span>Technical Knowledge</span><strong>85%</strong></div>
          <div class="mini-score"><span>Communication</span><strong>78%</strong></div>
          <div class="mini-score"><span>Relevance</span><strong>91%</strong></div>
          <div class="mini-score"><span>Overall</span><strong>84%</strong></div>
        </section>
      </div>
    </main>
  `;
}

function login() {
  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="card form-card">
        <h2>Welcome back 👋</h2>
        <p style="color:var(--muted)">Login to continue your interview practice.</p>
        <form id="loginForm">
          <div class="form-group"><label>Email</label><input class="input" id="email" type="email" required placeholder="you@example.com"></div>
          <div class="form-group"><label>Password</label><input class="input" id="password" type="password" required placeholder="••••••••"></div>
          <button class="btn btn-primary" style="width:100%">Login</button>
        </form>
        <div class="form-footer">Don't have an account? <span class="link" onclick="location.hash='#register'">Create one</span></div>
      </div>
    </main>
  `;

  document.getElementById("loginForm").onsubmit = async e => {
    e.preventDefault();
    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: document.getElementById("email").value.trim(),
          password: document.getElementById("password").value
        })
      });
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      location.hash = "#dashboard";
    } catch (err) { toast(err.message); }
  };
}

function register() {
  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="card form-card">
        <h2>Create your account 🚀</h2>
        <p style="color:var(--muted)">Start practicing with your personal AI interview coach.</p>
        <form id="registerForm">
          <div class="form-group"><label>Name</label><input class="input" id="name" required placeholder="Your name"></div>
          <div class="form-group"><label>Email</label><input class="input" id="email" type="email" required placeholder="you@example.com"></div>
          <div class="form-group"><label>Password</label><input class="input" id="password" type="password" minlength="6" required placeholder="Minimum 6 characters"></div>
          <button class="btn btn-primary" style="width:100%">Create Account</button>
        </form>
        <div class="form-footer">Already registered? <span class="link" onclick="location.hash='#login'">Login</span></div>
      </div>
    </main>
  `;

  document.getElementById("registerForm").onsubmit = async e => {
    e.preventDefault();
    try {
      const data = await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: document.getElementById("name").value.trim(),
          email: document.getElementById("email").value.trim(),
          password: document.getElementById("password").value
        })
      });
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      location.hash = "#setup";
    } catch (err) { toast(err.message); }
  };
}

function setup() {
  if (!loggedIn()) return location.hash = "#login";

  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="page-title">
        <h1>Set up your interview</h1>
        <p>Choose a role and difficulty. The AI will prepare your interview.</p>
      </div>

      <div class="setup-grid">
        <section class="card">
          <h3>Choose job role</h3>
          <div class="role-grid">
            ${["Software Developer","Python Developer","Data Analyst","Cyber Security"].map((r, i) =>
              `<button class="role ${i===0 ? "active" : ""}" data-role="${r}">${r}</button>`
            ).join("")}
          </div>
          <div class="form-group">
            <label>Or enter a custom role</label>
            <input class="input" id="customRole" placeholder="e.g. Full Stack Developer">
          </div>
        </section>

        <section class="card">
          <h3>Interview settings</h3>
          <div class="form-group">
            <label>Difficulty</label>
            <select class="input" id="difficulty">
              <option value="easy">Easy</option>
              <option value="medium" selected>Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div class="form-group">
            <label>Number of questions</label>
            <select class="input" id="questionCount">
              <option>5</option><option>7</option><option>10</option>
            </select>
          </div>
          <button class="btn btn-primary" style="width:100%;margin-top:12px" id="startBtn">Start Interview →</button>
        </section>
      </div>
    </main>
  `;

  let selectedRole = "Software Developer";
  document.querySelectorAll(".role").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll(".role").forEach(x => x.classList.remove("active"));
      btn.classList.add("active");
      selectedRole = btn.dataset.role;
      document.getElementById("customRole").value = "";
    };
  });

  document.getElementById("customRole").oninput = () => {
    if (document.getElementById("customRole").value.trim()) {
      document.querySelectorAll(".role").forEach(x => x.classList.remove("active"));
      selectedRole = "";
    }
  };

  document.getElementById("startBtn").onclick = async () => {
    const job_role = document.getElementById("customRole").value.trim() || selectedRole;
    try {
      const data = await api("/interview/start", {
        method: "POST",
        body: JSON.stringify({
          job_role,
          difficulty: document.getElementById("difficulty").value,
          question_count: Number(document.getElementById("questionCount").value)
        })
      });
      sessionStorage.setItem("interview", JSON.stringify(data));
      location.hash = "#interview";
    } catch (err) { toast(err.message); }
  };
}

async function interview() {
  if (!loggedIn()) return location.hash = "#login";

  const saved = JSON.parse(sessionStorage.getItem("interview") || "null");
  if (!saved) return location.hash = "#setup";

  let questions = saved.questions;
  let index = Number(sessionStorage.getItem("question_index") || 0);
  let analyses = [];

  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="interview-layout">
        <aside class="card sidebar-card">
          <div class="question-number" id="progressText"></div>
          <div class="progress" style="margin:10px 0 20px"><div id="progressBar"></div></div>
          <div class="interview-meta">
            <span class="chip">${escapeHtml(saved.job_role)}</span>
            <span class="chip">${escapeHtml(saved.difficulty)}</span>
          </div>
          <hr style="border:0;border-top:1px solid var(--border);margin:22px 0">
          <p style="color:var(--muted);font-size:13px;line-height:1.7">
            Tip: Structure your answer clearly. Explain the concept, give an example,
            and mention the result when possible.
          </p>
        </aside>

        <section class="card">
          <div class="question-number" id="questionNo"></div>
          <div class="question-text" id="questionText"></div>
          <textarea id="answer" class="input" placeholder="Type your answer here..."></textarea>
          <div class="answer-actions">
            <button class="btn btn-secondary" id="backBtn">← Back</button>
            <button class="btn btn-primary" id="nextBtn">Submit & Continue →</button>
          </div>
        </section>
      </div>
    </main>
  `;

  async function showQuestion() {
    const q = questions[index];
    questionNo.textContent = `Question ${index + 1}`;
    questionText.textContent = q.question;
    progressText.textContent = `${index + 1} of ${questions.length}`;
    progressBar.style.width = `${((index + 1) / questions.length) * 100}%`;
    answer.value = sessionStorage.getItem(`answer_${q.id}`) || "";
    backBtn.disabled = index === 0;
    nextBtn.textContent = index === questions.length - 1 ? "Submit & Finish ✓" : "Submit & Continue →";
  }

  backBtn.onclick = () => {
    if (index > 0) {
      sessionStorage.setItem(`answer_${questions[index].id}`, answer.value);
      index--;
      sessionStorage.setItem("question_index", index);
      showQuestion();
    }
  };

  nextBtn.onclick = async () => {
    const q = questions[index];
    const text = answer.value.trim();
    if (!text) return toast("Please enter an answer first.");

    nextBtn.disabled = true;
    nextBtn.textContent = "AI is analyzing...";

    try {
      const data = await api(`/interview/${saved.interview_id}/answer`, {
        method: "POST",
        body: JSON.stringify({ question_id: q.id, answer: text })
      });

      analyses[index] = data.question;
      sessionStorage.setItem(`answer_${q.id}`, text);

      if (index === questions.length - 1) {
        await api(`/interview/${saved.interview_id}/finish`, { method: "POST" });
        sessionStorage.removeItem("question_index");
        location.hash = `#result/${saved.interview_id}`;
      } else {
        index++;
        sessionStorage.setItem("question_index", index);
        await showQuestion();
      }
    } catch (err) {
      toast(err.message);
    } finally {
      nextBtn.disabled = false;
    }
  };

  showQuestion();
}

async function result(id) {
  if (!loggedIn()) return location.hash = "#login";
  app.innerHTML = `${nav()}<main class="container page"><div class="loading">Loading your AI report...</div></main>`;

  try {
    const data = await api(`/interview/${id}/result`);
    const score = Math.round(data.overall_score || 0);
    const first = data.questions?.[0];

    app.innerHTML = `
      ${nav()}
      <main class="container page">
        <div class="page-title">
          <h1>Interview Report 🎯</h1>
          <p>${escapeHtml(data.job_role)} · ${escapeHtml(data.difficulty)} difficulty</p>
        </div>

        <section class="card result-header">
          <div>
            <div class="score-circle" style="--score:${score}%">
              <div class="score-number">${score}</div>
            </div>
          </div>
          <div>
            <span class="badge">AI Analysis Complete</span>
            <h2>Your overall score is ${score}%</h2>
            <p style="color:var(--muted);line-height:1.8">
              Review the category scores and personalized feedback below to improve your next interview.
            </p>
            <button class="btn btn-primary" onclick="location.hash='#setup'">Take Another Interview</button>
          </div>
        </section>

        <div class="metric-grid">
          ${[
            ["Technical", first?.technical_score],
            ["Communication", first?.communication_score],
            ["Relevance", first?.relevance_score],
            ["Confidence", first?.confidence_score]
          ].map(([label,val]) => `<div class="metric"><small>${label}</small><strong>${Math.round(val || 0)}%</strong></div>`).join("")}
        </div>

        <div class="feedback-grid">
          <section class="card feedback-card"><h3>💪 Strengths</h3>${list(data.strengths)}</section>
          <section class="card feedback-card"><h3>🔧 Areas to improve</h3>${list(data.weaknesses)}</section>
          <section class="card feedback-card"><h3>💡 Suggestions</h3>${list(data.suggestions)}</section>
        </div>

        <section class="card" style="margin-top:20px">
          <h2>Question-by-question analysis</h2>
          ${(data.questions || []).map((q, i) => `
            <div style="padding:20px 0;border-bottom:1px solid var(--border)">
              <strong>Q${i+1}. ${escapeHtml(q.question)}</strong>
              <p style="color:var(--muted)"><b>Your answer:</b> ${escapeHtml(q.answer || "No answer")}</p>
              <p><b>Score:</b> ${Math.round(q.overall_score || 0)}% · ${escapeHtml(q.feedback || "")}</p>
            </div>
          `).join("")}
        </section>
      </main>
    `;
  } catch (err) {
    app.innerHTML = `${nav()}<main class="container page"><div class="card"><h2>Unable to load report</h2><p>${escapeHtml(err.message)}</p><button class="btn btn-primary" onclick="location.hash='#dashboard'">Dashboard</button></div></main>`;
  }
}

function list(items = []) {
  if (!items.length) return "<p style='color:var(--muted)'>No feedback available.</p>";
  return `<ul>${items.map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>`;
}

async function dashboard() {
  if (!loggedIn()) return location.hash = "#login";
  app.innerHTML = `${nav()}<main class="container page"><div class="loading">Loading dashboard...</div></main>`;

  try {
    const [data, history] = await Promise.all([
      api("/dashboard"),
      api("/interview/history/all")
    ]);

    app.innerHTML = `
      ${nav()}
      <main class="container page">
        <div class="page-title">
          <h1>Welcome back, ${escapeHtml(user()?.name || "Candidate")} 👋</h1>
          <p>Track your interview progress and keep improving.</p>
        </div>

        <div class="metric-grid">
          <div class="metric"><small>Total Interviews</small><strong>${data.total_interviews}</strong></div>
          <div class="metric"><small>Completed</small><strong>${data.completed_interviews}</strong></div>
          <div class="metric"><small>Average Score</small><strong>${data.average_score}%</strong></div>
          <div class="metric"><small>Best Score</small><strong>${data.best_score}%</strong></div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;margin:30px 0 15px;gap:10px">
          <h2 style="margin:0">Interview History</h2>
          <button class="btn btn-primary" onclick="location.hash='#setup'">+ New Interview</button>
        </div>

        <section class="card">
          ${history.interviews.length ? history.interviews.map(i => `
            <div class="history-item">
              <div>
                <strong>${escapeHtml(i.job_role)}</strong>
                <div style="color:var(--muted);font-size:13px;margin-top:5px">
                  ${escapeHtml(i.difficulty)} · ${new Date(i.created_at).toLocaleString()}
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:14px">
                <span class="history-score">${Math.round(i.overall_score || 0)}%</span>
                ${i.status === "completed" ? `<button class="btn btn-secondary" onclick="location.hash='#result/${i.id}'">View</button>` : ""}
              </div>
            </div>
          `).join("") : `<p style="color:var(--muted)">No interviews yet. Start your first AI interview.</p>`}
        </section>
      </main>
    `;
  } catch (err) {
    app.innerHTML = `${nav()}<main class="container page"><div class="card"><h2>Dashboard error</h2><p>${escapeHtml(err.message)}</p></div></main>`;
  }
}

window.addEventListener("hashchange", render);
render();
