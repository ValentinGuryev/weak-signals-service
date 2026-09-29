# (2024) Ebadi, Auger, Gauthier — WISDOM: AI-Powered Framework for Emerging Research Detection

**Файл:** `(2024) !!! Ebadi, Auger, Gauthier — WISDOM Framework Emerging Research Detection.pdf`
**Библиография:** Ashkan Ebadi, Alain Auger, Yvan Gauthier. «WISDOM: An AI-Powered Framework for Emerging Research Detection Using Weak Signal Analysis and Advanced Topic Modeling». arXiv:2409.15340 (2024).
**Аффилиации:** National Research Council Canada (NRC, Digital Technologies Research Centre, Toronto/Ottawa), Defence Research and Development Canada (DRDC, Science and Technology Foresight and Risk Assessment Unit).
**Релевантность:** 5/5 — **продолжение работы Ebadi 2022 (у нас в кейсах как эталон метода)**: BERTopic + weak signal analysis для выявления emerging research. Кейс: underwater sensing (2004-2021). Прямой аналог нашей задачи.

---

## Суть работы

Многослойный AI-фреймворк **WISDOM** для автоматического выявления emerging research themes: **BERTopic** (продвинутый тематический анализ на трансформерах) + **weak signal analysis** (анализ слабых сигналов). Мотивация: библиометрия и эксперты имеют недостатки (упрощение, субъективность, ручной труд). WISDOM обрабатывает большие объёмы, находит скрытые кросс-дисциплинарные паттерны, даёт объективные инсайты.

**Кейс-технология:** underwater sensing technologies, научные статьи 2004-2021 (~2 десятилетия).

## Ключевые результаты

### 6 вкладов (по авторам)
1. **BERTopic** для идентификации тем и трассировки эволюции (трансформеры + class-based TF-IDF → плотные кластеры, интерпретируемые темы);
2. **Weak signal analysis** для выявления зарождающихся тем (то, что не видно обычными методами);
3. Модульный/многослойный подход, переносимый на разные домены;
4. **Временной охват ~2 десятилетия** (2004-2021) — темпоральный анализ эволюции;
5. **Объективность** (без human bias);
6. Демонстрация на underwater sensing.

### Контекст (определения emerging)
- Rotolo et al. — 5 атрибутов emerging tech: radical novelty, fast growth, coherence, significant impact, uncertainty/ambiguity;
- Разные определения: socio-economic impact / uncertainty / novelty+growth;
- Ebadi 2022 (прошлая работа): BERT-ключевые слова + KEM/KIM карты; WISDOM расширяет (BERTopic вместо STM).

### Методика (пайплайн)
1. Данные: все публикации по underwater sensing (с доменными экспертами), 2004-2021;
2. **BERTopic** — извлечение главных тем (преимущество над STM: контекст, интерпретируемость, time-specific темы);
3. **Weak signal extraction** — выявление зарождающихся тем.

### Отличие от прошлой работы (Ebadi 2022)
- 2022: BERT-экстракция ключевых слов + KEM/KIM (частотные карты), кейс гиперзвук;
- 2024 (WISDOM): BERTopic (темы, а не слова) + weak signal, кейс underwater sensing;
- BERTopic даёт темы с эволюцией во времени, интерпретируемые, с representative keywords.

## Выводы авторов
- WISDOM — end-to-end, модульный, переносимый; для стратегических планировщиков и экспертов;
- Быстрее, объективнее, масштабнее ручной библиометрии;
- Ограничения: один домен-кейс; общность заявлена, требует проверки.

## Значимость для кейса/проекта
- **Прямой аналог** (тот же автор, что наш эталон Ebadi 2022);
- **BERTopic** — потенциальный инструмент для нашего S2 (семантический сдвиг) / S3 (кластеры тем): темы + эволюция по времени;
- Слабое место WISDOM: **один источник (статьи), без пересечения баз** — наш мульти-базовый подход (S1: статьи ∩ патенты ∩ гранты ∩ рынок) строже и это наше преимущество;
- Подтверждает: **weak signal analysis — признанный тренд методов** (оборонные/научные агентства Канады инвестируют).

## Замечания
- Препринт arXiv (2024), не рецензированный (на момент обработки);
- Ebadi/Auger/Gauthier — те же авторы, что у нашего эталона 2022 — стоит сопоставить оба метода (для METHODOLOGY-раздела «сравнение с аналогами»).
