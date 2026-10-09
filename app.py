import os
from flask import Flask, render_template, request, jsonify
from ai_engine import engine

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Configuration API
@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/config")
def get_config():
    """Retrieve current AI engine configuration and status."""
    return jsonify(engine.get_config())

@app.post("/api/config")
def update_config():
    """Update API keys, provider, or model configuration live from the UI."""
    data = request.get_json(force=True) or {}
    new_config = engine.update_config(data)
    return jsonify({"success": True, "config": new_config})

@app.post("/api/test-connection")
def test_connection():
    """Test AI model connection with a ping."""
    data = request.get_json(force=True) or {}
    provider = data.get("provider")
    key = data.get("api_key")
    model = data.get("model")
    result = engine.test_connection(provider, key, model)
    return jsonify(result)

@app.get("/api/domains")
def domains():
    """Return all supported interview domains."""
    return jsonify(engine.DEFAULT_DOMAINS)

@app.post("/api/question")
def question():
    """
    Generate an interview question using the AI Model.
    Supports domain, experience_level, difficulty, job_role, and previous_questions.
    """
    data = request.get_json(force=True) or {}
    domain = data.get("domain", "Artificial Intelligence & ML")
    experience_level = data.get("experience_level", "Fresher / Junior")
    difficulty = data.get("difficulty", "Medium")
    job_role = data.get("job_role", "Software Engineer")
    previous_questions = data.get("previous_questions", [])

    item = engine.generate_question(
        domain=domain,
        experience_level=experience_level,
        difficulty=difficulty,
        job_role=job_role,
        previous_questions=previous_questions
    )
    return jsonify(item)

@app.post("/api/evaluate")
def evaluate():
    """
    Deeply evaluates candidate's answer using the AI Model.
    """
    data = request.get_json(force=True) or {}
    question_text = data.get("question", "")
    answer_text = data.get("answer", "")
    domain = data.get("domain", "General")
    experience_level = data.get("experience_level", "Junior")
    is_follow_up = data.get("is_follow_up", False)
    parent_question = data.get("parent_question", "")

    if not question_text:
        return jsonify({"error": "Question is required"}), 400

    evaluation = engine.evaluate_answer(
        question=question_text,
        answer=answer_text,
        domain=domain,
        experience_level=experience_level,
        is_follow_up=is_follow_up,
        parent_question=parent_question
    )
    return jsonify(evaluation)

@app.post("/api/session-summary")
def session_summary():
    """
    Generates a full AI-driven candidate scorecard, verdict, and custom preparation roadmap.
    """
    data = request.get_json(force=True) or {}
    candidate_name = data.get("candidate_name", "Candidate")
    domain = data.get("domain", "General")
    experience_level = data.get("experience_level", "Junior")
    results = data.get("results", [])

    summary = engine.generate_session_summary(
        candidate_name=candidate_name,
        domain=domain,
        experience_level=experience_level,
        results=results
    )
    return jsonify(summary)

@app.get("/api/stats")
def stats():
    return jsonify({
        "domains": len(engine.DEFAULT_DOMAINS),
        "evaluation_criteria": [
            "Technical Accuracy & Depth (35%)",
            "Relevance & Completeness (25%)",
            "Technical Problem Solving (20%)",
            "Communication & Structure (20%)"
        ],
        "active_provider": engine.get_config()["active_provider"]
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting AI Interview Preparation Assistant on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
