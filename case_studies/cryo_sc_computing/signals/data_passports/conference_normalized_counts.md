# Нормированные частоты: «Нанофизика и наноэлектроника», Нижний Новгород

## Метод и статус
- Локальные PDF: `data/raw/conferences/Наноконференция_Новгород/`; внешних запросов: **0**.
- Извлечение: `pdftotext -enc UTF-8 input.pdf /tmp/nn_normalized_*/name.txt`, последовательно, timeout 180 с/файл.
- Фиксированные токены: `[A-Za-zА-Яа-яЁё]+`, нижний регистр; дефисы разделяют токены. Переносы слов не склеиваются.
- Термины со `*`: начало токена; SFQ-family: точные токены sfq/rsfq/esfq/ersfq (без двойного счёта).
- Каждая ячейка: **число вхождений / вхождений на 1000 слов**. Годовая частота = 1000 × сумма вхождений / сумма слов, НЕ среднее частот файлов.
- Ошибка извлечения или пустой текст: файл исключён из числителя И знаменателя; отсутствие данных НЕ равно нулю.
- Прочитано/файлов — техническое покрытие имеющихся файлов, НЕ полнота конференции или года.
- Это диагностика лексики полного текста, НЕ число докладов о вычислениях. Оглавления, библиография, реклама и повторы не исключены; полнота текстового слоя не проверена постранично.
- v1/v2 — разные тома. В 2025–2026 титулы указывают «Тезисы докладов»; смена формата ограничивает сопоставимость с трудами прошлых лет. Один файл не доказывает неполноту года.
- Размер PDF в байтах не служит мерой объёма текста. Раннее предположение, что проблемные маленькие файлы — программы, не подтвердилось: есть ошибки структуры PDF и пустое извлечение.
- **Прежний вывод conference_signal.md о подтверждённом росте именно крио/СП-вычислений этим пересчётом НЕ подтверждён.** Для него нужен тематический отбор уникальных докладов и отделение квантового управления/детекторов от классической вычислительной логики.

## Частоты

| Год | Прочитано/файлов | Слов | сверхпровод* | джозефсон* | криоген* | SFQ-family | криотрон* | квантов* |
|---|---|---|---|---|---|---|---|---|
| 2005 | 2/2 | 218589 | 127 / 0.581 | 74 / 0.339 | 3 / 0.014 | 0 / 0.000 | 0 / 0.000 | 366 / 1.674 |
| 2006 | 2/2 | 229057 | 196 / 0.856 | 68 / 0.297 | 1 / 0.004 | 16 / 0.070 | 0 / 0.000 | 384 / 1.676 |
| 2007 | 1/1 | 251371 | 304 / 1.209 | 47 / 0.187 | 2 / 0.008 | 0 / 0.000 | 0 / 0.000 | 568 / 2.260 |
| 2008 | 2/2 | 235589 | 281 / 1.193 | 42 / 0.178 | 1 / 0.004 | 0 / 0.000 | 0 / 0.000 | 438 / 1.859 |
| 2009 | 1/2 | 137471 | 185 / 1.346 | 48 / 0.349 | 1 / 0.007 | 9 / 0.065 | 0 / 0.000 | 246 / 1.789 |
| 2010 | 2/2 | 317639 | 378 / 1.190 | 93 / 0.293 | 6 / 0.019 | 0 / 0.000 | 0 / 0.000 | 702 / 2.210 |
| 2011 | 2/2 | 317259 | 415 / 1.308 | 89 / 0.281 | 15 / 0.047 | 0 / 0.000 | 10 / 0.032 | 905 / 2.853 |
| 2012 | 2/2 | 302146 | 531 / 1.757 | 158 / 0.523 | 10 / 0.033 | 8 / 0.026 | 0 / 0.000 | 746 / 2.469 |
| 2013 | 2/2 | 323140 | 596 / 1.844 | 113 / 0.350 | 9 / 0.028 | 6 / 0.019 | 0 / 0.000 | 729 / 2.256 |
| 2014 | 1/2 | 141088 | 570 / 4.040 | 91 / 0.645 | 14 / 0.099 | 2 / 0.014 | 0 / 0.000 | 128 / 0.907 |
| 2015 | 2/2 | 239452 | 381 / 1.591 | 195 / 0.814 | 14 / 0.058 | 1 / 0.004 | 0 / 0.000 | 689 / 2.877 |
| 2016 | 0/0 | н/д | н/д | н/д | н/д | н/д | н/д | н/д |
| 2017 | 0/0 | н/д | н/д | н/д | н/д | н/д | н/д | н/д |
| 2018 | 0/0 | н/д | н/д | н/д | н/д | н/д | н/д | н/д |
| 2019 | 0/2 | н/д | н/д | н/д | н/д | н/д | н/д | н/д |
| 2020 | 2/2 | 198714 | 369 / 1.857 | 93 / 0.468 | 5 / 0.025 | 0 / 0.000 | 0 / 0.000 | 169 / 0.850 |
| 2021 | 2/2 | 392095 | 468 / 1.194 | 177 / 0.451 | 14 / 0.036 | 0 / 0.000 | 0 / 0.000 | 621 / 1.584 |
| 2022 | 2/2 | 450781 | 740 / 1.642 | 197 / 0.437 | 16 / 0.035 | 6 / 0.013 | 0 / 0.000 | 635 / 1.409 |
| 2023 | 2/2 | 362162 | 671 / 1.853 | 160 / 0.442 | 22 / 0.061 | 1 / 0.003 | 0 / 0.000 | 754 / 2.082 |
| 2024 | 2/2 | 484255 | 988 / 2.040 | 318 / 0.657 | 62 / 0.128 | 23 / 0.047 | 0 / 0.000 | 927 / 1.914 |
| 2025 | 1/1 | 271628 | 691 / 2.544 | 167 / 0.615 | 29 / 0.107 | 3 / 0.011 | 0 / 0.000 | 689 / 2.537 |
| 2026 | 1/1 | 296959 | 885 / 2.980 | 108 / 0.364 | 44 / 0.148 | 18 / 0.061 | 0 / 0.000 | 846 / 2.849 |

## Контроль файлов

| Файл | Статус | Слов извлечено | Диагностика |
|---|---|---:|---|
| 2005_v1.pdf | OK | 100741 | Syntax Error: Unknown character collection 'PDFXC-Indentity0' Syntax Error: Unknown character collection 'PDFXC-Indentity0' Syntax Error: Unknown character collection 'PDFXC-Indentity0' Syntax Error: Unknown character collection 'PDFXC-Indentity0' |
| 2005_v2.pdf | OK | 117848 | Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error |
| 2006_v1.pdf | OK | 114151 | Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error |
| 2006_v2.pdf | OK | 114906 | Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not  |
| 2007.pdf | OK | 251371 | Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not  |
| 2008_v1.pdf | OK | 116851 | Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error |
| 2008_v2.pdf | OK | 118738 | Syntax Warning: Mismatch between font type and embedded font file Syntax Error: Unknown character collection 'TimesNewRomanPS-BoldMT-TimesNewRomanPS-BoldMT' Syntax Warning: Mismatch between font type and embedded font file Syntax Error: Unknown character collection 'TimesNewRomanPSMT-TimesNewRomanPSMT' Syntax Warning: Mismatch between font type and |
| 2009_v1.pdf | OK | 137471 | Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not an ICC profile, invalid signature Syntax Warning: read ICCBased color space profile error Syntax Warning: not  |
| 2009_v2.pdf | EMPTY | 0 | Internal Error: xref num 26048 not found but needed, try to reconstruct<0a> Syntax Error: Kid object (page 1) is wrong type (null) Syntax Error: Kid object (page 1) is wrong type (null) |
| 2010_v1.pdf | OK | 152044 | — |
| 2010_v2.pdf | OK | 165595 | — |
| 2011_v1.pdf | OK | 162531 | Syntax Error (869891): Illegal character <54> in hex string Syntax Error (869893): Illegal character <28> in hex string Syntax Error (869895): Illegal character <2c> in hex string Syntax Error (869895): Illegal character <29> in hex string Syntax Error (869897): Illegal character <54> in hex string Syntax Error (869897): Illegal character <6a> in h |
| 2011_v2.pdf | OK | 154728 | Syntax Error (15266877): Too many args in content stream Syntax Error (15266880): Too many args in content stream Syntax Error (15266881): Too many args in content stream Syntax Error (15266883): Too many args in content stream Syntax Error (15266885): Too many args in content stream Syntax Error (15266887): Too many args in content stream Syntax E |
| 2012_v1.pdf | OK | 158200 | Syntax Error: Expected the optional content group list, but wasn't able to find it, or it isn't an Array Syntax Error (9489924): Illegal character ')' Syntax Error (9489924): Dictionary key must be a name object Syntax Error (9489936): Dictionary key must be a name object Syntax Error (9489936): Illegal character '{' Syntax Error (9489936): Diction |
| 2012_v2.pdf | OK | 143946 | Syntax Error (386053): Missing 'endstream' or incorrect stream length Syntax Error (383541): Unknown operator 'q0' Syntax Error (383560): Unknown operator 'q0' Syntax Error (383579): Unknown operator 'q0' Syntax Error (383613): Too few (1) args to 'm' operator Syntax Error: XObject 'Fm1' is unknown Syntax Error (388358): Unknown operator 'gs8' Synt |
| 2013_v1.pdf | OK | 163883 | Syntax Error (654854): Missing 'endstream' or incorrect stream length Syntax Error (654337): Too few (1) args to 'd' operator Syntax Error (82045458): Illegal character '{' Syntax Error (82045458): Missing 'endstream' or incorrect stream length Syntax Error (82045458): Unexpected end of file in flate stream Syntax Warning: Illegal entry in bfrange  |
| 2013_v2.pdf | OK | 159257 | Syntax Error (2170372): Illegal character '>' Syntax Error (2170372): Illegal character '>' Syntax Error (2170373): Unknown operator 'A' Syntax Error (2170415): Too many args in content stream Syntax Error (2170417): Too many args in content stream Syntax Error (2170417): Too many args in content stream Syntax Error (2170419): Too many args in cont |
| 2014_v1.pdf | OK | 141088 | — |
| 2014_v2.pdf | ERROR | 0 | Syntax Error: Couldn't find trailer dictionary Syntax Error: Invalid XRef entry 15898 Syntax Error: Invalid XRef entry 15812 Syntax Error: Top-level pages object is wrong type (null) Command Line Error: Wrong page range given: the first page (1) can not be after the last page (0). |
| 2015_v1.pdf | OK | 94576 | — |
| 2015_v2.pdf | OK | 144876 | — |
| 2019_v1.pdf | ERROR | 0 | Syntax Error: Couldn't find trailer dictionary Syntax Error: Couldn't find trailer dictionary Syntax Error: Couldn't read xref table |
| 2019_v2.pdf | ERROR | 0 | Syntax Error: Couldn't find trailer dictionary Syntax Error: Couldn't find trailer dictionary Syntax Error: Couldn't read xref table |
| 2020_v1.pdf | OK | 129949 | — |
| 2020_v2.pdf | OK | 68765 | — |
| 2021_v1.pdf | OK | 201323 | — |
| 2021_v2.pdf | OK | 190772 | — |
| 2022_v1.pdf | OK | 248179 | Syntax Warning: Invalid Font Weight Syntax Warning: Invalid Font Weight Syntax Warning: Invalid Font Weight |
| 2022_v2.pdf | OK | 202602 | — |
| 2023_v1.pdf | OK | 184859 | — |
| 2023_v2.pdf | OK | 177303 | — |
| 2024_v1.pdf | OK | 252026 | — |
| 2024_v2.pdf | OK | 232229 | — |
| 2025.pdf | OK | 271628 | — |
| 2026.pdf | OK | 296959 | — |
