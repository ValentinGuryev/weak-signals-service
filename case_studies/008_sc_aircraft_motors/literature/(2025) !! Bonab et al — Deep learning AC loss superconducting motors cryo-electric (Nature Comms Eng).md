# (2025) !! Bonab et al — Deep-learning model for AC losses in superconducting motors for hydrogen cryo-electric aircraft (Nature Comms Eng)

> **Файл PDF:** `(2025) !! Bonab et al — Deep learning AC loss superconducting motors cryo-electric (Nature Comms Eng).pdf`
> **Репозиторий:** ❌ (данные/модель в статье; Nature Comms Eng)
> **Статус:** выжимка готова ()

---

## Библиография
- **Авторы:** Shahin Alipour Bonab¹, Frederick Berg², Wenjuan Song¹, Alexandre Colle², Mohammad Yazdani-Asrami¹
  ¹ (University of Glasgow — Yazdani-Asrami, СП-машины), ² **AIRBUS** (Berg, Colle — Cryoprop)
- **Название:** Advanced deep-learning model for temporal-dependent prediction of dynamic behavior of AC losses in superconducting propulsion motors for hydrogen-powered cryo-electric aircraft
- **Источник:** Communications Engineering (Nature Portfolio), 2025 — **OPEN ACCESS**
- **DOI:** 10.1038/s44172-025-00554-8

## Релевантность: **5/5 (!!!) — открытая, с соавторами Airbus (Cryoprop)**
- Прямо про СП-моторы для **водородных cryo-electric самолётов** (Cryoprop-контекст!), AC-потери — ключевой барьер кейса.
- Соавторы из Airbus (Berg, Colle) — подтверждает, что Airbus UpNext/Cryoprop активно работает над СП-моторами.

## Суть (1 абзац)
СП-моторы дают высокую плотность мощности для водородных cryo-electric самолётов, но AC-потери при крио надо точно и быстро оценивать на этапе дизайна. Классика: FEM слишком медленна для системных моделей; аналитика/таблицы неточны; прежние ML давали только средние по циклу потери. Авторы: **AI-модель (deep learning)** предсказывает **динамические AC-потери** (морфологию мгновенных потерь во времени + средние по циклу) для разных режимов и **обобщается на невиданные конфигурации** моторов.

## Ключевые результаты
1. **DL-модель: предсказание <9 мс с точностью 99.97% (R²)** — пригодна для системного моделирования.
2. Предсказывает и **cycle-averaged, и time-dependent** потери (динамику) — новое против прежних статических ML.
3. Интеграция в **model-based design**: быстрые прогоны, compliance-проверки, выявление интеграционных проблем до развёртывания.
4. Большой датасет конфигураций моторов; обобщение на unseen-дизайны.

## Что это даёт кейсу 008
1. **Airbus (Cryoprop) + Glasgow активно развивают СП-моторы** (2025, открыто) — тренд жив в водородной нише.
2. AC-потери — решаемая проблема (и Pardo 2026, и эта AI-модель для их быстрой оценки) — **барьер из README 008 снят**.
3. Методологически: AI-surrogate для AC-потерь — пример «инженеризация» темы (S2-сигнал зрелости: от физики к инструментам дизайна).
4. Yazdani-Asrami (Glasgow) — активный автор по СП-машинам/крио (см. также его обзоры).

## Заметки
- Nature Comms Engineering — открытый (CC-BY), скачан.
- Созвучно Pardo 2026 (AC-потери <0.018%): консенсус 2025-26 — AC-потери управляемы, СП-моторы для водородной авиации проектируются.
