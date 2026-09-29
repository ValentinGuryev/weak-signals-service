# (2026) Menning, Farkas, Vribek, van der Velden — Regulatory foresight weak signal mining (Array)

- **Библиография:** Menning A.¹, Farkas Z.², Vribék K.², van der Velden B.H.M.³ — «Enhancing regulatory
  foresight through weak signal mining: An AI-based micro-topic emergence scoring approach», Array 31 (2026) 101126.
  ¹ German Federal Institute for Risk Assessment; ² Univ. Veterinary Medicine Budapest; ³ Wageningen Food Safety Research.
- **DOI:** (ScienceDirect Array, S2590005626004492)
- **Код/репо:** ✅ `https://github.com/HOLiFOOD/WSM` (Weak Signal Miner) → имя `_!!_`
- **Релевантность:** 4/5 (_!!_). **Операционализация weak signals в text mining** — прямо релевантно
  нашему пайплайну (детекция зарождающихся трендов из текстов).

## Суть
Представлен **Weak Signal Miner (WSM)** — AI-конвейер для детекции ранних слабых сигналов в больших
текстовых корпусах. Применение: **регуляторный форсайт** (пищевая безопасность, EFSA).

**Ключевое определение (операционализация weak signal):**
> Weak signals = концепты/темы с **низкой общей частотой, но выше-средним ускорением видимости во времени**.

## Метод (4 шага)
1. **Transformer-based micro-topic modelling** — выделение микро-тем в корпусе;
2. **Adaptive temporal aggregation** — адаптивная временная агрегация;
3. **Recency-and-magnitude scoring** — оценка «недавность × величина» для редких тем с
   непропорциональным недавним ростом;
4. **LLM-слой интерпретации** (опционально) — понятные ярлыки, оценки новизны и серьёзности,
   для поддержки эксперта (НЕ замена человека).

## Результаты (ретроспективная валидация)
- WSM выявил сигналы **PFOS-загрязнения (2004-2007)** и **citrinin в красном дрожжевом рисе (2010-2017)**
  **задолго** до официального признания в заключениях EFSA;
- Подтверждает: weak signal mining дополняет экспертный анализ, выявляя проблемы до/вне
  традиционных экспертных каналов.

## Значение для нашего проекта
1. **Формальное определение weak signal** (редкая тема + ускорение видимости) — совпадает с нашей
   S1/S3-логикой (рост малых тем);
2. **Метод**: micro-topic + recency/magnitude scoring — применим к arXiv/патентам;
3. **LLM как интерпретатор** (не классификатор) — как в нашем wordshift+LLM;
4. Регуляторный форсайт — аналог нашей задачи (слабые сигналы → тренды).
