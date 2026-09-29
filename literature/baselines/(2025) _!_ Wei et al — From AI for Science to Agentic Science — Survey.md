# (2025) Wei et al. — From AI for Science to Agentic Science: A Survey

**Файл:** `(2025) _!_ Wei et al — From AI for Science to Agentic Science — Survey.pdf`
**Библиография:** Wei J., Yang Y., Zhang X., Chen Y., Zhuang X., Gao Z., Zhou D. et al. «From AI for Science to Agentic Science: A Survey on Autonomous Scientific Discovery». arXiv:2508.14111v2 [cs.LG], 20 Oct 2025. Homepage: agenticscience.github.io; **репозиторий: github.com/AgenticScience/Awesome-Agent-Scientists**.
**Аффилиации:** Shanghai AI Laboratory, Zhejiang University, Fudan University, University of British Columbia, Tongji University, CUHK, Shanghai Jiaotong University, Stony Brook University, Tsinghua University и др.
**Релевантность:** 3/5 — наиболее полная (из имеющейся у нас) карта направления «автономный научный поиск» (agentic science): пятиуровневая модель зрелости, четырёхэтапный workflow, доменные обзоры. Контекст и related-work; метод детекции трендов не даёт.

---

## Суть работы

Обзор **Agentic Science** как стадии парадигмы AI-for-Science: ИИ переходит от инструмента к автономному партнёру исследователя (гипотезы, дизайн экспериментов, исполнение, анализ, итерации). Объединяет три ранее разрозненных перспективы (process-, autonomy-, mechanism-oriented) в единый фреймворк.

Вклады: (i) эволюция AI-for-Science; (ii) 5 базовых способностей научного агента; (iii) научное открытие как 4-этапный workflow; (iv) обзор применений в life sciences, химии, материаловедении, физике; (v) вызовы и будущее.

## Ключевые результаты

1. Модель зрелости: Level 1 «AI как вычислительный оракул» → Level 2 «автоматизированный ассистент» → … → полная научная агентность;
2. 5 ключевых способностей: генерация гипотез, планирование/дизайн, исполнение (в т.ч. лабораторное), анализ данных, итеративная рефлексия;
3. Доменные реализации: химия/биология/материалы/физика (SciAgents и др. — внутри карты);
4. Вызовы: доверие/воспроизводимость, оценка качества (evaluation), интеграция с человеческим исследователем.

## Выводы авторов

- Agentic Science — структурированная парадигма для продвижения AI-исследований;
- Ключевая нерешённая проблема — **оценка** агентов (близко к нашим бенчмарковым вопросам).

## Значимость для кейса/проекта

- Самая свежая и полная карта agentic-science: позволяет позиционировать нашу работу (детекция трендов ≠ автономный поиск, но мы используем LLM-агентов как ассистентов в пайплайне);
- Репозиторий Awesome-Agent-Scientists — **готовый каталог** будущих методов для расширения нашей библиотеки (SCI-IDEA, SciAgents и др. там индексированы);
- В related work статьи: цитируем как карту ландшафта «LLM-агенты в науке» (2025).

## Замечания

- arXiv v2 (Oct 2025); крупный обзор (~40 стр.);
- Есть официальный repo (Awesome-Agent-Scientists) → по конвенции подчёркивание в релевантности: `_!_`.