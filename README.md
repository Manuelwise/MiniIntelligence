# 🧠 Productivity Insight Engine — AI Rule Engine + LLM Challenge 2025

A hybrid AI system that analyzes daily productivity using **deterministic rules** + **LLM-generated insights**.  
The system ingests a structured daily report and produces a **score**, **tags**, and **explanations**, enhanced by **LLM insights and recommendations**.

---

## 1. 🔍 Summary
This project evaluates a user’s daily productivity by combining a **local rule-based engine** with an **LLM analysis layer** to produce actionable insights. The chosen domain is **personal productivity & behavior analytics**.

---

## 2. 🎯 Problem & Domain

### **Domain**
Modern productivity tracking tools often focus on raw metrics (time spent, tasks completed) but fail to interpret *why* performance fluctuates or *how* someone can improve.  
This project solves that by merging algorithmic scoring with LLM reasoning.

### **Use Cases**
- Personal productivity analysis  
- Employee wellness dashboards  
- Daily self-reflection journaling  
- Coaching and behavioral improvement tools  

---

## 3. 🏗️ Architecture

### **High-Level Flow**
```mermaid
flowchart TD
    A[Client Request] --> B[FastAPI Endpoint /api/v1/analyze]
    B --> C[Input Validation (Pydantic)]
    C --> D[Rule Engine compute_productivity()]
    D --> E[Score + Tags + Explanations]
    E --> F[LLM Layer (LangChain + OpenAI)]
    F --> G[Caching Layer (Redis/In-memory)]
    G --> H[Final Structured JSON Response]

Components

FastAPI backend

Rule Engine (deterministic scoring)

LangChain LLM Layer for insights

Caching (Redis or in-memory fallback)

Rate Limiting to protect LLM API

Pydantic Schemas for validation

Tech Stack
Component	Tech Used
Backend	FastAPI (Python)
LLM Framework	LangChain
AI Provider	OpenAI API
Cache	Redis + fallback
Auth	Basic API key
Deployment	Any container environment
4. 📦 Data & Schema
Input Schema
{
  "user_id": "123",
  "date_range": "2025-11-29",
  "tasks": [
    {
      "id": "T1",
      "title": "Write report",
      "planned_minutes": 60,
      "actual_minutes": 45,
      "completed": true
    }
  ],
  "deep_work_minutes": 120,
  "meetings_minutes": 40,
  "interruptions": 12,
  "sleep_hours": 6.5,
  "breaks_minutes": 20,
  "mood": 6,
  "notes": "Busy day but productive."
}

Output Schema
{
  "score": 72.5,
  "tags": ["good-focus", "insufficient-sleep"],
  "explanations": [
    {
      "rule_id": "R1",
      "description": "Deep work above threshold",
      "effect_on_score": 15
    }
  ],
  "llm_insight": "Your productivity was strong, but interruptions reduced your efficiency.",
  "llm_recommendations": [
    "Reduce phone switches during deep work blocks",
    "Maintain your deep work practice"
  ]
}

5. 🧮 Rule Engine

Rules are located in app/rules/ and include:

Examples

Deep Work Boost
If deep_work_minutes > 90 → +15 points

Excessive Interruptions
If interruptions > 15 → −10 points

Low Sleep Penalty
If sleep_hours < 7 → −8 points

Task Completion Ratio
Completed tasks / total tasks influences score

Why These Rules?

These rules reflect common productivity science principles such as:

Quality focus beats hours worked

Sleep strongly affects cognitive ability

Context switching reduces efficiency

6. 🤖 LLM Layer
Model

Provider: OpenAI

Model: defined in .env (LLM_MODEL=gpt-4.1-mini recommended)

LangChain Components

ChatOpenAI

PromptTemplate

LLMChain

PydanticOutputParser

Prompt Structure

The LLM receives:

Score

Tags

Rule Engine Explanations
And must return strict structured JSON following a Pydantic model.

Safety

Max retries configured

Temperature controlled (default 0.3)

Strict JSON parsing with fallback on error

Caching prevents unnecessary repeat LLM calls

7. 🛠️ API Usage
POST /api/v1/analyze

Main endpoint.

Example Request
curl -X POST "http://localhost:8000/api/v1/analyze" \
-H "Content-Type: application/json" \
-d '{"deep_work_minutes":120,"meetings_minutes":40,"interruptions":10,"sleep_hours":6.5,"breaks_minutes":20,"tasks":[]}'

Response
{
  "score": 68.0,
  "tags": ["good-focus"],
  "explanations": [...],
  "llm_insight": "...",
  "llm_recommendations": ["..."]
}

8. 🚀 Quickstart
1. Clone repo
git clone <your-repo-url>
cd project-folder

2. Install dependencies
pip install -r requirements.txt

3. Create .env
LLM_API_KEY=your_openai_key
LLM_MODEL=gpt-4.1-mini
RATE_LIMIT="5/minute"
CACHE_EXPIRE_SECONDS=3600

4. Run server
uvicorn app.main:app --reload

5. Test in browser

Open:

http://localhost:8000/docs