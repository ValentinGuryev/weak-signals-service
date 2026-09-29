# Wishlist кейса 003 (Flux pump / космос) — что скачать

> Правило §4.2a: только НЕскачанные документы. Скачанные → вычищаются.
> PDF → `case_studies/003_flux_pump_space/literature/(YYYY) _*_ Author — Title.pdf`, выжимка `.md` рядом — обязательна.

## Фокус: термоэлектрическая накачка / Peltier-токовводы (альтернатива flux pump)

> **Контекст:** патент **JP5417643B2 (Toshiba+JAXA, заявка 08.09.2009, рег. 19.02.2014)** —
> космический HTS-магнит, возбуждаемый **термоэлектрическим элементом** (эффект Зеебека:
> перепад температур «солнечная засветка → радиационный холодильник» рождает ЭДС → ток в катушке).
> Это **альтернативный инженерный путь** к бестоковводной/квазиперсистентной накачке в космосе —
> конкурент flux pump (Hēki). Нужно понять: физика, достижимые токи, сравнение с flux pump.

### 1. Прямое научное продолжение патента (Toshiba, quasi-persistent)

> ~~A1 (Ono & Kuriyama 2002), A2 (Kuriyama 2006) — скачаны, выжимки в literature/~~ → вычищено .

| # | Документ | DOI/URL | Релев. | Зачем | Статус |
|---|---|---|---|---|---|
| A3 | **Ono, Kuriyama, Ueda, Okamura — «Basic study of high Tc superconducting magnet excited by thermoelectromotive force»** (Cryogenics 43, 2003) | 10.1016/s0011-2275(03)00165-6 | !!! | Промежуточное звено 2002→2004: базовая физика термо-ЭДС накачки | 📥 |
| A4 | **Ono, Kuriyama, Oguchi, Ueda, Okamura — «Cryocooler-Cooled High Tc SC Magnet Excited by Thermoelectromotive Force»** (IEEE TAS 14, 2004) | 10.1109/TASC.2004.830519 (уточнить) | !!! | Криокулерная версия: катушка 10-20K + элемент 50-70K | 📥 |
| A5 | **Ono, Kuriyama, Oguchi, Okamura — «...Excited by a Hybrid Semiconductor-HTS Thermoelectric Element»** (IEEE TAS 15, 2005) | 10.1109/tasc.2005.849152 | !!! | Гибридный элемент (полупроводник+СП) | 📥 |
| A6 | **Tosaka, Mizuno, Koyanagi, Okamura, Kuriyama — «Tesla-Class Quasi-Persistent-Mode HTS Magnet Excited by Thermoelectric Element»** (IEEE TAS 18, 2008) | 10.1109/tasc.2008.922281 | !!! | **Пик программы** (Tesla-класс, 2008); Tosaka = изобретатель патента JP5417643B2 | 📥 |

### 2. Peltier-токовводы (PCL) — уменьшение теплопритока (смежная тема!)

| # | Документ | DOI/URL | Релев. | Зачем | Статус |
|---|---|---|---|---|---|
| B1 | **Yamaguchi et al. — «Peltier Current Lead Experiments with a Thermoelectric Semiconductor near 77 K»** (1997/98) | arXiv:cond-mat/9711042 | !!! | **Первая демонстрация PCL** (S. Yamaguchi, Chubu Univ): принцип — термоэлектрик в токовводе откачивает тепло, уменьшая теплоприток в криостат. Фундамент всей ветки | 📥 |
| B2 | **Gehring, Hüttner, Huebener — «Peltier cooling of superconducting current leads»** (Cryogenics 41, 2001) | 10.1016/s0011-2275(01)00124-2 | !!! | Peltier-охлаждение СП-токовводов (Tübingen). Альтернатива flux pump: снижение теплопритока токовводов тем же термоэлектрическим принципом | 📥 |
| B3 | **Hasegawa et al. — «Reduction of heat leak in cryogenic system using Peltier current leads»** (Cryogenics 42, 2002) | 10.1016/s0011-2275(02)00048-6 | !! | Количественно: насколько PCL снижают теплоприток (17 цит.) — данные для сравнения с flux pump (150 мВт vs 1476 мВт в Hēki) | 📥 |
| B4 | **Kawahara, Fujii, Emoto, Hamabe, Watanabe, Sun, Ivanov, Yamaguchi — «Double Peltier Current Lead for Heat Leak Reduction...»** (IEEE TAS 21, 2011) | 10.1109/tasc.2010.2096451 | !! | Современные PCL (double) для СП-DC-применений (12 цит.) — зрелость технологии | 📥 |
| B5 | **Fujii et al. — «Thermoelectric Property Dependence and Geometry Optimization of Peltier Current Leads...»** (J. Electron. Mater. 40, 2011) | 10.1007/s11664-011-1513-4 | !! | Оптимизация материалов/геометрии PCL — что реально достижимо | 📥 |

### 3. Применение PCL к конкретным системам / космос

| # | Документ | DOI/URL | Релев. | Зачем | Статус |
|---|---|---|---|---|---|
| C1 | **Sasaki — «Optimization of Peltier Current Leads for 5T Cryogen-Free Superconducting Magnets»** (AIP Conf. Proc. 2006) | 10.1063/1.2192375 | !! | PCL для безгелиевых 5T-магнитов (Toshiba? Kuriyama-группа) — связь с патентным семейством | 📥 |
| C2 | **Miyata et al. — «Evaluation of Thermoelectric Performance of Peltier Current Leads Designed for SC DC Transmission Cable Systems»** (IEEE TAS 26, 2016) | 10.1109/tasc.2016.2541686 | ! | PCL для СП-кабелей — смежная область | 📥 |
| C3 | **Ivanov, Watanabe, Chikumoto et al. — «Testing of Peltier current leads used in real electrical superconducting network»** (2019) | 10.1016/j.matpr.2019.02.060 | ! | Испытания PCL в реальной СП-сети (2019) — зрелость | 🔶 |


> Вычищено из wishlist: A1 (Ono & Kuriyama 2002), A2 (Kuriyama 2006) — скачаны, выжимки
> `literature/(2002) !!! Ono & Kuriyama...` и `literature/(2006) !!! Kuriyama...` (2026-09-04).
> Заменены на нескачанные A3-A6 (продолжения серии 2003-2008).
