/**
 * InterviewAI - Frontend Application Logic
 * Integrates with Flask backend and AI Engine (Gemini / OpenAI / Groq / Offline)
 */

// Application State
const appState = {
  domain: "Artificial Intelligence & ML",
  jobRole: "Software Engineer",
  experienceLevel: "Mid-Level (2-4 yrs)",
  difficulty: "Medium",
  candidateName: "Candidate",
  sessionSize: 5,
  currentIndex: 1,
  currentQuestion: null,
  previousQuestions: [],
  sessionResults: [],
  
  // Timer State
  timerDuration: 150, // default 2.5 mins
  timerRemaining: 150,
  timerInterval: null,
  isTimerRunning: false,

  // Audio / Speech State
  voiceEnabled: true,
  isSpeaking: false,
  isRecording: false,
  recognition: null,

  // AI Config
  activeProvider: "gemini",
  activeModel: "gemini-2.5-flash"
};

// DOM Helper
const $ = (id) => document.getElementById(id);

// Navigation & View Switching
const views = document.querySelectorAll(".view");
const navItems = document.querySelectorAll(".nav-item");

function switchView(viewId) {
  views.forEach(v => v.classList.toggle("active", v.id === viewId));
  navItems.forEach(n => n.classList.toggle("active", n.dataset.view === viewId));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

navItems.forEach(item => {
  item.addEventListener("click", () => switchView(item.dataset.view));
});

// Mobile Sidebar Toggle
if ($("sidebarToggle")) {
  $("sidebarToggle").addEventListener("click", () => {
    document.querySelector(".sidebar").classList.toggle("open");
  });
}

// ============================================================================
// 1. AI MODEL CONFIGURATION & MODAL MANAGEMENT
// ============================================================================

const configModal = $("configModal");
const openSettingsBtns = [$("openSettingsBtn"), $("topSettingsBtn"), $("heroConfigBtn"), $("topbarModelPill")];

openSettingsBtns.forEach(btn => {
  if (btn) btn.addEventListener("click", () => openConfigModal());
});

if ($("closeModalBtn")) {
  $("closeModalBtn").addEventListener("click", () => closeConfigModal());
}

function openConfigModal() {
  configModal.classList.remove("hidden");
  $("testResultBox").classList.add("hidden");
}

function closeConfigModal() {
  configModal.classList.add("hidden");
}

// Close on outside click
configModal.addEventListener("click", (e) => {
  if (e.target === configModal) closeConfigModal();
});

// Provider selector toggles visible fields
$("aiProviderSelect").addEventListener("change", (e) => {
  const provider = e.target.value;
  $("geminiFields").classList.toggle("hidden", provider !== "gemini");
  $("openaiFields").classList.toggle("hidden", provider !== "openai");
  $("groqFields").classList.toggle("hidden", provider !== "groq");
  $("offlineFields").classList.toggle("hidden", provider !== "offline");
});

// Show/Hide password toggle
document.querySelectorAll(".toggle-pw-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const targetInput = $(btn.dataset.target);
    if (targetInput.type === "password") {
      targetInput.type = "text";
      btn.textContent = "🔒";
    } else {
      targetInput.type = "password";
      btn.textContent = "👁";
    }
  });
});

// Load config from server
async function loadConfig() {
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    appState.activeProvider = data.active_provider;
    
    // Update labels
    updateModelBadges(data);

    $("aiProviderSelect").value = data.active_provider;
    $("aiProviderSelect").dispatchEvent(new Event("change"));

    if (data.models) {
      if (data.models.gemini) $("geminiModelSelect").value = data.models.gemini;
      if (data.models.openai) $("openaiModelSelect").value = data.models.openai;
      if (data.models.groq) $("groqModelSelect").value = data.models.groq;
    }
  } catch (err) {
    console.error("Failed to load AI config:", err);
  }
}

function updateModelBadges(data) {
  const provider = data.active_provider || appState.activeProvider;
  let label = "Offline Smart Engine";
  let fullLabel = "Built-in Heuristic Engine";

  if (provider === "gemini") {
    const model = data.models ? data.models.gemini : "gemini-2.5-flash";
    label = `Gemini (${model.replace("gemini-", "")})`;
    fullLabel = `Google Gemini (${model})`;
  } else if (provider === "openai") {
    const model = data.models ? data.models.openai : "gpt-4o-mini";
    label = `OpenAI (${model})`;
    fullLabel = `OpenAI (${model})`;
  } else if (provider === "groq") {
    label = `Groq (Llama 3.3)`;
    fullLabel = `Groq Cloud (Llama 3.3 70B)`;
  }

  $("topbarModelLabel").textContent = label;
  $("sideModelName").textContent = fullLabel;
  $("sideModelProvider").textContent = provider === "offline" ? "OFFLINE SMART ENGINE" : "ACTIVE AI MODEL";
  
  if ($("evalEngineSource")) {
    $("evalEngineSource").textContent = `Evaluated by ${fullLabel}`;
  }
}

// Test Connection
$("testConnectionBtn").addEventListener("click", async () => {
  const provider = $("aiProviderSelect").value;
  const resultBox = $("testResultBox");
  resultBox.className = "test-result-box";
  resultBox.innerHTML = `Testing connection to ${provider}...`;
  resultBox.classList.remove("hidden");

  let apiKey = "";
  let model = "";

  if (provider === "gemini") {
    apiKey = $("geminiApiKeyInput").value;
    model = $("geminiModelSelect").value;
  } else if (provider === "openai") {
    apiKey = $("openaiApiKeyInput").value;
    model = $("openaiModelSelect").value;
  } else if (provider === "groq") {
    apiKey = $("groqApiKeyInput").value;
    model = $("groqModelSelect").value;
  }

  try {
    const res = await fetch("/api/test-connection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, api_key: apiKey, model })
    });
    const result = await res.json();

    if (result.success) {
      resultBox.classList.add("success");
      resultBox.innerHTML = `✓ <strong>Connected!</strong> ${result.message} <small>(${result.latency_ms}ms)</small>`;
    } else {
      resultBox.classList.add("error");
      resultBox.innerHTML = `❌ <strong>Connection Error:</strong> ${result.message}`;
    }
  } catch (err) {
    resultBox.classList.add("error");
    resultBox.innerHTML = `❌ Network error while contacting server.`;
  }
});

// Save & Apply Settings
$("saveConfigBtn").addEventListener("click", async () => {
  const provider = $("aiProviderSelect").value;
  const payload = { provider };

  if (provider === "gemini") {
    payload.gemini_api_key = $("geminiApiKeyInput").value;
    payload.gemini_model = $("geminiModelSelect").value;
  } else if (provider === "openai") {
    payload.openai_api_key = $("openaiApiKeyInput").value;
    payload.openai_model = $("openaiModelSelect").value;
  } else if (provider === "groq") {
    payload.groq_api_key = $("groqApiKeyInput").value;
    payload.groq_model = $("groqModelSelect").value;
  }

  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      updateModelBadges(data.config);
      showToast(`AI Model configuration saved (${provider})!`);
      closeConfigModal();
    }
  } catch (err) {
    showToast("Failed to save settings.");
  }
});

// ============================================================================
// 2. DOMAINS & TRACKS MANAGEMENT
// ============================================================================

async function loadDomains() {
  try {
    const res = await fetch("/api/domains");
    const domains = await res.json();

    // Populate Domain Selector in Sidebar
    $("domainSelect").innerHTML = domains.map(d => `<option value="${d.id}">${d.name}</option>`).join("");
    
    // Populate Dashboard Tracks (Top 4)
    $("dashboardTracksGrid").innerHTML = domains.slice(0, 4).map(d => `
      <div class="track-card" data-domain="${d.id}" data-name="${d.name}">
        <div class="track-icon">${d.icon}</div>
        <h3>${d.name}</h3>
        <p>${d.description}</p>
        <div class="track-footer">
          <span class="track-badge">PRACTICE DRILL</span>
          <span class="track-action">Start Track →</span>
        </div>
      </div>
    `).join("");

    // Populate Full Domains View
    $("fullDomainsGrid").innerHTML = domains.map(d => `
      <div class="domain-card" data-domain="${d.id}" data-name="${d.name}">
        <div class="domain-icon">${d.icon}</div>
        <h3>${d.name}</h3>
        <p>${d.description}</p>
        <button class="primary-btn w-100 start-domain-btn" data-domain="${d.id}">Start Interview Drill</button>
      </div>
    `).join("");

    // Click handlers for track cards
    document.querySelectorAll(".track-card, .domain-card").forEach(card => {
      card.addEventListener("click", (e) => {
        const domainId = card.dataset.domain;
        if (domainId) {
          $("domainSelect").value = domainId;
          appState.domain = domainId;
          updateTopbarInfo();
          switchView("interview");
          startSession();
        }
      });
    });

  } catch (err) {
    console.error("Failed to load domains:", err);
  }
}

function updateTopbarInfo() {
  const selectedOpt = $("domainSelect").options[$("domainSelect").selectedIndex];
  const domainText = selectedOpt ? selectedOpt.text : appState.domain;
  $("topbarDomain").textContent = domainText;
  $("topbarRole").textContent = $("jobRoleInput").value || "Software Engineer";
}

$("domainSelect").addEventListener("change", () => {
  appState.domain = $("domainSelect").value;
  updateTopbarInfo();
});

$("jobRoleInput").addEventListener("input", updateTopbarInfo);

// ============================================================================
// 3. LIVE INTERVIEW SESSION LOGIC
// ============================================================================

async function startSession() {
  // Read inputs from setup drawer
  appState.candidateName = $("candidateNameInput").value.trim() || "Candidate";
  appState.domain = $("domainSelect").value;
  appState.jobRole = $("jobRoleInput").value.trim() || "Software Engineer";
  appState.experienceLevel = $("experienceLevelSelect").value;
  appState.difficulty = $("difficultySelect").value;
  appState.sessionSize = parseInt($("sessionSizeSelect").value, 10) || 5;
  appState.timerDuration = parseInt($("timerSettingSelect").value, 10);
  
  appState.currentIndex = 1;
  appState.sessionResults = [];
  appState.previousQuestions = [];

  updateTopbarInfo();
  await loadNextQuestion();
}

async function loadNextQuestion() {
  // Update UI trackers
  $("qCurrent").textContent = appState.currentIndex;
  $("qTotal").textContent = appState.sessionSize;
  $("domainBadge").textContent = appState.domain.toUpperCase();
  $("difficultyBadge").textContent = appState.difficulty.toUpperCase();
  
  // Clear answer input & hide evaluation
  $("answerInput").value = "";
  $("wordCount").textContent = "0";
  $("charCount").textContent = "0";
  $("answerStatus").textContent = "Drafting answer...";
  $("evaluationCard").classList.add("hidden");
  $("followUpCard").classList.add("hidden");
  $("hintsBox").classList.remove("hidden");
  $("hintContent").classList.add("hidden");
  $("hintArrow").textContent = "▼";
  
  $("questionText").innerHTML = `<span style="opacity:0.6">AI Model is synthesizing question...</span>`;

  try {
    const res = await fetch("/api/question", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        domain: appState.domain,
        experience_level: appState.experienceLevel,
        difficulty: appState.difficulty,
        job_role: appState.jobRole,
        previous_questions: appState.previousQuestions
      })
    });
    const qData = await res.json();
    appState.currentQuestion = qData;
    appState.previousQuestions.push(qData.q);

    $("questionText").textContent = qData.q;
    $("typeBadge").textContent = (qData.type || "TECHNICAL").toUpperCase();
    
    // Hints
    if (qData.hints && qData.hints.length) {
      $("hintText").textContent = qData.hints[0];
    }
    if (qData.expected_key_points && qData.expected_key_points.length) {
      $("expectedPointsTags").innerHTML = qData.expected_key_points.map(pt => 
        `<span class="kp-tag"># ${pt}</span>`
      ).join("");
    } else {
      $("expectedPointsTags").innerHTML = "";
    }

    // Start timer
    startTimer();

    // Text-to-speech if enabled
    if (appState.voiceEnabled) {
      speakQuestion(qData.q);
    }

  } catch (err) {
    $("questionText").textContent = "Could not load question. Please try again.";
    console.error(err);
  }
}

// Hint accordion toggle
$("hintToggleBtn").addEventListener("click", () => {
  const content = $("hintContent");
  const arrow = $("hintArrow");
  const isHidden = content.classList.contains("hidden");
  content.classList.toggle("hidden");
  arrow.textContent = isHidden ? "▲" : "▼";
});

// Ideal Answer accordion toggle
$("idealToggleBtn").addEventListener("click", () => {
  const content = $("idealContent");
  const arrow = $("idealArrow");
  const isHidden = content.classList.contains("hidden");
  content.classList.toggle("hidden");
  arrow.textContent = isHidden ? "▲" : "▼";
});

// Textarea live counters
$("answerInput").addEventListener("input", (e) => {
  const text = e.target.value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  $("wordCount").textContent = words;
  $("charCount").textContent = text.length;

  if (words > 80) {
    $("answerStatus").textContent = "Great detail! Review your explanation before submitting.";
  } else if (words > 30) {
    $("answerStatus").textContent = "Good length. Consider adding an example or trade-off.";
  } else {
    $("answerStatus").textContent = "Drafting answer...";
  }
});

// ============================================================================
// 4. SUBMIT ANSWER & EVALUATION
// ============================================================================

$("submitAnswerBtn").addEventListener("click", async () => {
  const answer = $("answerInput").value.trim();
  if (!answer) {
    showToast("Please provide an answer before submitting.");
    $("answerInput").focus();
    return;
  }

  // Show loading state
  $("submitBtnText").textContent = "AI Model Evaluating...";
  $("evalSpinner").classList.remove("hidden");
  $("submitAnswerBtn").disabled = true;
  stopTimer();

  try {
    const res = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: appState.currentQuestion.q,
        answer: answer,
        domain: appState.domain,
        experience_level: appState.experienceLevel
      })
    });
    const evalData = await res.json();

    // Save to session history
    appState.sessionResults.push({
      question: appState.currentQuestion.q,
      answer: answer,
      score: evalData.overall,
      accuracy: evalData.accuracy,
      relevance: evalData.relevance,
      communication: evalData.communication,
      technical_depth: evalData.technical_depth,
      feedback: evalData.feedback,
      strengths: evalData.strengths || [],
      improvements: evalData.improvements || [],
      model_answer: evalData.ideal_answer || "",
      source: evalData.source
    });

    displayEvaluationResult(evalData);

  } catch (err) {
    showToast("Error communicating with AI Evaluator.");
    console.error(err);
  } finally {
    $("submitBtnText").textContent = "Submit for AI Evaluation →";
    $("evalSpinner").classList.add("hidden");
    $("submitAnswerBtn").disabled = false;
  }
});

function displayEvaluationResult(data) {
  const card = $("evaluationCard");
  card.classList.remove("hidden");

  // Overall Score
  $("evalOverallScore").textContent = data.overall.toFixed(1);
  
  // 4 Criteria Bars
  $("scoreAccuracy").textContent = `${data.accuracy}/10`;
  $("barAccuracy").style.width = `${data.accuracy * 10}%`;

  $("scoreRelevance").textContent = `${data.relevance}/10`;
  $("barRelevance").style.width = `${data.relevance * 10}%`;

  $("scoreTechDepth").textContent = `${data.technical_depth}/10`;
  $("barTechDepth").style.width = `${data.technical_depth * 10}%`;

  $("scoreCommunication").textContent = `${data.communication}/10`;
  $("barCommunication").style.width = `${data.communication * 10}%`;

  // Feedback Text
  $("evalFeedbackText").textContent = data.feedback;

  // Strengths List
  $("evalStrengthsList").innerHTML = (data.strengths && data.strengths.length) 
    ? data.strengths.map(s => `<li>${s}</li>`).join("")
    : `<li>Addressed the core topic promptly.</li>`;

  // Improvements List
  $("evalImprovementsList").innerHTML = (data.improvements && data.improvements.length)
    ? data.improvements.map(i => `<li>${i}</li>`).join("")
    : `<li>Incorporate a concrete engineering example and discuss trade-offs.</li>`;

  // Missing Points
  const missingBox = $("missingConceptsBox");
  if (data.missing_points && data.missing_points.length) {
    missingBox.classList.remove("hidden");
    $("missingConceptsTags").innerHTML = data.missing_points.map(mp => 
      `<span class="missing-tag">${mp}</span>`
    ).join("");
  } else {
    missingBox.classList.add("hidden");
  }

  // Ideal Model Answer
  if (data.ideal_answer) {
    $("idealAnswerText").textContent = data.ideal_answer;
  }

  // Follow-up question
  if (data.follow_up_question) {
    $("followUpCard").classList.remove("hidden");
    $("followUpText").textContent = data.follow_up_question;
    $("followUpInput").value = "";
    $("followUpFeedback").classList.add("hidden");
  } else {
    $("followUpCard").classList.add("hidden");
  }

  // Scroll to evaluation
  card.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Follow-up answer handler
$("submitFollowUpBtn").addEventListener("click", () => {
  const text = $("followUpInput").value.trim();
  if (!text) {
    showToast("Please write a quick response to the follow-up.");
    return;
  }
  const fb = $("followUpFeedback");
  fb.classList.remove("hidden");
  fb.innerHTML = `✓ <strong>Follow-up recorded!</strong> Great initiative elaborating on your answer.`;
  showToast("Follow-up response recorded!");
});

// Refine & Retry answer
$("retryAnswerBtn").addEventListener("click", () => {
  $("evaluationCard").classList.add("hidden");
  $("answerInput").focus();
  window.scrollTo({ top: $("answerInput").offsetTop - 100, behavior: "smooth" });
});

// Next Question
$("nextQuestionBtn").addEventListener("click", async () => {
  if (appState.currentIndex >= appState.sessionSize) {
    await finishSession();
  } else {
    appState.currentIndex++;
    await loadNextQuestion();
  }
});

// Skip Question
$("skipQuestionBtn").addEventListener("click", async () => {
  if (appState.currentIndex >= appState.sessionSize) {
    await finishSession();
  } else {
    appState.currentIndex++;
    await loadNextQuestion();
  }
});

// New / Restart Session Buttons
$("restartSessionBtn").addEventListener("click", startSession);
$("heroStartBtn").addEventListener("click", () => {
  switchView("interview");
  startSession();
});
$("reportNewSessionBtn").addEventListener("click", () => {
  switchView("interview");
  startSession();
});

// ============================================================================
// 5. FINISH SESSION & GENERATE REPORT
// ============================================================================

async function finishSession() {
  switchView("report");
  showToast("Synthesizing comprehensive AI Performance Report...");

  try {
    const res = await fetch("/api/session-summary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_name: appState.candidateName,
        domain: appState.domain,
        experience_level: appState.experienceLevel,
        results: appState.sessionResults
      })
    });
    const summary = await res.json();
    renderReport(summary);
  } catch (err) {
    console.error("Failed to generate report summary:", err);
  }
}

function renderReport(summary) {
  // Verdict & Scores
  $("reportVerdict").textContent = summary.verdict || "Practice Completed";
  $("reportAvgScore").textContent = summary.overall_score.toFixed(1);
  $("reportStatusDesc").textContent = summary.hiring_status || summary.executive_summary;
  $("reportExecSummary").textContent = summary.executive_summary;

  // Category Bars
  const cat = summary.category_scores || {};
  $("repAcc").textContent = `${cat.accuracy || 0}/10`;
  $("repAccBar").style.width = `${(cat.accuracy || 0) * 10}%`;

  $("repRel").textContent = `${cat.relevance || 0}/10`;
  $("repRelBar").style.width = `${(cat.relevance || 0) * 10}%`;

  $("repTech").textContent = `${cat.technical_depth || 0}/10`;
  $("repTechBar").style.width = `${(cat.technical_depth || 0) * 10}%`;

  $("repComm").textContent = `${cat.communication || 0}/10`;
  $("repCommBar").style.width = `${(cat.communication || 0) * 10}%`;

  // Strengths & Gaps
  $("reportStrengthsList").innerHTML = (summary.key_strengths || []).map(s => 
    `<li>✓ ${s}</li>`
  ).join("");

  $("reportGapsList").innerHTML = (summary.critical_gaps || []).map(g => 
    `<li>▲ ${g}</li>`
  ).join("");

  // Roadmap Steps
  $("reportRoadmapSteps").innerHTML = (summary.preparation_roadmap || []).map((step, idx) => `
    <div class="roadmap-step-item">
      <div class="step-num">${idx + 1}</div>
      <div class="step-text">${step}</div>
    </div>
  `).join("");

  // Question-by-Question Log
  if (appState.sessionResults.length) {
    $("reportHistoryList").innerHTML = appState.sessionResults.map((r, i) => `
      <div class="history-item">
        <div class="history-header">
          <strong>Q${i + 1}. ${r.question}</strong>
          <span class="history-score">${r.score}/10</span>
        </div>
        <div class="history-answer"><em>Candidate Answer:</em> ${r.answer}</div>
        <div class="history-feedback"><strong>Feedback:</strong> ${r.feedback}</div>
        ${r.model_answer ? `<div class="history-feedback" style="margin-top:6px; color:#38bdf8;"><strong>Model Answer:</strong> ${r.model_answer}</div>` : ""}
      </div>
    `).join("");
  } else {
    $("reportHistoryList").innerHTML = `<p class="empty-state">No questions completed in this session.</p>`;
  }
}

// Print / PDF Button
$("printReportBtn").addEventListener("click", () => {
  window.print();
});

// ============================================================================
// 6. TIMER ENGINE
// ============================================================================

function startTimer() {
  stopTimer();
  if (appState.timerDuration <= 0) {
    $("timerBadge").classList.add("hidden");
    return;
  }

  $("timerBadge").classList.remove("hidden");
  $("timerBadge").classList.remove("urgent");
  appState.timerRemaining = appState.timerDuration;
  appState.isTimerRunning = true;
  updateTimerDisplay();

  appState.timerInterval = setInterval(() => {
    if (!appState.isTimerRunning) return;
    appState.timerRemaining--;
    updateTimerDisplay();

    if (appState.timerRemaining <= 30) {
      $("timerBadge").classList.add("urgent");
    }

    if (appState.timerRemaining <= 0) {
      stopTimer();
      showToast("Time's up! Submitting your answer for evaluation.");
      $("submitAnswerBtn").click();
    }
  }, 1000);
}

function stopTimer() {
  if (appState.timerInterval) {
    clearInterval(appState.timerInterval);
    appState.timerInterval = null;
  }
  appState.isTimerRunning = false;
}

function updateTimerDisplay() {
  const mins = Math.floor(appState.timerRemaining / 60);
  const secs = appState.timerRemaining % 60;
  $("timerText").textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

$("timerToggleBtn").addEventListener("click", () => {
  appState.isTimerRunning = !appState.isTimerRunning;
  $("timerToggleBtn").textContent = appState.isTimerRunning ? "⏸" : "▶";
});

// ============================================================================
// 7. SPEECH SYNTHESIS & VOICE DICTATION
// ============================================================================

// Voice Toggle Button in Topbar
$("voiceToggleBtn").addEventListener("click", () => {
  appState.voiceEnabled = !appState.voiceEnabled;
  $("voiceIcon").textContent = appState.voiceEnabled ? "🔊" : "🔇";
  $("voiceText").textContent = appState.voiceEnabled ? "AI Voice On" : "AI Voice Muted";
  $("voiceToggleBtn").classList.toggle("active", appState.voiceEnabled);
  
  if (!appState.voiceEnabled && window.speechSynthesis) {
    window.speechSynthesis.cancel();
    stopSpeakingWave();
  }
});

// Speak Question on Button Click
$("speakQuestionBtn").addEventListener("click", () => {
  if (appState.currentQuestion) {
    speakQuestion(appState.currentQuestion.q);
  }
});

function speakQuestion(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel(); // Stop any pending speech

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  // Pick natural voice if available
  const voices = window.speechSynthesis.getVoices();
  const naturalVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Samantha")));
  if (naturalVoice) utterance.voice = naturalVoice;

  utterance.onstart = () => {
    appState.isSpeaking = true;
    startSpeakingWave();
  };

  utterance.onend = () => {
    appState.isSpeaking = false;
    stopSpeakingWave();
  };

  utterance.onerror = () => {
    appState.isSpeaking = false;
    stopSpeakingWave();
  };

  window.speechSynthesis.speak(utterance);
}

function startSpeakingWave() {
  const waves = $("speakingWaves");
  if (waves) waves.classList.add("speaking");
}

function stopSpeakingWave() {
  const waves = $("speakingWaves");
  if (waves) waves.classList.remove("speaking");
}

// Speech-to-Text / Microphone Dictation
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  appState.recognition = new SpeechRecognition();
  appState.recognition.continuous = true;
  appState.recognition.interimResults = true;
  appState.recognition.lang = "en-US";

  appState.recognition.onstart = () => {
    appState.isRecording = true;
    $("micBtn").classList.add("recording");
    $("micLabel").textContent = "Listening...";
    showToast("Microphone listening. Speak your answer!");
  };

  appState.recognition.onresult = (event) => {
    let finalTranscript = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript + " ";
      }
    }
    if (finalTranscript) {
      const textarea = $("answerInput");
      textarea.value = (textarea.value ? textarea.value + " " : "") + finalTranscript.trim();
      textarea.dispatchEvent(new Event("input"));
    }
  };

  appState.recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    stopRecording();
  };

  appState.recognition.onend = () => {
    stopRecording();
  };

  $("micBtn").addEventListener("click", () => {
    if (appState.isRecording) {
      appState.recognition.stop();
      stopRecording();
    } else {
      try {
        appState.recognition.start();
      } catch (err) {
        console.error("Mic start error:", err);
      }
    }
  });

} else {
  // Not supported
  $("micBtn").addEventListener("click", () => {
    showToast("Speech Recognition not supported in this browser. Try Chrome/Edge.");
  });
}

function stopRecording() {
  appState.isRecording = false;
  $("micBtn").classList.remove("recording");
  $("micLabel").textContent = "Voice Dictation";
}

// ============================================================================
// 8. TOAST SYSTEM
// ============================================================================

function showToast(message) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}

// ============================================================================
// 9. INITIALIZATION
// ============================================================================

window.addEventListener("DOMContentLoaded", async () => {
  await loadConfig();
  await loadDomains();
});
