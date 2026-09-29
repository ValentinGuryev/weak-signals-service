# (2026) Ebadi, Auger, Gauthier — Weak Signals of Emergence in Underwater Sensing

**Файл:** `(2026) !!! Ebadi, Auger, Gauthier — Weak Signals of Emergence in Underwater Sensing.pdf`
**Библиография:** Ashkan Ebadi, Alain Auger, Yvan Gauthier. «Unveiling Weak Signals of Emergence in Underwater Sensing Research Trends». Archives of Advanced Engineering Science, 2026, Vol. 4(3), pp. 229–237. DOI: 10.47852/bonviewAAES42023902. Received 22.07.2024, published online 22.10.2024.
**Аффилиации:** Digital Technologies, National Research Council Canada (NRC, Canada); Science and Technology Foresight and Risk Assessment Unit, Defence Research and Development Canada (DRDC, Canada).
**Релевантность:** 5/5 — **прямой аналог нашей задачи**: слабые сигналы зарождения исследовательских тем через NLP + topic modeling на корпусе статей; те же авторы, что у наших эталонов Ebadi 2022 (KEM/KIM) и WISDOM 2024 (BERTopic). Это журнальная версия пред-этапа WISDOM (метод — structural topic modeling, STM).

---

## Суть работы

Выявление emerging research trends в области подводных сенсорных технологий (underwater sensing) по корпусу научных статей **2007–2021** с помощью NLP + topic modeling (structural topic modeling, STM) + слабых сигналов. Мотивация — та же, что у WISDOM: библиометрия упрощает, эксперты субъективны; нужен автоматизированный объективный детектор.

**Ключевое отличие от WISDOM (2024):** здесь метод — STM (не BERTopic как в WISDOM); окно корпуса 2007–2021 (не 2004–2021); это более ранний/параллельный вариант той же линии авторов.

## Ключевые результаты

1. Из **80 извлечённых тем** — **6 распознано как emerging weak signals** и **подтверждено экспертами**;
2. **Единственная тема, перешедшая из слабого в сильный сигнал** в финальный период: **deep learning for underwater imaging**;
3. Валидация экспертами встроена в пайплайн (метка «emerging» ставится не только статистикой);
4. Кейс: подводные сенсоры (UUV, Internet of Underwater Things, IoUT) — растущая область.

## Выводы авторов

- Поиск emerging тем на стыке «частотная аномалия + семантическая тема» работает и даёт проверяемые результаты;
- Тематика underwater sensing — удобный кейс: быстрорастущий домен, междисциплинарный, сфокусированный (оборонные/экологические применения).

## Значимость для кейса/проекта

- **Подтверждает линию Ebadi (2022 → 2024 → 2026)** как основной внешний метод-аналог нашего S2/S3: слова/темы/слабые сигналы по временным рядам статей;
- Урок для нас: «6 из 80 тем = слабые сигналы, подтверждённые экспертами» — слабые сигналы редки и нуждаются в **человеческом фильтре** (наш Этап 2: impact×adoption×conversion — это и есть строгий фильтр);
- 🇨🇬 Ограничение (общее для линии Ebadi): один источник (статьи), **нет пересечения баз** — наш мульти-базовый подход (S1) остаётся сильнее;
- Для раздела «сравнение с аналогами» в статье: полный треугольник Ebadi 2022 → WISDOM 2024 (BERTopic) → 2026 (STM, журнальная версия).

## Замечания

- Журнальный PDF (AAES) получен напрямую; DOI 10.47852/bonviewAAES42023902;
- Авторы те же, что у WISDOM — при цитировании не перепутать: **это НЕ дубль WISDOM** (разные методы STM vs BERTopic, разные окна корпуса), но это один исследовательский трек.