# Выжимка: A Bibliometric Model for Identifying Emerging Research Topics

> **Глубина:** стандартная (релевантность 4/5)
> **Источник:** оригинальный PDF в `literature/`

---

## Библиография

- **Автор:** Qi Wang (Danish Centre for Studies in Research & Research Policy, Aarhus University; INDEK, KTH)
- **Название:** A Bibliometric Model for Identifying Emerging Research Topics
- **Издание:** Journal of the Association for Information Science and Technology (JASIST), 2018 (принята 15 июня 2017)
- **DOI:** `10.1002/asi.23930`
- Данные: in-house WoS база CWTS Leiden (2003–2012, ~9 млн статей)

---

## Суть работы (2–3 предложения)

Развивает подход Rotolo et al. (2015): **адаптирует определение emerging technology к emerging research topic** (4 атрибута: radical novelty, relatively fast growth, coherence, scientific impact — вместо uncertainty/ambiguity) и предлагает **4 количественных критерия** для идентификации emerging-тем. Метод полностью прозрачный, простой и гибкий; применён к кластерам на основе **direct citation** (метод Waltman & Van Eck) на ~9 млн статей WoS. Оценка — демонстрация на примере graphene и сравнение с предыдущими исследованиями.

---

## 1. Мотивация

- Детекция emerging-тем полезна для фондов и политиков (пример: проект ERC ERACEP 2009).
- **Проблемы по Rotolo et al. (2015):** нет общепризнанного определения emergence; неполная связь определений и индикаторов.
- **Цель:** построить связь между концепцией emerging research topic и индикаторами.

## 2. Определение и атрибуты

- Rotolo et al.: emerging technology = radical novelty + relatively fast growth + coherence + prominent impact + uncertainty/ambiguity.
- **Адаптация к теме:** scientific impact должен проявиться в **короткий период** после emergence (иначе тема не emerging; «спящие» паттерны исключаются). Атрибут uncertainty/ambiguousness малорелевантен.
- **Определение emerging research topic:** радикально новая и относительно быстро растущая тема, характеризующаяся определённой когерентностью и значительным научным влиянием.
- **4 атрибута:** radical novelty, relatively fast growth, coherence, scientific impact.

## 3. Метод

### 3.1 Построение тем
- Кластеризация методом **Waltman & Van Eck (2012, 2013)** на основе **direct citation** (вместо комбинации direct+co-citation как у Small et al. 2014 — проверка, можно ли проще).
- Обоснование direct citation: «co-citations и bibliographic coupling — более косвенные механизмы; direct citations дают более сильное указание на связанность» (Waltman & Van Eck, p. 2380); Klavans & Boyack (2015) — direct citation точнее.
- Данные: WoS CWTS Leiden 2003–2012, статьи и обзоры, ~9 млн.

### 3.2 Критерии
Для темы i в год t:
1. **Рост (Criterion I):** r_{i,t,Δt} = p*_{i,t+Δt} / p*_{i,t} ≥ r_min, где p* — **сглаженное** (среднее за 3 года) число публикаций (сглаживание убирает случайные флуктуации базы).
2. **Новизна (Criterion II):** p*_{i,t} ≤ p_max (число публикаций в начале emergence мало).
3. **Научное влияние (Criterion III):** c_{i,t,Δt} ≥ c_min (число цитирований публикаций t..t+Δt в том же окне).
4. **Когерентность (Criterion IV):** h_i ≥ h_min (общее число внутрикластерных цитирований / общее число публикаций).
- Все 4 критерия должны выполняться для одного t; записывается первый emergent-период.

### 3.3 Пример (graphene)
- Δt=2; r_min=5, p_max=100, c_min=2500, h_min=1 → graphene **emerging**; при r_min=10 → нет. **Вывод: зависит от выбора параметров.**

## 4. Оценка
- Демонстрация на примерах; сравнение с результатами предыдущих исследований (Small et al. 2014 и др.).
- Сильная сторона: полная прозрачность, простота, гибкость.

---

## Релевантность проекту

**4/5** — прямо релевантен этапу 3 (Score):
- **4 критерия** (рост, новизна, влияние, когерентность) — прямое обоснование нашего Score; наш GrowthRate/NoveltyScore + идея добавить импакт.
- **Сглаживание (3-летнее среднее)** — для нашего учёта «эха» датировки arXiv (внутренний контракт 7.1).
- **Прозрачность/гибкость параметров** — образец для калибровки нашего порога.
- **Direct citation кластеризация** — альтернатива для нашего этапа 2 (если добавим цитаты).
- **Определение «влияние в короткий период»** — методологический выбор для нашего бэктеста.

---

## Ограничения работы
- WoS до 2012 (не самые свежие данные).
- Параметры (r_min, p_max, c_min, h_min) задаются вручную — чувствительность.
- Кластеры на direct citation требуют цитатных данных (у нас arXiv без цитат — используем текст).
