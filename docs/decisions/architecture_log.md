# Architecture Log

> تصمیم‌های حیاتی اطلس

---

## 2026-07-26
- **Decision:** حذف "Provider First".
- **Replacement:** Model First جایگزین شد.
- **Reason:** Atlas باید فقط مدل را بشناسد. Providerها صرفاً تأمین‌کننده (API Keys) هستند.

## 2026-07-27
- **Decision:** ساختار پکیج حافظه (core/memory/).
- **Reason:** جلوگیری از تداخل module قدیمی memory.py و پکیج جدید memory/.
- **Status:** مهاجرت کامل شد.

## 2026-07-27
- **Decision:** ساخت ExecutionEngine v1.
- **Reason:** استانداردسازی اجرای مدل‌ها و جدا کردن هسته اجرایی از لاجیک مسیریابی.

## 2026-07-28
- **Decision:** پیاده‌سازی Advanced Memory v2 (Epi, Sem, Proc).
- **Reason:** تفکیک حافظه بر اساس ماهیت داده‌ها برای یادگیری بهتر.

## 2026-07-28
- **Decision:** پیاده‌سازی Multi-Agent System.
- **Reason:** تخصصی کردن کارها توسط Agentهای مجزا (Coder, Researcher, Planner, Reviewer).

## 2026-07-28
- **Decision:** پیاده‌سازی Self-Modifying Agent (Safe).
- **Reason:** اجازه به Atlas برای تحلیل و اصلاح کد خود برای بهینه‌سازی (با احتیاط).