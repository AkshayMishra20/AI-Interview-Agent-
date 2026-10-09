# InterviewAI — Autonomous AI Interview Preparation Assistant

A modern, full-featured AI Interview Preparation Platform powered by **Google Gemini** (with multi-provider support for **OpenAI**, **Groq**, and an **Offline Smart Engine**). Built with Flask, HTML5, CSS3, and JavaScript.

---

## 🌟 Key Features

- **🤖 Real AI Model Integration**:
  - **Google Gemini**: Uses native Gemini models (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`) via `google-genai`. Free API keys available from [Google AI Studio](https://aistudio.google.com).
  - **OpenAI & Groq Cloud**: Ready-to-use support for `gpt-4o-mini`, `llama-3.3-70b-versatile`, or custom endpoints (e.g. local Ollama).
  - **Offline Smart Heuristic Engine**: Works seamlessly without any API key or when offline, utilizing a 50+ curated industry question bank and rubric analysis.
  - **In-App AI Configuration**: Switch models, enter API keys, and test latency with one click directly inside the web UI without modifying configuration files.

- **🎯 Dynamic Question Synthesis**:
  - Generates realistic, non-repetitive interview questions tailored to your **Domain**, **Job Role**, **Experience Level** (Junior / Mid / Senior), and **Difficulty**.
  - Provides instant **Hints & Context** for each question.

- **📊 4-Pillar AI Evaluation Rubric**:
  - **Technical Accuracy & Depth (35%)**: Checks factual correctness, terminology, and technical precision.
  - **Relevance & Completeness (25%)**: Evaluates how directly the answer addresses all parts of the question.
  - **Problem Solving & Architecture (20%)**: Assesses trade-offs, real-world examples, and reasoning.
  - **Communication & Structure (20%)**: Checks clarity, grammar, articulation, and formatting.

- **🎙️ Real-Time Voice & Audio**:
  - **AI Voice Reading (Text-to-Speech)**: The AI interviewer speaks questions aloud with animated speech waves.
  - **Voice Dictation (Speech-to-Text)**: Speak your answers hands-free using your microphone.

- **💡 Model Answers & Adaptive Follow-Ups**:
  - **Ideal / Model Answer**: Shows how an engineering lead or hiring manager would formulate the ideal response.
  - **Missing Concepts**: Highlights technical keywords or concepts you missed.
  - **Dynamic Follow-Up Questions**: Challenges you with spontaneous follow-ups based on what you answered.

- **📈 Scorecard & Customized Preparation Roadmap**:
  - Calculates final session score and official **Hiring Verdict** (*Strong Hire 🌟*, *Hire 👍*, *Leaning Hire ⚠️*, *Needs Preparation ❌*).
  - Outlines **Key Strengths** and **Primary Blindspots**.
  - Generates a personalized 3-step action roadmap.
  - Includes a question-by-question log with your submitted answers and expert solutions.
  - **Print / Save as PDF** support.

---

## 📁 Project Structure

```
ai_interview/
├── app.py                  # Flask web server and REST API endpoints
├── ai_engine.py            # Unified AI Engine (Gemini, OpenAI, Groq & Offline)
├── requirements.txt        # Python dependencies
├── .env.example            # Sample configuration file
├── templates/
│   └── index.html          # Modern cyber/dark responsive user interface
└── static/
    ├── css/
    │   └── style.css       # Full styling, glassmorphism, animations, print media
    └── js/
        └── app.js          # Interactive frontend logic, Speech API, timer & state
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher (Python 3.11 recommended).
- A modern web browser (Google Chrome, Microsoft Edge, or Firefox).

### 2. Install Dependencies

Open a terminal in this project folder and run:

```bash
pip install -r requirements.txt
```

### 3. (Optional) Set Your AI API Key

You can configure your API key either in `.env` or directly through the web UI:

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Add your **Google Gemini API Key** (Get free from [Google AI Studio](https://aistudio.google.com)):
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

*Note: If you don't provide an API key, the system automatically runs in **Offline Smart Engine Mode** with zero configuration.*

### 4. Run the Application

```bash
python app.py
```

### 5. Open Your Browser

Navigate to:
```
http://127.0.0.1:5000
```

---

## 🛠️ API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Main interview dashboard & live application |
| `/api/config` | `GET`, `POST` | Get or update AI model provider, keys & settings |
| `/api/test-connection` | `POST` | Ping the selected AI model to verify connection & latency |
| `/api/domains` | `GET` | List all interview tracks with descriptions & icons |
| `/api/question` | `POST` | Generate interview question using AI model |
| `/api/evaluate` | `POST` | Evaluate answer with 4-pillar rubric, feedback & model answer |
| `/api/session-summary` | `POST` | Generate final session debrief, verdict & roadmap |
| `/api/stats` | `GET` | General platform statistics |

---

## 🛡️ License & Academic Integrity

Developed for educational and technical preparation purposes. Free to customize, extend, and deploy.
