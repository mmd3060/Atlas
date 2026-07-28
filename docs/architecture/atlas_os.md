# Atlas OS Architecture

> معماری نهایی Atlas OS - Model-First، Agent-Oriented، Self-Improving

---

## Core (هسته اصلی)

- **Smart Router v2** ✅
  - Task Classification (Coding, Math, Writing, Research, Translation, Vision, Voice, Planning, Agent Tasks)
  - Model-Based Scoring (Quality, Speed, Cost, Context, Capability)
  - Provider-Agnostic تصمیم‌گیری

- **Model Registry** ✅
  - Capabilities (Vision, Audio, Tool Calling, Memory Compatibility)
  - Context Window
  - Providers list per model
  - Price per 1M tokens (input/output)
  - Speed tier
  - Tags

- **Model Resolver** ✅
  - هر مدل می‌تواند از چند Provider در بیاید
  - Priority-based resolution
  - Auto-failover

- **API Pool** ✅
  - GitHub Models Keys
  - OpenRouter Keys
  - NVIDIA NIM Keys
  - Google Gemini Keys
  - Key Rotation & Health Check

- **Decision Engine** ✅
  - Quality (0-1)
  - Speed (0-1)
  - Cost (0-1)
  - Memory (0-1)
  - Health (0-1)
  - Capability Match (0-1)
  - User Preference

---

## Routers (مسیریاب‌ها)

- **Text Router** ✅
  - تحلیل متن
  - انتخاب بهترین مدل متنی

- **Voice Router** 🟡
  - STT (Speech to Text)
  - Task Detection
  - Best Model Selection
  - TTS (Text to Speech) برای پاسخ

- **Vision Router** 🟡
  - Image Analysis
  - OCR
  - Vision Model Selection
  - Vision Model Execution

- **Tool Router** 🟡
  - تشخیص نیاز به ابزار
  - انتخاب ابزار مناسب
  - اجرای ابزار

---

## Intelligence (هوش)

- **Memory** ✅
  - Short Memory (Session)
  - Long Memory (Episodic) ✅
  - Semantic Memory (Knowledge Graph) ✅
  - Procedural Memory (How-to) ✅
  - User Memory
  - Reflection Memory

- **Reflection Engine** ✅
  - تحلیل پاسخ‌ها
  - استخراج درس (Lesson)
  - بهینه‌سازی استراتژی

- **Evolution Core** ✅
  - Weight Optimizer
  - Hypothesis Engine
  - Experiment Planner
  - Experiment Runner
  - Evaluator
  - Evolution Memory

- **Cost Intelligence** ✅
  - Token Tracking
  - Cost Estimation
  - Budget Management

- **Health Monitor** ✅
  - Provider Latency
  - Provider Uptime
  - Error Rate
  - Quota Tracking
  - Auto-Failover

---

## Target: Model-First Architecture

**Atlas هیچ Providerی را نشناسد. تمام تصمیم‌ها بر اساس Model هستند.**

```
User Message
    ↓
Input Analyzer (Task Type, Language, Complexity)
    ↓
Smart Router V2
    ↓
Model Ranker
    ↓
Model Resolver (API Pool)
    ↓
Execution Engine
    ↓
Model Executor
    ↓
API Pool (Provider Keys)
    ↓
Provider (GitHub / OpenRouter / NVIDIA / Gemini)
    ↓
Response
    ↓
Memory Store
    ↓
Reflection
    ↓
Evolution (Weight Update)
    ↓
Final Answer
```