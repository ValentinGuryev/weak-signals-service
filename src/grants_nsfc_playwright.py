"""NSFC (Китай) — гранты через браузер (Playwright), v8: парсинг сырого текста с \n.

Структура блока (из отладки):
  1.Название проекта
  批准号：12075270
  申请代码：A2804
  项目类别： 面上项目
  项目负责人： 沙鹏
  资助经费：63.0（万元）
  批准年度：2020
  结题年度：2024
  依托单位： 中国科学院高能物理研究所
  关键词： 谐振腔； 轴子； ...
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

KEYWORDS = ["超导", "高温超导", "超导量子比特", "超导磁铁", "磁通钉扎", "约瑟夫森结", "超导带材", "拓扑超导", "离子束辅助", "织构基带", "涂层导体", "第二代高温超导带材"]


def extract_fields(block: str) -> dict:
    d: dict = {}
    def grab(pat: str, key: str) -> None:
        m = re.search(pat, block)
        if m:
            d[key] = re.sub(r"\s+", " ", m.group(1)).strip()

    # title: «N.Название» до «批准号»
    m = re.search(r"\d+\.(.+?)\s*批准号[:：]", block, re.S)
    if not m:
        m = re.search(r"(.+?)\s*批准号[:：]", block, re.S)
    if m:
        d["title"] = re.sub(r"\s+", " ", m.group(1)).strip()
    grab(r"批准号[:：]\s*([\w\-]+)", "number")
    grab(r"申请代码[:：]\s*([\w\-]+)", "code")
    grab(r"项目类别[:：]\s*([^\n]+)", "category")
    grab(r"项目负责人[:：]\s*([^\n]+)", "pi")
    grab(r"资助经费[:：]\s*([\d\.]+)", "amount")
    grab(r"批准年度[:：]\s*(\d{4})", "approve_year")
    grab(r"结题年度[:：]\s*(\d{4})", "complete_year")
    grab(r"依托单位[:：]\s*([^\n]+)", "org")
    grab(r"关键词[:：]\s*([^\n]+)", "keywords")
    return d


def main() -> None:
    from playwright.sync_api import sync_playwright

    out_path = PROJECT_ROOT / "data" / "raw" / "grants_foreign" / "nsfc_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    all_projects: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120")

        for kw in KEYWORDS:
            logger.info("=== Поиск: %s ===", kw)
            try:
                page.goto("https://kd.nsfc.cn/finalSearchList", timeout=45000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)
                for inp in page.locator("input").all():
                    try:
                        ph = inp.get_attribute("placeholder") or ""
                        if "关键词" in ph:
                            inp.fill(kw)
                            break
                    except Exception:
                        continue
                page.wait_for_timeout(500)
                page.locator("button:has-text('检索')").first.click()
                page.wait_for_timeout(7000)

                for page_n in range(1, 4):
                    txt = page.inner_text("body")
                    # отрезать до «根据条件检索到»
                    body = txt.split("根据条件检索到")[-1]
                    # блоки начинаются с «N.» ТОЛЬКО после перевода строки; разделитель оставляем в блоке
                    blocks = re.split(r"\n(?=\d+\.)", body)
                    # первый блок — служебный (инфо), отбрасываем если нет номера проекта
                    for b in blocks:
                        f = extract_fields(b)
                        if f.get("number"):
                            f["query"] = kw
                            f["source"] = "nsfc"
                            all_projects.append(f)
                    logger.info("  стр %d → всего %d", page_n, len([x for x in all_projects if x.get('query') == kw]))
                    # goto page
                    goto_input = None
                    for inp in page.locator("input").all():
                        try:
                            cls = inp.get_attribute("class") or ""
                            if any(k in cls for k in ["pagination", "goto", "page"]):
                                goto_input = inp
                                break
                        except Exception:
                            continue
                    if goto_input is None:
                        inputs = page.locator(".el-pagination input, .pagination input").all()
                        if inputs:
                            goto_input = inputs[0]
                    if goto_input:
                        try:
                            goto_input.fill(str(page_n + 1))
                            goto_input.press("Enter")
                            page.wait_for_timeout(4000)
                        except Exception:
                            break
                    else:
                        break
            except Exception as e:
                logger.error("Ошибка для %s: %s", kw, str(e)[:150])
            time.sleep(2)

        browser.close()

    seen: set[str] = set()
    uniq: list[dict] = []
    for pr in all_projects:
        if pr.get("number") in seen:
            continue
        seen.add(pr["number"])
        uniq.append(pr)

    out_path.write_text(json.dumps({"method": "NSFC kd.nsfc.cn (Playwright v8)", "count": len(uniq),
                                    "projects": uniq}, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d проектов)", out_path, len(uniq))


if __name__ == "__main__":
    main()
