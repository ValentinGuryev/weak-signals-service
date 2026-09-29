#!/usr/bin/env python3
"""Сбор утреннего доклада (запускается в 7:00): статус патентов + конференций."""
import json, time
from pathlib import Path
from datetime import datetime

ROOT = Path("/home/user/projects/Hackathon")
PAT = ROOT / "experiment" / "runs" / "patents"
CONF = ROOT / "data" / "raw" / "conferences" / "conference_hits.json"

# Ждём до 7:00 (если запущен раньше)
now = datetime.now()
target = now.replace(hour=7, minute=0, second=0, microsecond=0)
if target < now:
    target = target.replace(day=now.day + 1)  # завтра 7:00
print(f'Жду до {target}', flush=True)
time.sleep((target - now).total_seconds())

lines = [f"# Утренний доклад ({datetime.now():%Y-%m-%d %H:%M})", ""]

# 1. Патенты
lines.append("## 1. Патенты (16 тем)")
if PAT.exists():
    for f in sorted(PAT.glob("*.json")):
        size = f.stat().st_size
        ok = "✅" if size > 1000 else ("⚠️" if size > 100 else "❌")
        lines.append(f"{ok} {f.name}: {size} байт")
else:
    lines.append("Папка патентов отсутствует")

# 2. Конференции
lines.append("\n## 2. Конференции")
if CONF.exists():
    try:
        d = json.loads(CONF.read_text(encoding="utf-8"))
        lines.append(f"✅ conference_hits.json: {d.get('total', '?')} статей, {CONF.stat().st_size} байт")
        s = d.get("summary", {})
        for src, kws in s.items():
            tot = sum(kws.values())
            lines.append(f"   {src}: {tot} матчей по {len(kws)} словам")
    except Exception as e:
        lines.append(f"⚠️ Файл есть, но не прочитался: {e}")
else:
    lines.append("❌ conference_hits.json отсутствует")

# 3. Процессы
lines.append("\n## 3. Процессы")
import subprocess
for name in ["night_scheduler", "patents_by_topic", "conference_mining"]:
    out = subprocess.run(["pgrep", "-f", name], capture_output=True, text=True)
    lines.append(f"{'✅' if out.stdout.strip() else '❌'} {name}: {'жив' if out.stdout.strip() else 'не работает'}")

(ROOT / "results" / "morning_report.md").write_text("\n".join(lines), encoding="utf-8")
print("Доклад готов:", ROOT / "results" / "morning_report.md")
