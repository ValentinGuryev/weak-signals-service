# Паспорт: разведка публикационного сигнала (S1a) — кейс #87 крио/СП-вычисления

- Файл: `signals/s1a_pub_terms_counts.json`
- Скрипт: разведочный (2026-09-16), OpenAlex `works?filter=title_and_abstract.search:Q&group_by=publication_year`
- Запросы (8): cryogenic_computing, superconducting_logic, cryo_cmos, rql, aqfp,
  energy_eff_sc_digital, cryo_datacenter, snowcap
- Дата: 2026-09-16 · API-бюджет: 8 разведочных запросов (free API, rate-limit 0.4с)
- Поля: year → count по термину (без полного select; полный корпус — отдельным шагом, по согласованию)
- Восстановление: повторить запросы выше (через API): `filter=title_and_abstract.search:"<термин>"&group_by=publication_year`
