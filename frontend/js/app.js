const app = document.getElementById("app");
let interviewTimer = null;
document.documentElement.dataset.theme = localStorage.getItem("theme") === "dark" ? "dark" : "light";

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = nextTheme;
  localStorage.setItem("theme", nextTheme);
}

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

function isAdmin() {
  return Boolean(user()?.is_admin);
}

function logout() {
  const destination = isAdmin() ? "#admin-login" : "#login";
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  location.hash = destination;
}

function nav() {
  return `
    <nav class="navbar">
      <div class="container" style="display:flex;justify-content:space-between;align-items:center;width:100%">
        <div class="brand"><div class="logo">AI</div> Interview Analyzer</div>
        <div class="nav-actions">
          ${loggedIn() ? isAdmin() ? `
            <button class="btn btn-secondary" onclick="location.hash='#admin'">Admin Console</button>
            <button class="btn btn-danger" onclick="logout()">Logout</button>
          ` : `
            <button class="btn btn-secondary" onclick="location.hash='#dashboard'">Dashboard</button>
            <button class="btn btn-secondary" onclick="location.hash='#resume'">Resume & Match</button>
            <button class="btn btn-secondary" onclick="location.hash='#study'">Study Plan</button>
            <button class="btn btn-primary" onclick="location.hash='#setup'">New Interview</button>
            <button class="btn btn-danger" onclick="logout()">Logout</button>
          ` : `
            <button class="btn btn-secondary" onclick="location.hash='#login'">Login</button>
            <button class="btn btn-primary" onclick="location.hash='#register'">Get Started</button>
            <span class="nav-divider" aria-hidden="true"></span>
            <button class="nav-admin-link" onclick="location.hash='#admin-login'">Admin Login</button>
          `}
          <button class="theme-toggle" type="button" onclick="toggleTheme()" aria-label="Switch to ${document.documentElement.dataset.theme === "dark" ? "light" : "dark"} mode" title="Switch theme">${document.documentElement.dataset.theme === "dark" ? "☀" : "☾"}</button>
        </div>
      </div>
    </nav>
  `;
}

function render() {
  const route = location.hash || "#home";
  if (route !== "#interview" && interviewTimer !== null) {
    clearInterval(interviewTimer);
    interviewTimer = null;
  }

  if (loggedIn()) {
    const isAdminRoute = route === "#admin" || route === "#admin-login";
    const isUserRoute = route === "#login" || route === "#register" || route === "#dashboard" || route === "#resume" || route === "#study" || route === "#setup" || route === "#interview" || route.startsWith("#result");
    if (isAdmin() && isUserRoute) {
      location.hash = "#admin";
      return;
    }
    if (!isAdmin() && isAdminRoute) {
      location.hash = "#dashboard";
      return;
    }
  } else if (route === "#admin") {
    location.hash = "#admin-login";
    return;
  }

  if (route === "#home") home();
  else if (route === "#login") login();
  else if (route === "#admin-login") adminLogin();
  else if (route === "#register") register();
  else if (route === "#resume") resumeAnalyzer();
  else if (route === "#study") studyPlanPage();
  else if (route === "#setup") setup();
  else if (route === "#interview") interview();
  else if (route.startsWith("#result")) result(route.split("/")[1]);
  else if (route === "#dashboard") dashboard();
  else if (route === "#admin") adminDashboard();
  else home();
}

function home() {
  app.innerHTML = `
    ${nav()}
    <main class="home-page">
      <section class="container hero home-hero">
        <div class="hero-grid">
          <section class="home-copy">
            <span class="badge"><span class="status-dot"></span> YOUR NEXT INTERVIEW, REHEARSED</span>
            <h1>Make practice<br>feel like the <span class="gradient">real thing.</span></h1>
            <p>
              Take a role-specific mock interview, answer by voice or text,
              and get a clear AI report on what to sharpen next.
            </p>
            <div class="hero-buttons">
              <button class="btn btn-primary home-cta" onclick="location.hash='${loggedIn() ? "#setup" : "#register"}'">Start a practice interview <span aria-hidden="true">↗</span></button>
              ${loggedIn() ? `<button class="btn btn-secondary" onclick="location.hash='#dashboard'">Your dashboard</button>` : `<button class="btn btn-secondary" onclick="location.hash='#login'">Sign in</button>`}
            </div>
            <div class="home-trustline"><span class="trust-mark">01</span> No pressure. Just one better answer at a time.</div>
          </section>

          <section class="report-preview" aria-label="Example interview report preview">
            <div class="preview-topline"><span class="preview-kicker">REPORT PREVIEW</span><span class="preview-status"><span class="status-dot"></span> COMPLETE</span></div>
            <div class="preview-role"><div class="preview-role-icon">DS</div><div><strong>Data Analyst</strong><span>Mock interview · Medium</span></div><span class="preview-arrow" aria-hidden="true">↗</span></div>
            <div class="preview-score-row"><div><span class="preview-label">Overall score</span><strong class="preview-score">84<span>%</span></strong></div><div class="score-ring" aria-hidden="true"><span>84</span></div></div>
            <div class="preview-divider"></div>
            <div class="preview-metrics">
              <div><span>Technical</span><strong>85%</strong><i><b style="--fill:85%"></b></i></div>
              <div><span>Communication</span><strong>78%</strong><i><b style="--fill:78%"></b></i></div>
              <div><span>Relevance</span><strong>91%</strong><i><b style="--fill:91%"></b></i></div>
              <div><span>Confidence</span><strong>82%</strong><i><b style="--fill:82%"></b></i></div>
            </div>
            <div class="preview-note"><span aria-hidden="true">✳</span><span><strong>One thing to build on</strong><br>Use a specific example to make your answer more memorable.</span></div>
            <span class="preview-caption">Illustrative report preview</span>
          </section>
        </div>
        <div class="capability-row" aria-label="Interview features">
          <div><span class="capability-icon">↗</span><span>Questions for your target role</span></div>
          <div><span class="capability-icon">◖</span><span>Speak or type your answers</span></div>
          <div><span class="capability-icon">◎</span><span>Feedback you can act on</span></div>
        </div>
      </section>

      <section class="practice-section">
        <div class="container practice-inner">
          <div class="practice-heading"><span class="section-eyebrow">A SIMPLE PRACTICE LOOP</span><h2>From “what if?”<br>to “I’ve got this.”</h2></div>
          <div class="practice-steps">
            <article class="practice-step"><span class="step-number">01</span><h3>Set your scene</h3><p>Choose a role, set the difficulty, and decide how many questions to take on.</p></article>
            <article class="practice-step"><span class="step-number">02</span><h3>Find your rhythm</h3><p>Work through interview questions at your own pace. Answer by voice or type.</p></article>
            <article class="practice-step"><span class="step-number">03</span><h3>Know what’s next</h3><p>Review your scores and feedback, then bring what you learned into your next round.</p></article>
          </div>
          <div class="practice-footer"><span>Ready when you are.</span><button class="btn btn-primary" onclick="location.hash='${loggedIn() ? "#setup" : "#register"}'">Build your confidence <span aria-hidden="true">↗</span></button></div>
        </div>
      </section>
    </main>
  `;
}

function login() {
  app.innerHTML = `
    ${nav()}
    <main class="container page auth-page">
      <div class="auth-layout">
        <section class="auth-story">
          <span class="auth-eyebrow"><span class="status-dot"></span> AI INTERVIEW PRACTICE</span>
          <h1>Good interviews<br>start <span>before</span><br>the interview.</h1>
          <p>Pick up where you left off. Build your answers, find your pace, and walk into the next conversation prepared.</p>
          <div class="auth-question" aria-label="Example interview question">
            <div class="auth-question-top"><span>QUESTION PREVIEW</span><span>01 / 05</span></div>
            <p>“Tell me about a project you’re proud of. What made it challenging?”</p>
            <div class="auth-wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
            <div class="auth-question-foot"><span>ROLE-SPECIFIC</span><span>VOICE OR TEXT</span><span>YOUR OWN PACE</span></div>
          </div>
        </section>

        <section class="auth-panel">
          <div class="auth-panel-heading">
            <span class="auth-small-label">YOUR PRACTICE SPACE</span>
            <h2>Welcome back</h2>
            <p>Sign in to continue your interview practice.</p>
          </div>
          <form id="loginForm">
            <div class="form-group">
              <label for="email">Email address</label>
              <input class="input" id="email" type="email" autocomplete="email" required placeholder="you@example.com">
            </div>
            <div class="form-group">
              <label for="password">Password</label>
              <div class="password-field">
                <input class="input" id="password" type="password" autocomplete="current-password" required placeholder="Enter your password">
                <button class="password-toggle" id="togglePassword" type="button" aria-label="Show password" aria-pressed="false">Show</button>
              </div>
            </div>
            <button class="btn btn-primary auth-submit" type="submit">Sign in <span aria-hidden="true">↗</span></button>
            <p class="auth-status" id="loginStatus" role="status" aria-live="polite"></p>
          </form>
          <div class="auth-signup">New to Interview Analyzer? <a class="link" href="#register">Create an account <span aria-hidden="true">→</span></a></div>
          <div class="auth-security"><span aria-hidden="true">◈</span> Your practice history stays linked to your account.</div>
        </section>
      </div>
    </main>
  `;

  const loginForm = document.getElementById("loginForm");
  const passwordInput = document.getElementById("password");
  const passwordToggle = document.getElementById("togglePassword");
  const loginStatus = document.getElementById("loginStatus");

  passwordToggle.onclick = () => {
    const showPassword = passwordInput.type === "password";
    passwordInput.type = showPassword ? "text" : "password";
    passwordToggle.textContent = showPassword ? "Hide" : "Show";
    passwordToggle.setAttribute("aria-label", `${showPassword ? "Hide" : "Show"} password`);
    passwordToggle.setAttribute("aria-pressed", String(showPassword));
  };

  loginForm.onsubmit = async e => {
    e.preventDefault();
    const submitButton = loginForm.querySelector("button[type='submit']");
    submitButton.disabled = true;
    submitButton.textContent = "Signing in...";
    loginStatus.textContent = "Signing in to your account...";
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
    } catch (err) {
      loginStatus.textContent = err.message;
      toast(err.message);
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = 'Sign in <span aria-hidden="true">↗</span>';
    }
  };
}

function adminLogin() {
  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="card form-card admin-login-card">
        <h2>Admin Login</h2>
        <form id="adminLoginForm">
          <div class="form-group"><label for="adminEmail">Admin email</label><input class="input" id="adminEmail" type="email" autocomplete="username" required placeholder="admin@example.com"></div>
          <div class="form-group"><label>Password</label><input class="input" id="adminPassword" type="password" required placeholder="Enter password"></div>
          <button class="btn btn-primary" style="width:100%">Open Admin Panel</button>
        </form>
      </div>
    </main>
  `;

  document.getElementById("adminLoginForm").onsubmit = async event => {
    event.preventDefault();
    const button = event.target.querySelector("button");
    button.disabled = true;
    button.textContent = "Checking access...";
    try {
      const data = await api("/auth/admin-login", {
        method: "POST",
        body: JSON.stringify({
          email: document.getElementById("adminEmail").value.trim(),
          password: document.getElementById("adminPassword").value
        })
      });
      if (!data.user?.is_admin) {
        throw new Error("This account does not have admin access.");
      }
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      location.hash = "#admin";
    } catch (err) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      toast(err.message);
    } finally {
      button.disabled = false;
      button.textContent = "Open Admin Panel";
    }
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
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      location.hash = "#login";
      toast("Registration successful. Please login to continue.");
    } catch (err) { toast(err.message); }
  };
}

async function resumeAnalyzer() {
  if (!loggedIn()) return location.hash = "#login";
  if (isAdmin()) return location.hash = "#admin";

  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="page-title">
        <h1>Resume & job match</h1>
        <p>Review your resume profile, then compare it with a target role.</p>
      </div>
      <div class="resume-workspace">
        <section class="card resume-tool">
          <span class="section-eyebrow">01 / PROFILE</span>
          <h2>Analyze a resume</h2>
          <p class="resume-help">PDF, DOC, or DOCX · 5 MB maximum. Uploaded files are parsed and not retained.</p>
          <form id="resumeUploadForm">
            <label class="resume-file-label" for="resumeFile">Choose resume</label>
            <input class="input" type="file" id="resumeFile" name="file" accept=".pdf,.doc,.docx" required>
            <button class="btn btn-primary" id="resumeUploadButton" type="submit">Analyze resume <span aria-hidden="true">↗</span></button>
          </form>
          <div id="resumeOutput" class="resume-output" role="status" aria-live="polite"></div>
        </section>

        <section class="card resume-tool">
          <span class="section-eyebrow">02 / ROLE FIT</span>
          <h2>Match a job description</h2>
          <p class="resume-help">Paste the role details, or upload a plain-text .txt description.</p>
          <form id="jobMatchForm">
            <div class="form-group">
              <label for="resumeSelection">Resume</label>
              <select class="input" id="resumeSelection" required><option value="">Loading resumes...</option></select>
            </div>
            <div class="form-group">
              <label for="jobTitle">Job title</label>
              <input class="input" id="jobTitle" maxlength="120" placeholder="e.g. Python Backend Engineer">
            </div>
            <div class="form-group">
              <label for="jobDescription">Job description</label>
              <textarea class="input resume-description" id="jobDescription" required placeholder="Paste responsibilities, requirements, and skills..."></textarea>
            </div>
            <label class="resume-file-label" for="jobDescriptionFile">Or load a .txt file</label>
            <input class="input" type="file" id="jobDescriptionFile" accept=".txt,text/plain">
            <button class="btn btn-primary" id="jobMatchButton" type="submit">Compare with resume <span aria-hidden="true">↗</span></button>
          </form>
          <div id="jobMatchOutput" class="resume-output" role="status" aria-live="polite"></div>
        </section>
      </div>
      <section class="resume-history">
        <div class="resume-history-heading"><div><span class="section-eyebrow">YOUR FILES</span><h2>Saved resume analyses</h2></div></div>
        <div id="resumeList" class="resume-list"><p class="loading">Loading your resumes...</p></div>
      </section>
    </main>
  `;

  const resumeForm = document.getElementById("resumeUploadForm");
  const resumeSelect = document.getElementById("resumeSelection");
  const resumeOutput = document.getElementById("resumeOutput");
  const resumeList = document.getElementById("resumeList");
  const matchOutput = document.getElementById("jobMatchOutput");
  let savedResumes = [];

  function showResume(resume) {
    const profile = resume.profile || {};
    const analysis = resume.analysis || {};
    const values = items => Array.isArray(items) && items.length
      ? `<ul>${items.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
      : `<p class="resume-empty-value">None detected</p>`;
    resumeOutput.innerHTML = `
      <div class="resume-score-row"><div><span class="resume-label">Completeness score</span><strong>${Math.round(analysis.resume_score || 0)}%</strong></div><span class="resume-score-note">${escapeHtml(resume.filename)}</span></div>
      <div class="resume-profile-line"><strong>${escapeHtml(profile.name || "Name not detected")}</strong><span>${escapeHtml(profile.email || "Email not detected")}${profile.phone ? ` · ${escapeHtml(profile.phone)}` : ""}</span></div>
      <div class="resume-analysis-grid">
        <section><h3>Skills detected</h3>${values(analysis.skills_detected || profile.skills)}</section>
        <section><h3>Strong areas</h3>${values(analysis.strong_areas)}</section>
        <section><h3>Areas to improve</h3>${values(analysis.weak_areas)}</section>
        <section><h3>Suggested skills</h3>${values(analysis.recommended_skills)}</section>
        <section><h3>Interview topics</h3>${values(analysis.recommended_interview_topics)}</section>
        <section><h3>Role-specific gaps</h3>${values(analysis.missing_skills)}</section>
      </div>
      <p class="resume-summary">${escapeHtml(analysis.summary || "")}</p>
    `;
  }

  function showMatch(match) {
    const result = match.result || {};
    const list = items => items?.length
      ? `<ul>${items.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
      : `<p class="resume-empty-value">No skills identified</p>`;
    matchOutput.innerHTML = `
      <div class="match-score-row"><strong>${Math.round(result.match_percentage || 0)}%</strong><span>estimated role match<br><small>${escapeHtml(match.title)}</small></span></div>
      <div class="match-bar"><span style="width:${Math.max(0, Math.min(100, Number(result.match_percentage || 0)))}%"></span></div>
      <div class="match-breakdown"><span>Skills ${Math.round(result.skill_match_percentage || 0)}%</span><span>Experience ${Math.round(result.experience_relevance_percentage || 0)}%</span></div>
      <div class="resume-analysis-grid"><section><h3>Matching skills</h3>${list(result.matching_skills)}</section><section><h3>Missing skills</h3>${list(result.missing_skills)}</section><section><h3>Preparation topics</h3>${list(result.recommended_preparation_topics)}</section></div>
      <p class="resume-summary">${escapeHtml(result.method || "")}</p>
    `;
  }

  async function loadResumes(selectedId) {
    const data = await api("/resumes");
    savedResumes = data.resumes || [];
    resumeSelect.innerHTML = `<option value="">Choose a saved resume</option>${savedResumes.map(resume => `<option value="${resume.id}">${escapeHtml(resume.filename)}</option>`).join("")}`;
    if (selectedId) resumeSelect.value = String(selectedId);
    resumeList.innerHTML = savedResumes.length
      ? savedResumes.map(resume => `<div class="resume-list-row"><div><strong>${escapeHtml(resume.filename)}</strong><span>${new Date(resume.created_at).toLocaleDateString()} · ${Math.round(resume.analysis.resume_score || 0)}% completeness</span></div><button class="btn btn-secondary" type="button" data-select-resume="${resume.id}">Review</button></div>`).join("")
      : `<p class="resume-empty">No resumes analyzed yet.</p>`;
    resumeList.querySelectorAll("[data-select-resume]").forEach(button => {
      button.onclick = () => {
        const selected = savedResumes.find(resume => resume.id === Number(button.dataset.selectResume));
        if (!selected) return;
        resumeSelect.value = String(selected.id);
        showResume(selected);
        matchOutput.innerHTML = "";
      };
    });
    if (selectedId) {
      const selected = savedResumes.find(resume => resume.id === Number(selectedId));
      if (selected) showResume(selected);
    }
  }

  resumeForm.onsubmit = async event => {
    event.preventDefault();
    const button = document.getElementById("resumeUploadButton");
    button.disabled = true;
    button.textContent = "Extracting and analyzing...";
    resumeOutput.innerHTML = `<p class="loading">Reading resume content...</p>`;
    try {
      const data = await api("/resumes/upload", { method: "POST", body: new FormData(resumeForm) });
      await loadResumes(data.resume.id);
      toast("Resume analysis saved.");
    } catch (err) {
      resumeOutput.innerHTML = `<p class="resume-error">${escapeHtml(err.message)}</p>`;
    } finally {
      button.disabled = false;
      button.innerHTML = 'Analyze resume <span aria-hidden="true">↗</span>';
    }
  };

  document.getElementById("jobDescriptionFile").onchange = async event => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > 50000) {
      toast("Job description text files must be 50 KB or smaller.");
      event.target.value = "";
      return;
    }
    document.getElementById("jobDescription").value = await file.text();
  };

  document.getElementById("jobMatchForm").onsubmit = async event => {
    event.preventDefault();
    const resumeId = resumeSelect.value;
    if (!resumeId) return toast("Analyze or choose a resume first.");
    const button = document.getElementById("jobMatchButton");
    button.disabled = true;
    button.textContent = "Comparing skills...";
    try {
      const data = await api(`/resumes/${resumeId}/match`, {
        method: "POST",
        body: JSON.stringify({
          title: document.getElementById("jobTitle").value.trim(),
          description: document.getElementById("jobDescription").value.trim(),
        }),
      });
      showMatch(data.match);
      await loadResumes(resumeId);
    } catch (err) {
      matchOutput.innerHTML = `<p class="resume-error">${escapeHtml(err.message)}</p>`;
    } finally {
      button.disabled = false;
      button.innerHTML = 'Compare with resume <span aria-hidden="true">↗</span>';
    }
  };

  loadResumes().catch(err => {
    resumeList.innerHTML = `<p class="resume-error">${escapeHtml(err.message)}</p>`;
    resumeSelect.innerHTML = `<option value="">Could not load resumes</option>`;
  });
}

async function studyPlanPage() {
  if (!loggedIn()) return location.hash = "#login";
  if (isAdmin()) return location.hash = "#admin";

  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="page-title">
        <h1>Your study plan</h1>
        <p>Turn interview feedback into small, trackable practice steps.</p>
      </div>
      <div class="study-toolbar">
        <label for="studyPlanHistory">Plan history</label>
        <select class="input" id="studyPlanHistory"><option value="">Loading plans...</option></select>
        <button class="btn btn-primary" id="generateStudyPlan">Generate a 7-day plan <span aria-hidden="true">↗</span></button>
      </div>
      <section id="studyPlanOutput" class="study-plan-output"><div class="loading">Loading your study plans...</div></section>
    </main>
  `;

  const historySelect = document.getElementById("studyPlanHistory");
  const output = document.getElementById("studyPlanOutput");
  let plans = [];

  function renderPlan(plan) {
    if (!plan) {
      output.innerHTML = `<div class="study-empty"><span class="section-eyebrow">START SMALL</span><h2>No plan yet</h2><p>Generate a plan from your recent interview feedback and resume analysis, or start with a general interview-preparation path.</p></div>`;
      return;
    }
    output.innerHTML = `
      <div class="study-progress-header"><div><span class="section-eyebrow">PERSONALIZED ROUTE</span><h2>${escapeHtml(plan.title)}</h2><p>${escapeHtml(plan.source)}</p></div><strong>${plan.progress_percent}%<small> complete</small></strong></div>
      <div class="progress study-progress"><div style="width:${Math.max(0, Math.min(100, plan.progress_percent))}%"></div></div>
      <div class="study-task-list">${plan.tasks.map(task => `
        <article class="study-task ${task.completed ? "is-complete" : ""}">
          <label class="study-task-check"><input type="checkbox" data-task-day="${task.day}" ${task.completed ? "checked" : ""}><span>Day ${task.day}</span></label>
          <div class="study-task-content"><h3>${escapeHtml(task.topic)}</h3><p>${escapeHtml(task.objective)}</p>${task.resource_url ? `<a href="${escapeHtml(task.resource_url)}" target="_blank" rel="noopener noreferrer">Open recommended resource <span aria-hidden="true">↗</span></a>` : `<small class="study-no-resource">Use your interview report and course notes as a starting point.</small>`}</div>
        </article>
      `).join("")}</div>
    `;
    output.querySelectorAll("[data-task-day]").forEach(checkbox => {
      checkbox.onchange = async () => {
        checkbox.disabled = true;
        try {
          const data = await api(`/study-plans/${plan.id}/tasks/${checkbox.dataset.taskDay}`, {
            method: "PATCH",
            body: JSON.stringify({ completed: checkbox.checked }),
          });
          renderPlan(data.plan);
        } catch (err) {
          toast(err.message);
          checkbox.checked = !checkbox.checked;
          checkbox.disabled = false;
        }
      };
    });
  }

  async function loadPlans(selectedId) {
    const data = await api("/study-plans");
    plans = data.plans || [];
    historySelect.innerHTML = plans.length
      ? plans.map(plan => `<option value="${plan.id}">${escapeHtml(plan.title)} · ${new Date(plan.created_at).toLocaleDateString()}</option>`).join("")
      : `<option value="">No saved plans</option>`;
    const selected = plans.find(plan => plan.id === Number(selectedId)) || plans[0];
    if (selected) historySelect.value = String(selected.id);
    renderPlan(selected);
  }

  historySelect.onchange = () => {
    renderPlan(plans.find(plan => plan.id === Number(historySelect.value)));
  };

  document.getElementById("generateStudyPlan").onclick = async event => {
    const button = event.currentTarget;
    button.disabled = true;
    button.textContent = "Building your plan...";
    try {
      const data = await api("/study-plans/generate", { method: "POST", body: JSON.stringify({}) });
      await loadPlans(data.plan.id);
      toast("Study plan created.");
    } catch (err) {
      toast(err.message);
    } finally {
      button.disabled = false;
      button.innerHTML = 'Generate a 7-day plan <span aria-hidden="true">↗</span>';
    }
  };

  loadPlans().catch(err => {
    output.innerHTML = `<p class="resume-error">${escapeHtml(err.message)}</p>`;
  });
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
          <div class="form-group">
            <label for="technology">Technology or skill focus</label>
            <input class="input" id="technology" maxlength="120" placeholder="e.g. Python, React, SQL">
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
              <option value="expert">Expert</option>
            </select>
          </div>
          <div class="form-group">
            <label for="experienceLevel">Experience level</label>
            <select class="input" id="experienceLevel">
              <option value="student">Student</option>
              <option value="entry">Entry level</option>
              <option value="junior">Junior</option>
              <option value="intermediate" selected>Intermediate</option>
              <option value="senior">Senior</option>
            </select>
          </div>
          <div class="form-group">
            <label>Number of questions</label>
            <select class="input" id="questionCount">
              <option>5</option><option>7</option><option>10</option>
            </select>
          </div>
          <label class="adaptive-toggle" for="adaptiveInterview">
            <input id="adaptiveInterview" type="checkbox">
            <span><strong>Adaptive interview</strong><small>Questions respond to your previous answers.</small></span>
          </label>
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
          question_count: Number(document.getElementById("questionCount").value),
          experience_level: document.getElementById("experienceLevel").value,
          technology: document.getElementById("technology").value.trim(),
          adaptive: document.getElementById("adaptiveInterview").checked
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

  app.innerHTML = `${nav()}<main class="container page"><div class="loading">Restoring your interview...</div></main>`;

  let interviewState;
  try {
    interviewState = await api(`/interview/${saved.interview_id}`);
  } catch (err) {
    toast(err.message);
    location.hash = "#dashboard";
    return;
  }

  if (interviewState.status === "completed") {
    location.hash = `#result/${saved.interview_id}`;
    return;
  }

  let questions = interviewState.questions || [];
  let index = questions.findIndex(question => !question.answer);
  if (index < 0 && questions.length) {
    await api(`/interview/${saved.interview_id}/finish`, { method: "POST" });
    location.hash = `#result/${saved.interview_id}`;
    return;
  }
  if (!questions.length) return location.hash = "#setup";
  sessionStorage.setItem("question_index", index);
  const targetCount = Number(interviewState.question_count || saved.question_count || questions.length);

  app.innerHTML = `
    ${nav()}
    <main class="container page">
      <div class="interview-layout">
        <aside class="card sidebar-card">
          <div class="question-number" id="progressText"></div>
          <div class="progress" style="margin:10px 0 20px"><div id="progressBar"></div></div>
          <div class="interview-meta">
            <span class="chip">${escapeHtml(interviewState.job_role)}</span>
            <span class="chip">${escapeHtml(interviewState.difficulty)}</span>
            <span class="chip">${escapeHtml(interviewState.experience_level)}</span>
            ${interviewState.technology ? `<span class="chip">${escapeHtml(interviewState.technology)}</span>` : ""}
            ${interviewState.adaptive ? '<span class="chip adaptive-chip">Adaptive</span>' : ""}
          </div>
          <hr style="border:0;border-top:1px solid var(--border);margin:22px 0">
          <p style="color:var(--muted);font-size:13px;line-height:1.7">
            Tip: Structure your answer clearly. Explain the concept, give an example,
            and mention the result when possible.
          </p>
        </aside>

        <section class="card">
          <div class="question-number" id="questionNo"></div>
          <div class="question-timer" id="questionTimer" role="timer" aria-label="Time on current question">00:00</div>
          <div class="question-text" id="questionText"></div>
          <div class="voice-actions">
            <button class="btn btn-secondary" id="speakBtn" type="button">🔊 Hear question</button>
            <button class="btn btn-secondary" id="listenBtn" type="button">🎙️ Answer by voice</button>
            <button class="btn btn-secondary hidden" id="stopListenBtn" type="button">⏹ Stop listening</button>
          </div>
          <p class="voice-status" id="voiceStatus" role="status">Voice interview is ready.</p>
          <textarea id="answer" class="input" placeholder="Type your answer here..."></textarea>
          <div class="answer-actions">
            <button class="btn btn-secondary" id="backBtn">← Back</button>
            <button class="btn btn-primary" id="nextBtn">Submit & Continue →</button>
          </div>
        </section>
      </div>
    </main>
  `;

  const questionNo = document.getElementById("questionNo");
  const questionText = document.getElementById("questionText");
  const progressText = document.getElementById("progressText");
  const progressBar = document.getElementById("progressBar");
  const answer = document.getElementById("answer");
  const backBtn = document.getElementById("backBtn");
  const nextBtn = document.getElementById("nextBtn");
  const speakBtn = document.getElementById("speakBtn");
  const listenBtn = document.getElementById("listenBtn");
  const stopListenBtn = document.getElementById("stopListenBtn");
  const voiceStatus = document.getElementById("voiceStatus");
  const questionTimer = document.getElementById("questionTimer");
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;
  let isListening = false;
  let questionStartedAt = Date.now();
  let speechStartedAt = null;
  let speechDurationSeconds = 0;
  let spokenWordCount = 0;
  let fillerWordCount = 0;

  if (interviewTimer !== null) clearInterval(interviewTimer);
  interviewTimer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - questionStartedAt) / 1000);
    questionTimer.textContent = `${String(Math.floor(elapsed / 60)).padStart(2, "0")}:${String(elapsed % 60).padStart(2, "0")}`;
  }, 1000);

  function speakQuestion() {
    if (!window.speechSynthesis) {
      voiceStatus.textContent = "Text-to-speech is not supported in this browser.";
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(questionText.textContent);
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
    voiceStatus.textContent = "Playing the question...";
  }

  function stopListening() {
    if (recognition && isListening) recognition.stop();
    if (speechStartedAt !== null) {
      speechDurationSeconds += (Date.now() - speechStartedAt) / 1000;
      speechStartedAt = null;
    }
    isListening = false;
    listenBtn.classList.remove("hidden");
    stopListenBtn.classList.add("hidden");
  }

  if (recognition) {
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.onstart = () => {
      isListening = true;
      speechStartedAt = Date.now();
      listenBtn.classList.add("hidden");
      stopListenBtn.classList.remove("hidden");
      voiceStatus.textContent = "Listening... speak your answer clearly.";
    };
    recognition.onresult = event => {
      const transcript = Array.from(event.results)
        .slice(event.resultIndex)
        .map(result => result[0].transcript)
        .join("");
      answer.value += `${answer.value && !answer.value.endsWith(" ") ? " " : ""}${transcript}`;
      spokenWordCount += transcript.trim().split(/\s+/).filter(Boolean).length;
      fillerWordCount += (transcript.match(/\b(?:um|uh|like|actually|basically)\b/gi) || []).length;
      sessionStorage.setItem(`draft_answer_${questions[index].id}`, answer.value);
    };
    recognition.onerror = event => {
      voiceStatus.textContent = event.error === "not-allowed"
        ? "Microphone permission was denied. You can type your answer instead."
        : `Voice input error: ${event.error}.`;
      stopListening();
    };
    recognition.onend = () => {
      if (isListening) voiceStatus.textContent = "Voice input paused.";
      stopListening();
    };
  } else {
    listenBtn.disabled = true;
    listenBtn.title = "Voice input is not supported in this browser";
    voiceStatus.textContent = "Voice input is unavailable here. You can type your answer instead.";
  }

  speakBtn.onclick = speakQuestion;
  listenBtn.onclick = () => {
    if (!recognition) return;
    answer.focus();
    recognition.start();
  };
  stopListenBtn.onclick = stopListening;

  async function showQuestion() {
    const q = questions[index];
    stopListening();
    window.speechSynthesis?.cancel();
    questionNo.textContent = `Question ${index + 1}`;
    questionText.textContent = q.question;
    progressText.textContent = `${index + 1} of ${targetCount}`;
    progressBar.style.width = `${((index + 1) / targetCount) * 100}%`;
    questionStartedAt = Date.now();
    speechStartedAt = null;
    speechDurationSeconds = 0;
    spokenWordCount = 0;
    fillerWordCount = 0;
    questionTimer.textContent = "00:00";
    answer.value = sessionStorage.getItem(`draft_answer_${q.id}`) || q.answer || "";
    backBtn.disabled = index === 0;
    nextBtn.textContent = index === targetCount - 1 ? "Submit & Finish ✓" : "Submit & Continue →";
  }

  answer.oninput = () => {
    sessionStorage.setItem(`draft_answer_${questions[index].id}`, answer.value);
  };

  backBtn.onclick = () => {
    if (index > 0) {
      sessionStorage.setItem(`draft_answer_${questions[index].id}`, answer.value);
      index--;
      sessionStorage.setItem("question_index", index);
      showQuestion();
    }
  };

  nextBtn.onclick = async () => {
    const q = questions[index];
    const text = answer.value.trim();
    if (!text) return toast("Please enter an answer first.");
    stopListening();

    nextBtn.disabled = true;
    nextBtn.textContent = "AI is analyzing...";

    try {
      const data = await api(`/interview/${saved.interview_id}/answer`, {
        method: "POST",
        body: JSON.stringify({
          question_id: q.id,
          answer: text,
          time_taken_seconds: Math.floor((Date.now() - questionStartedAt) / 1000),
          speech_duration_seconds: Math.round(speechDurationSeconds),
          spoken_word_count: spokenWordCount,
          filler_word_count: fillerWordCount
        })
      });

      sessionStorage.removeItem(`draft_answer_${q.id}`);
      if (data.next_question) {
        questions.slice(index + 1).forEach(previousQuestion => {
          sessionStorage.removeItem(`draft_answer_${previousQuestion.id}`);
        });
        questions = questions.slice(0, index + 1);
        questions.push(data.next_question);
      }

      const shouldFinish = interviewState.adaptive ? data.complete : index === questions.length - 1;
      if (shouldFinish) {
        const completion = await api(`/interview/${saved.interview_id}/finish`, { method: "POST" });
        if (completion.notifications?.length) toast(completion.notifications[0]);
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
    const averageScore = field => {
      const scores = (data.questions || []).map(question => Number(question[field] || 0));
      return scores.length ? Math.round(scores.reduce((total, value) => total + value, 0) / scores.length) : 0;
    };

    app.innerHTML = `
      ${nav()}
      <main class="container page">
        <div class="page-title">
          <h1>Interview Report 🎯</h1>
          <p>${escapeHtml(data.job_role)} · ${escapeHtml(data.experience_level)} · ${escapeHtml(data.difficulty)} difficulty${data.technology ? ` · ${escapeHtml(data.technology)}` : ""}${data.adaptive ? " · Adaptive" : ""}</p>
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
            <button class="btn btn-secondary" id="downloadReportBtn" type="button">Download PDF</button>
          </div>
        </section>

        <div class="metric-grid">
          ${[
            ["Technical", "technical_score"],
            ["Accuracy", "accuracy_score"],
            ["Relevance", "relevance_score"],
            ["Communication", "communication_score"],
            ["Confidence", "confidence_score"],
            ["Clarity", "clarity_score"],
            ["Completeness", "completeness_score"]
          ].map(([label, field]) => `<div class="metric"><small>${label}</small><strong>${averageScore(field)}%</strong></div>`).join("")}
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
              <p><b>Suggested answer:</b> ${escapeHtml(q.suggested_answer || "")}</p>
              <p><small>Question difficulty: ${escapeHtml(q.difficulty)} · Time: ${Math.round(q.time_taken_seconds || 0)} sec · ${q.spoken_word_count ? `${q.spoken_word_count} spoken words · ${Math.round(q.words_per_minute || 0)} WPM · ${q.filler_word_count} filler words` : "Typed response"}</small></p>
            </div>
          `).join("")}
        </section>
      </main>
    `;

    document.getElementById("downloadReportBtn").onclick = async event => {
      const button = event.currentTarget;
      button.disabled = true;
      button.textContent = "Preparing PDF...";
      try {
        await downloadFile(`/interview/${id}/report.pdf`, `interview-report-${id}.pdf`);
      } catch (err) {
        toast(err.message);
      } finally {
        button.disabled = false;
        button.textContent = "Download PDF";
      }
    };
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
          <p>Track your interview progress and keep improving.${data.improvement_points !== null ? ` Latest score moved ${data.improvement_points >= 0 ? "+" : ""}${data.improvement_points} points versus the previous interview.` : " Complete another interview to see your progress trend."}</p>
        </div>

        <div class="metric-grid">
          <div class="metric"><small>Total Interviews</small><strong>${data.total_interviews}</strong></div>
          <div class="metric"><small>Completed</small><strong>${data.completed_interviews}</strong></div>
          <div class="metric"><small>Average Score</small><strong>${data.average_score}%</strong></div>
          <div class="metric"><small>Best Score</small><strong>${data.best_score}%</strong></div>
          <div class="metric"><small>Technical Average</small><strong>${data.completed_interviews ? `${Math.round(data.category_averages.technical_score)}%` : "—"}</strong></div>
          <div class="metric"><small>Communication Average</small><strong>${data.completed_interviews ? `${Math.round(data.category_averages.communication_score)}%` : "—"}</strong></div>
          <div class="metric"><small>Interview Streak</small><strong>${data.interview_streak} days</strong></div>
        </div>

        <section class="achievement-section">
          <div class="achievement-heading"><div><span class="section-eyebrow">MILESTONES</span><h2>Achievements</h2></div></div>
          <div class="achievement-grid">${data.achievements.map(item => `<div class="achievement-badge ${item.unlocked ? "unlocked" : "locked"}" aria-label="${escapeHtml(item.title)}: ${item.unlocked ? "unlocked" : "locked"}"><span aria-hidden="true">${item.unlocked ? "✦" : "○"}</span><div><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.description)}</small></div></div>`).join("")}</div>
        </section>

        <div class="dashboard-analytics">
          <section class="analytics-panel">
            <div class="analytics-heading"><div><span class="section-eyebrow">SCORE HISTORY</span><h2>Performance over time</h2></div></div>
            ${data.performance_over_time.length ? `<div class="trend-chart" role="img" aria-label="Interview scores over time">${data.performance_over_time.map(item => `<div class="trend-column" title="${escapeHtml(item.job_role)} · ${item.score}% · ${escapeHtml(item.date)}"><strong>${Math.round(item.score)}</strong><span class="trend-bar" style="height:${Math.max(4, Math.min(100, item.score))}%"></span><small>${escapeHtml(item.date.slice(5))}</small></div>`).join("")}</div>` : `<p class="analytics-empty">Completed interview scores will appear here.</p>`}
          </section>
          <section class="analytics-panel">
            <div class="analytics-heading"><div><span class="section-eyebrow">BY ROLE</span><h2>Role performance</h2></div></div>
            ${data.role_performance.length ? `<div class="role-chart">${data.role_performance.map(item => `<div class="role-chart-row"><div><strong>${escapeHtml(item.job_role)}</strong><span>${item.interviews} interview${item.interviews === 1 ? "" : "s"}</span></div><strong>${Math.round(item.average_score)}%</strong><i><b style="width:${Math.max(0, Math.min(100, item.average_score))}%"></b></i></div>`).join("")}</div>` : `<p class="analytics-empty">Role comparisons will appear after an interview is completed.</p>`}
          </section>
          <section class="analytics-panel">
            <div class="analytics-heading"><div><span class="section-eyebrow">WHAT'S WORKING</span><h2>Strong topics</h2></div></div>
            ${data.strong_topics.length ? `<ul class="topic-list">${data.strong_topics.map(item => `<li><span>${escapeHtml(item.topic)}</span><small>${item.count} mention${item.count === 1 ? "" : "s"}</small></li>`).join("")}</ul>` : `<p class="analytics-empty">Strengths will appear after you submit answers.</p>`}
          </section>
          <section class="analytics-panel">
            <div class="analytics-heading"><div><span class="section-eyebrow">NEXT TO PRACTICE</span><h2>Growth topics</h2></div></div>
            ${data.weak_topics.length ? `<ul class="topic-list weak-topics">${data.weak_topics.map(item => `<li><span>${escapeHtml(item.topic)}</span><small>${item.count} mention${item.count === 1 ? "" : "s"}</small></li>`).join("")}</ul>` : `<p class="analytics-empty">Suggestions from your reports will appear here.</p>`}
          </section>
          <section class="analytics-panel">
            <div class="analytics-heading"><div><span class="section-eyebrow">VOICE PRACTICE</span><h2>Speaking metrics</h2></div></div>
            ${data.voice_metrics.spoken_words ? `<div class="voice-metric-row"><div><strong>${data.voice_metrics.words_per_minute}</strong><span>words per minute</span></div><div><strong>${data.voice_metrics.filler_words}</strong><span>filler words</span></div><div><strong>${data.voice_metrics.speaking_seconds}s</strong><span>speaking time</span></div></div>` : `<p class="analytics-empty">Use voice answers to see recognized words, filler words, and speaking pace.</p>`}
          </section>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;margin:30px 0 15px;gap:10px">
          <h2 style="margin:0">Interview History</h2>
          <div class="dashboard-actions">
            ${isAdmin() ? '<button class="btn btn-secondary" onclick="location.hash=\'#admin\'">⚙ Admin Panel</button>' : ''}
            <button class="btn btn-primary" onclick="location.hash='#setup'">+ New Interview</button>
          </div>
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

async function adminDashboard() {
  if (!loggedIn()) return location.hash = "#admin-login";
  if (!isAdmin()) {
    app.innerHTML = `${nav()}<main class="container page"><div class="card"><h2>Admin access error</h2><p>admin access required</p></div></main>`;
    return;
  }

  app.innerHTML = `${nav()}<main class="container page"><div class="loading">Loading admin panel...</div></main>`;

  try {
    const data = await api("/admin/overview");
    app.innerHTML = `
      ${nav()}
      <main class="container page">
        <div class="page-title">
          <h1>Admin Panel</h1>
          <p>Monitor candidates, interviews and platform performance.</p>
        </div>
        <div class="metric-grid">
          <div class="metric"><small>Total Users</small><strong>${data.stats.users}</strong></div>
          <div class="metric"><small>Total Interviews</small><strong>${data.stats.interviews}</strong></div>
          <div class="metric"><small>Completed</small><strong>${data.stats.completed_interviews}</strong></div>
          <div class="metric"><small>Average Score</small><strong>${data.stats.average_score}%</strong></div>
        </div>
        <section class="card admin-section">
          <h2>Users</h2>
          <div class="admin-table-wrap"><table class="admin-table">
            <thead><tr><th>Name</th><th>Email</th><th>Interviews</th><th>Joined</th><th></th></tr></thead>
            <tbody>${data.users.map(item => `
              <tr>
                <td>${escapeHtml(item.name)}</td><td>${escapeHtml(item.email)}</td>
                <td>${item.interviews}</td><td>${new Date(item.created_at).toLocaleDateString()}</td>
                <td><button class="btn btn-danger btn-small" data-delete-user="${item.id}">Delete</button></td>
              </tr>`).join("")}</tbody>
          </table></div>
        </section>
        <section class="card admin-section">
          <h2>Recent Interviews</h2>
          <div class="admin-table-wrap"><table class="admin-table">
            <thead><tr><th>Candidate</th><th>Role</th><th>Status</th><th>Score</th><th>Date</th></tr></thead>
            <tbody>${data.interviews.length ? data.interviews.map(item => `
              <tr><td>${escapeHtml(item.candidate)}<small>${escapeHtml(item.email)}</small></td>
              <td>${escapeHtml(item.job_role)}</td><td>${escapeHtml(item.status)}</td>
              <td>${Math.round(item.score || 0)}%</td><td>${new Date(item.created_at).toLocaleDateString()}</td></tr>
            `).join("") : `<tr><td colspan="5">No interviews yet.</td></tr>`}</tbody>
          </table></div>
        </section>
      </main>
    `;

    document.querySelectorAll("[data-delete-user]").forEach(button => {
      button.onclick = async () => {
        if (!window.confirm("Delete this user and their interviews?")) return;
        try {
          await api(`/admin/users/${button.dataset.deleteUser}`, { method: "DELETE" });
          toast("User deleted");
          adminDashboard();
        } catch (err) { toast(err.message); }
      };
    });
  } catch (err) {
    app.innerHTML = `${nav()}<main class="container page"><div class="card"><h2>Admin access error</h2><p>${escapeHtml(err.message)}</p></div></main>`;
  }
}

window.addEventListener("hashchange", render);
render();
