#!/usr/bin/env python3
"""freeze_oracle_6areas.py — черновик оракулов областей 2..6 по методике
ORACLE_METHOD_20260927.md (заморожена ДО просмотра кандидатов).

DRAFT ниже = ручной разбор автора-ассистента таблицы кандидатов
(results/oracle_candidates_6areas.md) + дорурейст имён (тот же скрипт).
Ступень 1: резолв имён → topic_id, отчёт неразрешённых. Ступень 2 (после
кросс-проверки субагентом): --freeze пишет results/qa_oracles_6areas_v1.json
+ sha256.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# n → {"A": [имена тем], "B": [имена тем]}  (C = пусто, уйдёт в out_of_scope)
DRAFT: dict[int, dict[str, list[str]]] = {
    # --- Edge (16) ---
    1: {"A": [], "B": ["Advanced Data Compression Techniques"]},  # вериф. 27.09: суть не подтверждена, B-смежная (примечание в _comment)
    16: {"A": ["Internet of Things and AI", "IoT and Edge/Fog Computing"],
         "B": ["Embedded Systems and FPGA Applications", "Advanced Data and IoT Technologies"]},
    17: {"A": ["CCD and CMOS Imaging Sensors"],
         "B": ["Autonomous Vehicle Technology and Safety", "IoT and GPS-based Vehicle Safety Systems"]},
    18: {"A": [], "B": ["Space Satellite Systems and Control", "Satellite Communication Systems",
                        "IoT and Edge/Fog Computing"]},
    19: {"A": [], "B": ["Privacy-Preserving Technologies in Data"]},
    44: {"A": ["Analog and Mixed-Signal Circuit Design"],
         "B": ["Advanced Memory and Neural Computing", "VLSI and FPGA Design Techniques"]},
    45: {"A": [], "B": ["Low-power high-performance VLSI design", "Embedded Systems Design Techniques"]},
    46: {"A": ["IoT and Edge/Fog Computing"], "B": ["Internet of Things and AI"]},
    47: {"A": ["Photonic and Optical Devices"],
         "B": ["Advanced optical system design", "Semiconductor Lasers and Optical Devices"]},
    72: {"A": [], "B": ["Multi-Agent Systems and Negotiation", "Embedded Systems and FPGA Applications"]},
    73: {"A": [], "B": ["Mobile and Web Applications", "Domain Adaptation and Few-Shot Learning"]},
    74: {"A": [], "B": ["Embedded Systems and FPGA Applications", "AI and Big Data Applications"]},
    75: {"A": ["IoT and Edge/Fog Computing"],
         "B": ["Cloud Computing and Remote Desktop Technologies", "Advanced Wireless Communication Technologies"]},
    94: {"A": ["Privacy-Preserving Technologies in Data"],
         "B": ["Advanced Authentication Protocols Security", "Information and Cyber Security"]},
    95: {"A": [], "B": ["CCD and CMOS Imaging Sensors", "Sensor Technology and Measurement Systems"]},
    96: {"A": [], "B": ["Advanced Data Storage Technologies"]},
    # --- Индустриальный ИИ (17) ---
    5: {"A": ["Architecture and Computational Design", "Real-time simulation and control systems"],
        "B": ["Diverse Industrial Engineering Technologies", "Modeling and Simulation Systems"]},
    6: {"A": ["Supply Chain and Inventory Management"],
        "B": ["Advanced Manufacturing and Logistics Optimization", "Information Systems and Technology Applications"]},
    7: {"A": ["Thermodynamic and Exergetic Analyses of Power and Cooling Systems"],
        "B": ["Thermal Radiation and Cooling Technologies", "Advanced Sensor and Control Systems",
              "Energy Efficiency in Computing"]},
    26: {"A": ["Robotics and Automated Systems"],
         "B": ["Reinforcement Learning in Robotics", "Real-time simulation and control systems",
               "Industrial Automation and Control Systems"]},
    27: {"A": ["Industrial Vision Systems and Defect Detection"],
         "B": ["Image Processing Techniques and Applications", "Fault Detection and Control Systems"]},
    28: {"A": ["Geophysical Methods and Applications"],
         "B": ["Geochemistry and Geologic Mapping", "Geographic Information Systems Studies",
               "Robotics and Automated Systems"]},
    29: {"A": ["Industrial Automation and Control Systems"],
         "B": ["Industrial Technology and Control Systems", "Technology and Security Systems",
               "Distributed Control Multi-Agent Systems"]},
    30: {"A": ["Advanced Welding Techniques Analysis", "Welding Techniques and Residual Stresses"],
         "B": ["Robotics and Sensor-Based Localization", "Industrial Automation and Control Systems",
               "Flexible and Reconfigurable Manufacturing Systems"]},
    31: {"A": ["Smart Grid Energy Management", "Microgrid Control and Optimization"],
         "B": ["Real-time simulation and control systems", "Smart Grid and Power Systems"]},
    53: {"A": ["Time Series Analysis and Forecasting", "Complex Systems and Time Series Analysis"],
         "B": ["Real-time simulation and control systems", "Fault Detection and Control Systems"]},
    54: {"A": [], "B": ["Vibration Control and Rheological Fluids", "IoT and Edge/Fog Computing"]},
    55: {"A": ["Industrial Automation and Control Systems"],
         "B": ["Semiconductor materials and devices", "Advancements in Semiconductor Devices and Circuit Design",
               "Advanced Sensor and Control Systems"]},
    78: {"A": ["Logic, programming, and type systems"],
         "B": ["Software Engineering Research", "Industrial Automation and Control Systems",
               "Model-Driven Software Engineering Techniques"]},
    79: {"A": [], "B": ["Business Process Modeling and Analysis",
                        "Diverse Industrial Engineering Technologies",
                        "Information Systems and Technology Applications"]},
    80: {"A": [], "B": ["Internet of Things and AI", "Wireless Sensor Networks for Data Analysis",
                        "Low-power high-performance VLSI design"]},
    81: {"A": ["Real-time simulation and control systems", "Industrial Automation and Control Systems"],
         "B": ["Advanced Control Systems Optimization", "Iterative Learning Control Systems"]},
    82: {"A": [], "B": ["Privacy-Preserving Technologies in Data",
                        "Distributed and Parallel Computing Systems"]},
    # --- Инфраструктура ИИ (17) ---
    8: {"A": [], "B": ["Advanced Memory and Neural Computing", "Cognitive Computing and Networks",
                       "Low-power high-performance VLSI design"]},
    9: {"A": ["Optical Network Technologies", "Advanced Optical Network Technologies"],
        "B": ["Interconnection Networks and Systems", "Photonic and Optical Devices"]},
    10: {"A": ["Advanced Data Storage Technologies"],
         "B": ["Caching and Content Delivery", "Real-Time Systems Scheduling"]},
    32: {"A": ["3D IC and TSV technologies"],
         "B": ["Advanced Data Storage Technologies", "VLSI and FPGA Design Techniques"]},
    33: {"A": [], "B": ["Parallel Computing and Optimization Techniques",
                        "Low-power high-performance VLSI design"]},
    34: {"A": [], "B": ["Power Systems and Technologies", "Energy Efficiency in Computing",
                        "Microgrid Control and Optimization"]},
    35: {"A": [], "B": ["Cloud Computing and Remote Desktop Technologies",
                        "Information and Cyber Security", "Technology and Security Systems"]},
    56: {"A": ["IoT and Edge/Fog Computing"],
         "B": ["Cloud Computing and Remote Desktop Technologies", "Distributed and Parallel Computing Systems"]},
    57: {"A": ["Advanced Data Storage Technologies"],
         "B": ["VLSI and FPGA Design Techniques", "Parallel Computing and Optimization Techniques"]},
    58: {"A": ["Peer-to-Peer Network Technologies"],
         "B": ["Distributed and Parallel Computing Systems", "Distributed systems and fault tolerance"]},
    59: {"A": [], "B": ["Space Satellite Systems and Control", "Satellite Communication Systems"]},
    60: {"A": ["Photonic and Optical Devices"],
         "B": ["Advanced optical system design", "Semiconductor Lasers and Optical Devices",
               "Photorefractive and Nonlinear Optics"]},
    83: {"A": ["3D IC and TSV technologies"],
         "B": ["Advanced Data Storage Technologies", "Parallel Computing and Optimization Techniques"]},
    84: {"A": ["Analog and Mixed-Signal Circuit Design"],
         "B": ["Advanced Memory and Neural Computing", "VLSI and Analog Circuit Testing"]},
    85: {"A": [], "B": ["Thermal Radiation and Cooling Technologies",
                        "Thermodynamic and Exergetic Analyses of Power and Cooling Systems",
                        "3D IC and TSV technologies"]},
    86: {"A": ["Low-power high-performance VLSI design"],
         "B": ["VLSI and FPGA Design Techniques", "Real-Time Systems Scheduling"]},
    87: {"A": ["Superconducting and THz Device Technology"],
         "B": ["Low-power high-performance VLSI design"]},
    # --- Роботы (17) ---
    11: {"A": [], "B": ["Robotics and Automated Systems"]},  # вериф. 27.09: tier понижен A→B (общеробототехническая)
    12: {"A": ["Robotics and Automated Systems"], "B": ["Power Line Inspection Robots"]},
    13: {"A": ["Human-Automation Interaction and Safety"],
         "B": ["Safety Systems Engineering in Autonomy", "Risk and Safety Analysis"]},
    14: {"A": ["Robotics and Automated Systems"],
         "B": ["Teleoperation and Haptic Systems", "Technology and Data Analysis"]},
    36: {"A": ["Robot Manipulation and Learning"],
         "B": ["Robotic Mechanisms and Dynamics", "Soft Robotics and Applications"]},
    37: {"A": ["Modular Robots and Swarm Intelligence"],
         "B": ["Robotics and Automated Systems", "Soft Robotics and Applications"]},
    38: {"A": [], "B": ["Low-power high-performance VLSI design", "Robotics and Automated Systems",
                        "VLSI and FPGA Design Techniques"]},
    61: {"A": ["Underwater Vehicles and Communication Systems"],
         "B": ["Robotics and Automated Systems", "Modular Robots and Swarm Intelligence",
               "Water Quality Monitoring Technologies"]},
    62: {"A": ["Insurance and Financial Risk Management"],
         "B": ["Insurance, Mortality, Demography, Risk Management", "Robotics and Automated Systems"]},
    63: {"A": ["Tactile and Sensory Interactions", "Teleoperation and Haptic Systems"],
         "B": ["Robot Manipulation and Learning", "Soft Robotics and Applications"]},
    64: {"A": ["Robot Manipulation and Learning"],
         "B": ["Human Motion and Animation", "Robotics and Automated Systems"]},
    88: {"A": [], "B": ["Simulation and Modeling Applications", "Modeling and Simulation Systems",
                        "Robotics and Automated Systems"]},
    89: {"A": ["Soft Robotics and Applications"],
         "B": ["Robotics and Automated Systems", "Modular Robots and Swarm Intelligence",
               "Micro and Nano Robotics"]},
    90: {"A": [], "B": ["Soft Robotics and Applications", "Micro and Nano Robotics",
                        "Robotics and Automated Systems"]},
    97: {"A": [], "B": ["Robotic Locomotion and Control", "Soft Robotics and Applications",
                        "Robotic Mechanisms and Dynamics"]},
    98: {"A": ["Polymer composites and self-healing"],
         "B": ["Advanced Sensor and Energy Harvesting Materials", "Robotics and Automated Systems"]},
    99: {"A": [], "B": ["Robotic Locomotion and Control", "Robotic Mechanisms and Dynamics"]},
    # --- Финтех (17) ---
    15: {"A": [], "B": ["Biometric Identification and Security", "User Authentication and Security Systems",
                        "Information and Cyber Security"]},
    39: {"A": ["Speech and dialogue systems"],
         "B": ["AI in Service Interactions", "Speech Recognition and Synthesis"]},
    40: {"A": ["Banking Systems and Strategies"],
         "B": ["Digital Transformation in Financial Services", "finance, banking, and market dynamics",
               "Banking Sector Performance and Management"]},
    41: {"A": ["FinTech, Crowdfunding, Digital Finance"],
         "B": ["Credit Risk and Financial Regulations", "Blockchain Technology Applications and Security",
               "Banking Sector Performance and Management"]},
    42: {"A": ["Blockchain Technology Applications and Security"],
         "B": ["FinTech, Crowdfunding, Digital Finance", "Monetary Policy and Economic Impact"]},
    43: {"A": [], "B": ["Privacy-Preserving Technologies in Data", "Regulation and Compliance Studies",
                        "Banking stability, regulation, efficiency"]},
    65: {"A": [], "B": ["FinTech, Crowdfunding, Digital Finance"]},
    66: {"A": ["Regulation and Compliance Studies"],
         "B": ["User Authentication and Security Systems", "Governance, Compliance, and Sustainability",
               "Access Control and Trust"]},
    67: {"A": [], "B": ["FinTech, Crowdfunding, Digital Finance"]},
    68: {"A": ["Privacy-Preserving Technologies in Data"],
         "B": ["Advanced Authentication Protocols Security", "User Authentication and Security Systems",
               "Cryptography and Data Security"]},
    69: {"A": [], "B": ["FinTech, Crowdfunding, Digital Finance",
                        "User Authentication and Security Systems"]},
    70: {"A": ["Insurance and Financial Risk Management"],
         "B": ["Insurance, Mortality, Demography, Risk Management", "Digitalization, Law, and Regulation"]},
    71: {"A": ["Financial Markets and Investment Strategies"],
         "B": ["FinTech, Crowdfunding, Digital Finance", "Digital Transformation in Financial Services"]},
    91: {"A": [], "B": ["User Authentication and Security Systems", "Access Control and Trust",
                        "Multi-Agent Systems and Negotiation"]},
    92: {"A": [], "B": ["Stock Market Forecasting Methods",
                        "Stochastic processes and financial applications",
                        "Financial Markets and Investment Strategies",
                        "Simulation and Modeling Applications"]},
    93: {"A": ["FinTech, Crowdfunding, Digital Finance"],
         "B": ["Blockchain Technology Applications and Security", "Banking Systems and Strategies",
               "Credit Risk and Financial Regulations"]},
    100: {"A": ["Cryptography and Data Security"],
          "B": ["Digital Transformation in Financial Services", "FinTech, Crowdfunding, Digital Finance",
                "Cryptographic Implementations and Security"]},
}

OUT = ROOT / "results/qa_oracles_6areas_v1.json"
DRAFT_OUT = ROOT / "results/qa_oracles_6areas_DRAFT.json"


def main() -> int:
    freeze = "--freeze" in sys.argv
    t = pd.read_parquet(ROOT / "data/openalex_derived/taxonomy/topics.parquet")
    t["tid"] = [int(str(i).rstrip("/").split("T")[-1]) for i in t["id"]]
    by_name = {}
    for tid, n in zip(t["tid"], t["display_name"]):
        by_name.setdefault(str(n).strip().casefold(), tid)

    x = json.loads((ROOT / "results/oracle_candidates_6areas.json").read_text())
    area_of = {c["n"]: c["area"] for c in x}
    tech_of = {c["n"]: c["tech"] for c in x}

    unresolved: dict[str, list[str]] = {}
    targets_by_area: dict[str, list] = {}
    for n, d in sorted(DRAFT.items()):
        area = area_of.get(n, "?")
        allowed: list[int] = []
        tier = None
        for name in d["A"] + d["B"]:
            tid = by_name.get(name.strip().casefold())
            if tid is None:
                unresolved.setdefault(area, [])
                if name not in unresolved[area]:
                    unresolved[area].append(name)
                continue
            if tid not in allowed:
                allowed.append(tid)
        if d["A"]:
            tier = "A"
        elif d["B"]:
            tier = "B"
        else:
            tier = "C"
        targets_by_area.setdefault(area, []).append(
            {"n": n, "tier": tier, "allowed": allowed, "tech": tech_of[n]})

    if unresolved:
        print("⛔ НЕРАЗРЕШЁННЫЕ ИМЕНА:")
        for a, names in unresolved.items():
            print(f"  [{a}]: {names}")
        if not freeze:
            return 2

    # need = ceil(0.7 * N) по правилу автора (27.09), N = все технологии области
    doc = {
        "_comment": ("ORACLE v1 областей 2..6. Методика: results/runtime/"
                     "ORACLE_METHOD_20260927.md (заморожена ДО просмотра кандидатов). "
                     "allowed: A = имя темы покрывает суть, B = смежный; C = out_of_scope. "
                     "need = ceil(0.7×N) по правилу. "
                     "Кросс-проверка субагентом evidence-auditor 27.09: 7 замечаний, "
                     "все обработаны (21 id верифицирован по display_name; №11 A→B; "
                     "№73 добавлена Domain Adaptation and Few-Shot Learning; №1 — суть "
                     "покрытия не подтверждена, тема оставлена как B-смежная)."),
        "frozen_at": "2026-09-27" if freeze else None,
        "areas": {},
    }
    for area, tgts in sorted(targets_by_area.items()):
        n_tech = len(tgts)
        need = -(-n_tech * 70 // 100)  # ceil
        doc["areas"][area] = {
            "n_tech": n_tech, "need": int(need),
            "targets": tgts,
            "out_of_scope": [t["n"] for t in tgts if t["tier"] == "C"],
        }
        a = sum(1 for t in tgts if t["tier"] == "A")
        b = sum(1 for t in tgts if t["tier"] == "B")
        c = sum(1 for t in tgts if t["tier"] == "C")
        print(f"{area}: N={n_tech} need={need} | A={a} B={b} C={c} "
              f"| allowed всего={sum(len(t['allowed']) for t in tgts)}")

    path = OUT if freeze else DRAFT_OUT
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{'ЗАМОРОЖЕН' if freeze else 'DRAFT'} → {path.name} sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
