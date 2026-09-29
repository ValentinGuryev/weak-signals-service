# Симуляция гейта релевантности (P1)

Окно Y=2025, топ-50. rel = IDF-покрытие лексики запроса профилем темы (имя + топ-100 работ).

## q1_ru_canonical

Запрос: Выдай темы по защите ИИ в 2026 году

| вариант | покрытие | мусор в топ-50 |
|---|---|---|
| base | 2/12 ❌ | 14 |
| gate | 2/12 ❌ | 13 |
| win100 | 8/12 ❌ | 8 |
| win250 | 6/12 ❌ | 10 |
| win400 | 4/12 ❌ | 11 |
| fusion | 4/12 ❌ | 11 |
| gate+fusion | 4/12 ❌ | 11 |
| win50fusion | 5/12 ❌ | 7 |
| win50fusion_mlex | 5/12 ❌ | 7 |
| win100fusion | 8/12 ❌ | 9 |
| win100fusion_mlex | 8/12 ❌ | 8 |

### Топ-15 (base)

1. T13880 Innovative Education Methods and Tools — screen=0.0115, rel=0.014, retr_rank=332
2. T13345 Advanced Technologies and Applied Computing — screen=0.0038, rel=0.056, retr_rank=442
3. T14496 Educational Technology and E-Learning — screen=0.0019, rel=0.019, retr_rank=458
4. T14262 Extenics and Innovation Methods — screen=0.0017, rel=0.026, retr_rank=742
5. T10388 Advanced Steganography and Watermarking Techniques — screen=0.0015, rel=0.058, retr_rank=408
6. T14443 COVID-19, Geopolitics, Technology, Migration — screen=0.0014, rel=0.003, retr_rank=400
7. T13957 Corporate Governance and Financial Management — screen=0.0012, rel=0.033, retr_rank=83
8. T14413 Advanced Technologies in Various Fields — screen=0.0009, rel=0.055, retr_rank=51
9. T13647 AI and Big Data Applications — screen=0.0007, rel=0.040, retr_rank=678
10. T12958 Digital Economy and Transformation — screen=0.0002, rel=0.019, retr_rank=278
11. T14161 Health and Education Studies — screen=0.0002, rel=0.000, retr_rank=450
12. T14100 Scientific Research and Technology — screen=0.0002, rel=0.025, retr_rank=92
13. T13541 IoT-based Control Systems — screen=0.0002, rel=0.023, retr_rank=380
14. T14435 Information Retrieval and Data Mining — screen=0.0002, rel=0.032, retr_rank=339
15. T13567 AI and Multimedia in Education — screen=0.0002, rel=0.050, retr_rank=549

### Топ-15 (win100)

1. T13957 Corporate Governance and Financial Management — screen=0.0012, rel=0.033, retr_rank=83
2. T14413 Advanced Technologies in Various Fields — screen=0.0009, rel=0.055, retr_rank=51
3. T14100 Scientific Research and Technology — screen=0.0002, rel=0.025, retr_rank=92
4. T11714 Multimodal Machine Learning Applications — screen=0.0001, rel=0.022, retr_rank=6
5. T11273 Advanced Graph Neural Networks — screen=0.0001, rel=0.028, retr_rank=14
6. T10714 Software-Defined Networks and 5G — screen=0.0000, rel=0.014, retr_rank=99
7. T10036 Advanced Neural Network Applications — screen=0.0000, rel=0.023, retr_rank=3
8. T14240 E-Learning and COVID-19 — screen=0.0000, rel=0.015, retr_rank=31
9. T11835 Sustainability in Higher Education — screen=0.0000, rel=0.028, retr_rank=86
10. T10775 Generative Adversarial Networks and Image Synthesis — screen=0.0000, rel=0.041, retr_rank=7
11. T10273 IoT and Edge/Fog Computing — screen=0.0000, rel=0.013, retr_rank=45
12. T10764 Privacy-Preserving Technologies in Data — screen=0.0000, rel=0.053, retr_rank=59
13. T10812 Human Pose and Action Recognition — screen=0.0000, rel=0.015, retr_rank=84
14. T11101 Online Learning Methods and Innovations — screen=0.0000, rel=0.008, retr_rank=22
15. T11133 UAV Applications and Optimization — screen=0.0000, rel=0.015, retr_rank=63

## q2_ru_long

Запрос: Безопасность искусственного интеллекта: защита языковых моделей от атак и инъекций промптов, приватность данных, регулирование и надёжность ИИ-систем

| вариант | покрытие | мусор в топ-50 |
|---|---|---|
| base | 3/12 ❌ | 7 |
| gate | 3/12 ❌ | 6 |
| win100 | 8/12 ❌ | 9 |
| win250 | 7/12 ❌ | 8 |
| win400 | 6/12 ❌ | 8 |
| fusion | 5/12 ❌ | 6 |
| gate+fusion | 5/12 ❌ | 6 |
| win50fusion | 5/12 ❌ | 5 |
| win50fusion_mlex | 5/12 ❌ | 5 |
| win100fusion | 8/12 ❌ | 8 |
| win100fusion_mlex | 8/12 ❌ | 8 |

### Топ-15 (base)

1. T13880 Innovative Education Methods and Tools — screen=0.0115, rel=0.012, retr_rank=295
2. T13345 Advanced Technologies and Applied Computing — screen=0.0038, rel=0.045, retr_rank=384
3. T14496 Educational Technology and E-Learning — screen=0.0019, rel=0.016, retr_rank=396
4. T14262 Extenics and Innovation Methods — screen=0.0017, rel=0.021, retr_rank=612
5. T10388 Advanced Steganography and Watermarking Techniques — screen=0.0015, rel=0.046, retr_rank=359
6. T13957 Corporate Governance and Financial Management — screen=0.0012, rel=0.027, retr_rank=80
7. T14413 Advanced Technologies in Various Fields — screen=0.0009, rel=0.045, retr_rank=50
8. T13647 AI and Big Data Applications — screen=0.0007, rel=0.031, retr_rank=558
9. T12958 Digital Economy and Transformation — screen=0.0002, rel=0.016, retr_rank=255
10. T14161 Health and Education Studies — screen=0.0002, rel=0.000, retr_rank=389
11. T14100 Scientific Research and Technology — screen=0.0002, rel=0.021, retr_rank=84
12. T13541 IoT-based Control Systems — screen=0.0002, rel=0.018, retr_rank=338
13. T14435 Information Retrieval and Data Mining — screen=0.0002, rel=0.026, retr_rank=302
14. T13567 AI and Multimedia in Education — screen=0.0002, rel=0.039, retr_rank=457
15. T11714 Multimodal Machine Learning Applications — screen=0.0001, rel=0.017, retr_rank=6

### Топ-15 (win100fusion)

1. T14413 Advanced Technologies in Various Fields — screen=0.0009, rel=0.045, retr_rank=50
2. T13957 Corporate Governance and Financial Management — screen=0.0012, rel=0.027, retr_rank=80
3. T14100 Scientific Research and Technology — screen=0.0002, rel=0.021, retr_rank=84
4. T11714 Multimodal Machine Learning Applications — screen=0.0001, rel=0.017, retr_rank=6
5. T11273 Advanced Graph Neural Networks — screen=0.0001, rel=0.022, retr_rank=12
6. T10775 Generative Adversarial Networks and Image Synthesis — screen=0.0000, rel=0.033, retr_rank=7
7. T10036 Advanced Neural Network Applications — screen=0.0000, rel=0.018, retr_rank=3
8. T10714 Software-Defined Networks and 5G — screen=0.0000, rel=0.012, retr_rank=90
9. T10764 Privacy-Preserving Technologies in Data — screen=0.0000, rel=0.043, retr_rank=57
10. T14064 Organizational and Employee Performance — screen=0.0000, rel=0.049, retr_rank=49
11. T14240 E-Learning and COVID-19 — screen=0.0000, rel=0.013, retr_rank=28
12. T12026 Explainable Artificial Intelligence (XAI) — screen=0.0000, rel=0.034, retr_rank=4
13. T10273 IoT and Edge/Fog Computing — screen=0.0000, rel=0.010, retr_rank=43
14. T12128 AI in Service Interactions — screen=0.0000, rel=0.023, retr_rank=5
15. T10883 Ethics and Social Impacts of AI — screen=0.0000, rel=0.040, retr_rank=1

## q3_en

Запрос: AI security and safety: protecting language models from attacks, prompt injection defense, privacy-preserving AI, AI governance and regulation, reliable trustworthy AI

| вариант | покрытие | мусор в топ-50 |
|---|---|---|
| base | 4/12 ❌ | 5 |
| gate | 4/12 ❌ | 4 |
| win100 | 8/12 ❌ | 8 |
| win250 | 7/12 ❌ | 6 |
| win400 | 6/12 ❌ | 6 |
| fusion | 5/12 ❌ | 4 |
| gate+fusion | 5/12 ❌ | 4 |
| win50fusion | 5/12 ❌ | 5 |
| win50fusion_mlex | 5/12 ❌ | 5 |
| win100fusion | 8/12 ❌ | 7 |
| win100fusion_mlex | 8/12 ❌ | 7 |

### Топ-15 (base)

1. T13880 Innovative Education Methods and Tools — screen=0.0115, rel=0.014, retr_rank=294
2. T13345 Advanced Technologies and Applied Computing — screen=0.0038, rel=0.051, retr_rank=392
3. T14496 Educational Technology and E-Learning — screen=0.0019, rel=0.018, retr_rank=402
4. T14262 Extenics and Innovation Methods — screen=0.0017, rel=0.025, retr_rank=620
5. T10388 Advanced Steganography and Watermarking Techniques — screen=0.0015, rel=0.060, retr_rank=366
6. T13957 Corporate Governance and Financial Management — screen=0.0012, rel=0.032, retr_rank=71
7. T14413 Advanced Technologies in Various Fields — screen=0.0009, rel=0.052, retr_rank=46
8. T13647 AI and Big Data Applications — screen=0.0007, rel=0.036, retr_rank=567
9. T12958 Digital Economy and Transformation — screen=0.0002, rel=0.018, retr_rank=254
10. T14161 Health and Education Studies — screen=0.0002, rel=0.000, retr_rank=397
11. T14100 Scientific Research and Technology — screen=0.0002, rel=0.023, retr_rank=75
12. T13541 IoT-based Control Systems — screen=0.0002, rel=0.021, retr_rank=342
13. T14435 Information Retrieval and Data Mining — screen=0.0002, rel=0.030, retr_rank=302
14. T13567 AI and Multimedia in Education — screen=0.0002, rel=0.045, retr_rank=469
15. T11714 Multimodal Machine Learning Applications — screen=0.0001, rel=0.020, retr_rank=7

### Топ-15 (win100fusion)

1. T14413 Advanced Technologies in Various Fields — screen=0.0009, rel=0.052, retr_rank=46
2. T13957 Corporate Governance and Financial Management — screen=0.0012, rel=0.032, retr_rank=71
3. T14100 Scientific Research and Technology — screen=0.0002, rel=0.023, retr_rank=75
4. T11714 Multimodal Machine Learning Applications — screen=0.0001, rel=0.020, retr_rank=7
5. T11273 Advanced Graph Neural Networks — screen=0.0001, rel=0.026, retr_rank=12
6. T10775 Generative Adversarial Networks and Image Synthesis — screen=0.0000, rel=0.038, retr_rank=8
7. T10764 Privacy-Preserving Technologies in Data — screen=0.0000, rel=0.062, retr_rank=54
8. T10036 Advanced Neural Network Applications — screen=0.0000, rel=0.021, retr_rank=4
9. T10714 Software-Defined Networks and 5G — screen=0.0000, rel=0.013, retr_rank=81
10. T14064 Organizational and Employee Performance — screen=0.0000, rel=0.057, retr_rank=45
11. T12026 Explainable Artificial Intelligence (XAI) — screen=0.0000, rel=0.039, retr_rank=5
12. T10273 IoT and Edge/Fog Computing — screen=0.0000, rel=0.012, retr_rank=41
13. T12128 AI in Service Interactions — screen=0.0000, rel=0.026, retr_rank=6
14. T10812 Human Pose and Action Recognition — screen=0.0000, rel=0.015, retr_rank=72
15. T10883 Ethics and Social Impacts of AI — screen=0.0000, rel=0.045, retr_rank=2

