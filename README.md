# Atlas OS 🧠⚡

> **Atlas OS** یک سیستم‌عامل هوش مصنوعی است که بر روی Android (Termux) اجرا می‌شود.
> مدل‌های هوش مصنوعی را مثل «پردازنده‌های» جایگزین و قابل تر پیکربندی می‌بیند.

---

## 🚀 ویژگی‌ها

### Core Intelligence
- **Smart Router v2** — تصمیم‌گیری بر اساس مدل (نه Provider)
- **Model Registry** — رجیستری تمام مدل‌ها با قابلیت‌ها
- **Multi-Model Consensus** — اگر اختلاف امتیاز کم بود، چند مدل همزمان اجرا شوند
- **Decision Engine** — امتیازدهی: Quality + Speed + Cost + Memory + Health

### Memory System (v3)
- **Episodic Memory** — اتفاقات و تجربیات
- **Semantic Memory** — دانش و روابط (Knowledge Graph)
- **Procedural Memory** — روش‌ها (How-to)
- **SQLite + Bridge** — پایداری دائمی بین سشن‌ها

### Tool System
- **Terminal** — اجرای دستورات شل (با Permission)
- **File Manager** — خواندن، نوشتن، جستجو، پیدا کردن فایل‌ها
- **Web Search** — جستجوی اینترنت (DuckDuckGo + Wikipedia)
- **Code Executor** — اجرای کد پایتون در محیط ایزوله
- **Remove Background** — حذف پس‌زمینه عکس (FeyNoBg)

### Voice & Vision
- **Voice Router** — گفتار به متن + پاسخ صوتی (gTTS + Whisper)
- **Vision Router** — تحلیل تصاویر (Gemini Vision)

### Multi-Agent System
- **Coder** — نوشتن کد
- **Researcher** — تحقیق و جمع‌آوری اطلاعات
- **Planner** — برنامه‌ریزی و تقسیم وظایف
- **Reviewer** — بازبینی و بهبود
- **Orchestrator** — هدف‌گذاری خودکار ایجنت‌ها

### Self-Improvement
- **Self-Modifying Agent** — توانایی اصلاح کدهای خودش (با Backup)
- **Evolution Core v1 + v2** — خودکار بهینه‌سازی و آزمایش
- **Reflection Engine** — تحلیل پس از هر پاسخ

---

## 📦 نصب (Termux)

```bash
# ۱. کلون کن
git clone https://github.com/mmd3060/Atlas.git ~/Atlas
cd ~/Atlas

# ۲. نصب پیش‌نیازها
pip install -r requirements.txt

# ۳. تنظیمات محیطی
cp .env.example .env
# فایل .env رو ویرایش کن و API Keys رو بنویس

# ۴. اجرا
python main.py
```

---

## 🤖 Telegram Bot

```bash
# تنظیم توکن ربات در .env
TELEGRAM_BOT_TOKEN=your_token_here

# اجرای ربات
python telegram_bot.py
```

**دستورات تلگرام:**
| دستور | عملکرد |
|---|---|
| `/start` | خوش‌آمدگویی |
| `/status` | وضعیت سیستم |
| `/tools` | لیست ابزارها |
| `/agents` | لیست ایجنت‌ها |
| `/memory` | وضعیت حافظه |
| `/search <query>` | جستجوی وب |
| `/code <python>` | اجرای کد پایتون |

**Voice & Vision:** صدا یا عکس بفرست تا خودش پردازش کنه!

---

## 🧪 تست

```bash
# اجرای تمام تست‌ها
python test_smart_router_v2.py
python test_reasoning_pipeline.py
python test_brain_memory_adapter.py
python test_execution_engine.py
```

---

## 📂 ساختار پروژه

```
Atlas/
├── main.py                  # OS Shell (CLI entry point)
├── telegram_bot.py          # Telegram Bot Interface
├── .env                     # Configuration & API Keys
├── requirements.txt         # Python dependencies
├── core/
│   ├── intelligence/         # Kernel System
│   │   ├── execution_engine.py
│   │   ├── consensus_engine.py
│   │   └── ...
│   ├── memory/               # 3-Layer Memory
│   │   ├── episodic_memory.py
│   │   ├── semantic_memory.py
│   │   ├── procedural_memory.py
│   │   └── memory_bridge.py
│   ├── brain/                # Reasoning & Pipeline
│   │   ├── reasoning_pipeline.py
│   │   ├── reasoning_pipeline_v2.py
│   │   └── ...
│   ├── tools/                # Tool System
│   │   ├── tool_system.py
│   │   ├── tool_executor.py
│   │   ├── permission_manager.py
│   │   ├── file_manager.py
│   │   ├── web_search.py
│   │   ├── image_editor.py
│   │   ├── code_executor.py
│   │   └── cron_scheduler.py
│   ├── interfaces/           # Voice & Vision Gateways
│   │   ├── voice_gateway.py
│   │   └── vision_gateway.py
│   ├── agents/               # Multi-Agent System
│   │   ├── agent_manager.py
│   │   ├── orchestrator.py
│   │   └── self_modifying_agent.py
│   └── routers/              # Smart Router v2
├── docs/
│   ├── ideas/brainstorm.md   # All ideas
│   ├── architecture/atlas_os.md  # Final architecture
│   ├── roadmap/roadmap_v2.md  # Progress track
│   └── specifications/atlas_os_blueprint.md
├── providers/                # API Provider integrations
└── test_*.py                 # All test files
```

---

## 🔄 نقشه راه

- ✅ Smart Router v2 + Model-First Architecture
- ✅ Advanced Memory (Episodic + Semantic + Procedural)
- ✅ Tool System (9 tools)
- ✅ Multi-Agent + Orchestrator
- ✅ Self-Modifying Code
- ✅ Voice + Vision Gateways
- ✅ Telegram Bot with Typing Indicator
- 🟡 Multi-Model Consensus (Execution)
- 🟡 Full STT/TTS Pipeline
- 🔴 Judge Model + Answer Fusion

---

## 🤝 ساخت

**Atlas OS** توسط **mmd3060** ساخته شده با الهام از فلسفه:
> *Minimum restrictions + maximum observation + rollback capability*

---

## 📌 لایسنس

Private — Atlas OS Project

---

*Last Updated: 2026-07-28*