"""Парсер РНФ (rscf.ru) — полные карточки проектов по ключевым словам.

Этап 1: поиск по ключевому слову на /project/, сбор номеров проектов + базовых полей из таблицы.
Этап 2: для каждого проекта открываем карточку, вытаскиваем:
  - общие сведения (номер, название, руководитель, организация, конкурс, классификатор, ключевые слова, ГРНТИ)
  - аннотацию из заявки
  - публикации по гранту (авторы, название, журнал, год, DOI)

Структура карточки (проверено 2026-08-17):
  <span class="fld_title">Имя поля</span> ... текст
  Аннотация: <span class="fld_title">Аннотация</span><br><span style="white-space: pre-wrap;">ТЕКСТ</span>
  Публикации: блоки <div><p><span><b>N.</b> <em>авторы</em> <b>название</b> журнал (год) <a href=DOI>

Запуск:
    LD_LIBRARY_PATH=... .venv/bin/python src/rnf_parser.py --keywords "сверхпроводимость" --out ...
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

BASE_URL = "https://rscf.ru/project/"


# --- парсинг таблицы результатов -------------------------------------------
def parse_table(text: str) -> list[dict]:
    """Парсим таблицу результатов (inner_text) в список проектов.

    Формат строки: №\tНомер\tНазвание\nРуководитель\tосновной:\nКоды\tКонкурс\tОрганизация
    """
    projects = []
    lines = text.split("\n")
    pat = re.compile(r"^(\d+)\t(\d{2}-\d{2}-\d{5})\t(.+)$")
    for i, line in enumerate(lines):
        m = pat.match(line)
        if m:
            number = m.group(2)
            title = m.group(3).strip()
            leader = lines[i + 1].strip() if i + 1 < len(lines) else ""
            projects.append({"number": number, "title": title, "leader": leader})
    return projects


# --- парсинг карточки проекта ----------------------------------------------
def parse_card(page) -> dict:
    """Собираем все поля карточки проекта. page должен быть на странице карточки."""
    info: dict = {}

    # 1) общие сведения: все <span class="fld_title">Имя</span> + следующий текст
    flds = page.locator("span.fld_title")
    n = flds.count()
    for i in range(n):
        name = flds.nth(i).inner_text(timeout=3000).strip()
        # текст поля = текст родительского <p> без заголовка
        p = flds.nth(i).locator("xpath=..")
        full = p.inner_text(timeout=3000).strip()
        # убрать первое вхождение заголовка
        val = full[len(name):].strip() if full.startswith(name) else full
        # почистить мусор «№1 -» в конкурсе, «, регион»
        val = re.sub(r"^\s*№\d+\s*-\s*", "", val)
        val = re.sub(r"\s+", " ", val).strip()
        info[name] = val

    # 2) аннотация: <span class="fld_title">Аннотация</span><br><span style="white-space: pre-wrap;">
    ann = page.locator('span.fld_title:text("Аннотация") ~ span[style*="pre-wrap"]')
    if ann.count():
        info["Аннотация"] = ann.first.inner_text(timeout=5000).strip()
    # fallback: ищем pre-wrap спан рядом с «Аннотация»
    if "Аннотация" not in info:
        try:
            lbl = page.locator('span.fld_title:text("Аннотация")').first
            par = lbl.locator("xpath=..")
            info["Аннотация"] = par.inner_text(timeout=3000).replace("Аннотация", "", 1).strip()
        except Exception:
            pass

    # 3) публикации: блоки <div><p><span><b>N.</b> ... <a href=DOI>
    pubs = []
    pub_divs = page.locator("div p span:has(b)").filter(has_text="год публикации")
    m = pub_divs.count()
    for j in range(m):
        el = pub_divs.nth(j)
        txt = el.inner_text(timeout=3000).strip()
        doi_a = el.locator("a")
        doi = doi_a.get_attribute("href") if doi_a.count() else ""
        doi = doi.replace("https://doi.org/", "") if doi else ""
        pubs.append({"text": txt, "doi": doi})
    info["Публикации"] = pubs

    # маппинг: нормализованные поля для единообразия
    if "Название" in info and "title" not in info:
        info["title"] = info["Название"]
    if "Руководитель" in info and "leader" not in info:
        info["leader"] = info["Руководитель"]

    return info


# --- основной цикл ----------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Парсер РНФ (полные карточки)")
    ap.add_argument("--keywords", default="сверхпроводимость", help="ключевые слова через запятую")
    ap.add_argument("--max-pages", type=int, default=20, help="макс. число страниц поиска")
    ap.add_argument("--max-cards", type=int, default=0, help="макс. число карточек (0 = все)")
    ap.add_argument("--out", default="data/raw/rnf/rnf_results.json")
    args = ap.parse_args()

    keywords = args.keywords
    all_projects: dict[str, dict] = {}  # number -> record

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(BASE_URL, timeout=45000)
        page.wait_for_load_state("networkidle", timeout=30000)

        page.locator("#keywords-select").fill(keywords)
        time.sleep(2)
        page.click("#search-projects-btn")
        logger.info("Поиск по '%s' запущен", keywords)
        time.sleep(10)

        # страницы таблицы — РНФ отдаёт максимум 25 строк одним запросом, пагинация не работает
        ft = page.locator("#filtered-table")
        if ft.count() == 0 or not ft.inner_text(timeout=5000).strip():
            logger.error("Результаты не появились")
            browser.close()
            return

        text = ft.inner_text(timeout=5000)
        proj = parse_table(text)
        for x in proj:
            all_projects[x["number"]] = {"number": x["number"], "title": x["title"], "leader": x["leader"]}
        logger.info("Таблица: %d проектов (лимит РНФ = 25, пагинация не работает)", len(all_projects))

        # соберём ссылки на карточки из DOM таблицы (номер -> href)
        hrefs: dict[str, str] = {}
        links = ft.locator('a[href*="/project/"]')
        for i in range(links.count()):
            a = links.nth(i)
            num_txt = a.inner_text(timeout=3000).strip()
            href = a.get_attribute("href")
            if num_txt and href and re.match(r"\d{2}-\d{2}-\d{5}", num_txt):
                hrefs[num_txt] = href
        logger.info("Ссылок на карточки: %d", len(hrefs))

        # --- карточки ---
        items = list(all_projects.items())
        if args.max_cards:
            items = items[: args.max_cards]
        for idx, (num, rec) in enumerate(items, 1):
            href = hrefs.get(num)
            if not href:
                logger.warning("Нет ссылки для %s — пропуск", num)
                continue
            try:
                page.goto("https://rscf.ru" + href, timeout=45000)
                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(2)
                card = parse_card(page)
                rec.update({k: v for k, v in card.items() if v})
            except Exception as e:
                logger.warning("Карточка %s: %s", num, str(e)[:100])
            if idx % 5 == 0:
                logger.info("Карточки: %d/%d", idx, len(items))

        browser.close()

    out = {
        "method": "rnf_parser_cards",
        "keywords": keywords,
        "source": BASE_URL,
        "n_projects": len(all_projects),
        "projects": list(all_projects.values()),
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено %d проектов (с карточками) → %s", len(all_projects), out_path)


if __name__ == "__main__":
    main()
