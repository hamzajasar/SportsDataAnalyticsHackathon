# Topic 6 — The Sustainable Sports Club

> **How can community clubs use data to cut energy use, travel emissions or equipment waste?**

## Draft pitch (edit!)
_"We help community sports clubs in Bosnia and Herzegovina see where their carbon footprint comes from — electricity, away travel and kit — and pick the cheapest changes first, so that going green also makes sport cheaper and more accessible for young players."_

## What the data already shows (verified from the downloaded sources)
| Finding | Number | Source |
|---|---|---|
| BiH electricity is coal-heavy | **571 g CO₂/kWh** in 2025 — **2.7×** EU average (210), **3.6×** Croatia (158) | Ember |
| Coal share of BiH electricity | **55%** (2025); hydro 37%, solar 4%, wind 3% | Ember |
| Every kWh a BiH club saves avoids | ~0.57 kg CO₂ (vs 0.21 kg in the EU) → **efficiency pays off ~3× more here** | Ember |
| Away trip, 18 people, 120 km each way | 6 cars **241 kg** · 3 minibuses 183 kg · train 153 kg · **coach 120 kg** (–50%) | UK GHG 2025 |
| New vs re-used clothing | **22.3** vs **0.15** kg CO₂e per kg (~150×) → kit swaps are a huge, cheap lever | UK GHG 2025 |

## Why this can score well (mapping to the 6 criteria)
| Criterion | Our angle |
|---|---|
| Relevance | Real decisions a club makes every week: how to travel, what to heat, what kit to buy |
| Data quality & soundness | Official factors (UK Gov), Ember grid data, transparent assumptions, every number shows its source |
| Technical execution | Full-stack app with live calculators, tested API, CI |
| Innovation | Local angle: BiH's coal grid makes efficiency 3× more valuable than in the EU; facility map for pitch/bus sharing |
| Feasibility, impact & **inclusion** | Cheap actions (car-pooling, kit swap) **lower costs for families** → more kids can afford to play; no tracking of people |
| Presentation | One club, three numbers, one recommendation list |

## Open questions / to do
- [ ] **Organisers' synthetic data pack** (incl. `equipment.csv`): get it into `data/raw/pack/`, run `make profile`
- [ ] OpenStreetMap facilities: `make data` again (Overpass servers were overloaded at first try)
- [ ] Heating: relate monthly energy use to Sarajevo temperature (Open-Meteo) if the pack has energy data
- [ ] Pick a "persona" club (e.g. a Sarajevo youth football club) for the demo story
- [ ] "Action plan" view: rank actions by kg CO₂ saved per KM (convertible mark) spent
