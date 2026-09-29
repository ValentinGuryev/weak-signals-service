# Wishlist: Key Literature for Case #87 (Cryo/SC Computing)

> Актуализировано: 2026-09-17 (после закрытия 13 выжимок литературы кейса).
> По правилу §4.2a — здесь ТОЛЬКО документы, которых у нас НЕТ (не скачаны / не в библиотеке).
> Скачанные и обработанные (13 PDF + выжимки) в wishlist НЕ перечисляются (см. строку «Вычищено» ниже).

## 1. Недостающие обзоры / дорожные карты («архитекторы»)

| Title | Authors | Journal/Source | Year | DOI/URL | Релевантность | Зачем нужен | Статус |
|:---|:---|:---|:---|:---|:---|:---|:---|
| Cryogenic electronics for high performance computing applications: A comprehensive review | Faisal Bashir, Haider Abbas, Arshid Nisar, Usman Isyaku Bature, Ali Alzahrani, Furqan Zahoor | Materials Today Physics | 2025 | [10.1016/j.mtphys.2025.101960](https://doi.org/10.1016/j.mtphys.2025.101960) | !!! (5/5) | Систематический обзор крио-электроники именно для HPC (не квантовых) — прямой аналог Kawabata для классического/ИИ-сектора; автор F. Bashir — соавтор уже скачанного обзора RRAM (d4na00158c), но ЭТА статья — целевая и ещё не получена | 📥 скачать |
| SuperMind: a survey of the potential of superconducting electronics for neuromorphic computing | Michael L. Schneider, Emily Toomey, Graham Rowlands, Jeff Shainline, et al. | J. Phys.: Condens. Matter | 2022 | [10.1088/1361-6668/ac4cd2](https://doi.org/10.1088/1361-6668/ac4cd2) | !! (4/5) | Обзор СП-электроники для нейроморфных/ИИ-вычислений — обоснование «СП-логика для ИИ-нагрузок»; связывает кейс #87 с ИИ-сценарием (XNOR-Net, нейросети) | 📥 скачать |
| Hybrid Cryogenic Memory Cells for Superconducting Computing Applications | Jeng-Bang Yau, Yat-Kiu-Kent Fung, Gerald W. Gibson | IEEE ICRC | 2017 | [10.1109/icrc.2017.8123684](https://doi.org/10.1109/icrc.2017.8123684) | !! (4/5) | Гибридные крио-ячейки памяти (2017, до окна сигнала) — «пионер» гибридного подхода; точка отсчёта для S2/S1a | 📥 скачать |

## 2. Недостающие конкретные работы (по инсайтам из выжимок)

| Title | Authors | Journal/Source | Year | DOI/URL | Релевантность | Зачем нужен | Статус |
|:---|:---|:---|:---|:---|:---|:---|:---|
| An energy-efficient 32-bit bit-parallel superconducting SFQ specialized processor | Qu Peiyao, Liu Huanli, Zheng Xiangyu, et al. | Superconductivity | 2024 | DOI в самом PDF (кнт. журнал); см. кит. обзор Li Feng, ref [6] | !!! (5/5) | **Рекорд «снятия предела» на уровне чипа**: 32-бит SFQ-процессор, 12 ГГц / 251 GOPS/W (инсайт из Li Feng) — ключевой S4-факт | ⛔ платно (было 403) → 🔶 пробовать Sci-Hub/перевод |
| Heat Load Efficiency in Multi-Temperature Cryogenic Computing | N. Zhuldassov, R. Bairamkulov, E.G. Friedman | Cryogenics | 2024 (in review) | см. диссертацию Zhuldassov, ref [11] | !!! (5/5) | Статья-компаньон диссертации: энергоэффективность тепловой нагрузки многотемпературных систем; **уже покрыта диссертацией** (тот же контент) → строка для контроля, но НЕ критична | ⚠️ покрыто диссертацией (2024 Zhuldassov) — не нужно |
| Materials for quantum technologies: A roadmap for spin and topology | Niladri Banerjee, et al. | (Roadmap) | 2025 | 10.1063/5.0294020 | ! (3/5) | Дорожная карта материалов для квантовых (спин/топология) — фон для «крио-материалов», менее критично | 📥 скачать (низкий приоритет) |

## 3. Приоритеты скачивания (сводно)

1. **Bashir 2025 (mtphys.2025.101960)** — 📥 целевой обзор крио-электроники для HPC; аналог Kawabata для классического сектора. **Самый приоритетный.**
2. **Schneider 2022 SuperMind (ac4cd2)** — 📥 СП-нейроморф для ИИ.
3. **Yau 2017 (ICRC.8123684)** — 📥 гибридная крио-память (пионер 2017).
4. **Qu 2024 (SFQ-процессор 12 ГГц/251 GOPS/W)** — 🔶 платно; пробовать Sci-Hub/перевод; S4-рекорд уровня чипа.
5. **Banerjee 2025 (roadmap)** — 📥 низкий приоритет.

---
> **Вычищено из wishlist (2026-09-17):** Bao 2024 (Nat. Comm.); Alam & Aziz 2024 (XNOR hTron); Golod 2023 (вихревая память 1×1 мкм²); Volk 2023 (линии задержки); Kalashnikov 2024 (СВЧ-чтение); Soloviev 2017 (обзор СП-логики/памяти); Reilly 2015 (квантово-классический интерфейс); Kawabata 2026 (IEICE обзор); Li Feng & Peng Wei 2026 (кит. обзор памяти); Wu 2026 UTe₂ (arXiv:2603.02450); Zhuldassov 2024 (PhD-диссертация Rochester) — все скачаны, имеют выжимки, в wishlist больше не входят.
> Дополнительно: строка «Zhuldassov 2024 Cryogenics» помечена покрытой диссертацией; «Bao 2024» и «Alam&Aziz 2024» из прошлого wishlist — обработаны (выжимки готовы). Дубль F7506AB/jfmd — убран в `_rejected/`.