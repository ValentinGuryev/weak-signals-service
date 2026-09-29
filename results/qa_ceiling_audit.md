# Аудит потолка покрытия QA-теста «Защита ИИ» (23.09.2026)

> Вопрос автора: «покрытие реально маленькое или это проблема другой формулировки той же темы?»
> Метод: (1) широкие словари синонимов по полному blob темы (name+description+keywords,
> 4482 темы); (2) семантический топ-6 LaBSE от формулировки организатора (RU и EN);
> (3) точные фразы (red team, MCP, EU AI Act, unlearning, RAG, prompt injection, LLM, AI safety).

## Итог: потолок 12/16 (честные эквиваленты), 13/16 — с единственной натяжкой; 80% = 13

### Tier A — тема ЕСТЬ напрямую (другое название того же) — 7 шт.
| # | Тема организатора | Тема в базе |
|---|---|---|
| 2 | IAM для ИИ-агентов | T10927 Access Control and Trust, T11800 User Authentication and Security Systems |
| 20 | LLM-файрволы | T10400 Network Security and Intrusion Detection, T13983 Cybersecurity and Information Systems (в T12326 буквально «firewall») |
| 22 | AI-governance / EU AI Act | T14264 Law, Ethics, and AI Impact; T13851 Law, AI, and Intellectual Property; T10883 Ethics and Social Impacts of AI |
| 23 | Дифф. приватность / синтет. данные | T10764 Privacy-Preserving Technologies in Data |
| 24 | Конфиденциальный инференс (TEE) | T10237 Cryptography and Data Security (homomorphic encryption), T11424 Security and Verification in Computing (trusted execution) |
| 25 | Водяные знаки текста LLM | T10388 Advanced Steganography and Watermarking Techniques |
| 49 | Интерпретируемость как контроль | **T12026 Explainable Artificial Intelligence (XAI)** |

### Tier B — эквивалент защищённо обосновываем — 5 шт.
| # | Тема организатора | Эквивалент | Обоснование |
|---|---|---|---|
| 3 | Red-teaming ИИ-моделей | T11689 Adversarial Robustness in ML | то же семейство «атаки/стресс-тесты моделей» |
| 21 | Prompt injection | T11689 (adversarial attacks on models) | промпт-инъекция = атака на модель; отдельной NLP-темы нет |
| 50 | Крипто-верификация трафика агентов | T11504 Advanced Authentication Protocols Security, T10951 Cryptographic Implementations and Security | аутентификация/криптопротоколы = та же тема без «агентного» ярлыка |
| 51 | Подпись моделей / AI-SBOM | T11693 Cryptography and Residue Arithmetic (public key), T10951 | цифровая подпись/провенанс криптографический; «software supply chain» как темы НЕТ |
| 77 | Сканирование бэкдоров моделей | T11241 Advanced Malware Detection Techniques, T12122 (hardware trojan) | обнаружение вредоносного кода/backdoor; домен «железо/ПО», не «веса LLM» |

### Tier C — натяжка (спорно) — 1 шт.
| # | Тема | Эквивалент | Почему натяжка |
|---|---|---|---|
| 4 | Сканеры MCP-серверов / tool poisoning | T13983 Cybersecurity and Information Systems | generic-кибербезопасность ≠ безопасность MCP; AI/MCP-specific темы в базе нет (0 совпадений model context protocol / tool poisoning / LLM+security) |

### ❌ АБСОЛЮТНО ОТСУТСТВУЮТ (другая формулировка не спасает) — 3 шт.
| # | Тема | Доказательства 0 совпадений |
|---|---|---|
| 48 | Machine unlearning | unlearn / forgetting / data erasure / data deletion / right to be forgotten — 0; семантика RU/EN → мусор (Financial Distress, Machine Fault Diagnosis) |
| 52 | Мониторинг CoT / scheming | chain-of-thought — 0; hallucination → только медицинский; deception → только forensic psychology (T12268 — ДРУГАЯ тема) |
| 76 | Отравление памяти агентов / RAG | retrieval-augmented / RAG — 0; poisoning → только токсины/растения/Smart Grid; data poisoning ML — 0 |

### Контекст (почему так): таксономия пред-Llama-волны
- `\bLLM\b`/large language model/foundation model во всём blob — **2 совпадения, оба ложных** (GANs, Nonlinear Dynamics).
- `AI safety|AI alignment` — **0**. Red team — 0. Jailbreak — 0. MCP — 0. EU AI Act — 0. Unlearning — 0. RAG — 0.
- Темы-«ядра» защиты ИИ 2024–2026 просто не успели войти в 4482 кластера OpenAlex.

### ⚠️ Ложные срабатывания первоначального скорера (нужно чинить — завышали покрытие)
- #2: «authentication» в Spectroscopy/Currency Detection (не про IAM);
- #49: «interpret» в Legal Language/Archaeology/Cardiology (не про XAI) — спасает только T12026;
- #51: «supply chain» в логистике/трейде (не про software provenance);
- #52: deception в forensic psychology (не про scheming) — по сути ЛОЖНОЕ «да»;
- #77: trojan только в PUF/hardware (близко, но не веса моделей); #21: injection в Smart Grid (ЛОЖНОЕ «да»).

## Вывод
1. **Часть потолка — формулировка** (Tier A+B): с эквивалентами 11 → **12/16**, с Tier C → 13/16.
2. **Но 3 темы (#48, #52, #76) отсутствуют категорически** — жёсткий потолок **13/16**, и это
   достичь можно только засчитав Tier C. Без натяжек — **12/16 = 75% < 80%**.
3. Ограничение — **данные** (таксономия без LLM-security тем), НЕ формулировка запроса и НЕ качество ретривала.
4. Отдельно: ранги нужных тем у тестового запроса плохие (медиана 251) — ретвивал-тюнинг нужен в любом случае.

## Решение автора требуется
Как считать для порога 80%: (а) строго по Tier A+B = 12/16 — тест НЕ пройти никогда;
(б) + Tier C = 13/16 — проходимость на грани, один спорный засчёт; (в) иной критерий.
