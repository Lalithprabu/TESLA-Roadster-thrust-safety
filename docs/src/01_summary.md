# 1. Executive summary

The Roadster's "flying" feature is a cold-gas thruster system developed with SpaceX, paired with a fan-driven suction system. It gives powered hops of a few seconds, not sustained flight. This study shows the concept can be made acceptably safe only with four architectural measures: two-channel arming with two master valves in series, a "recover, then cut" response to faults in flight, fail-operational control during a hop, and pre-flight checks of every valve and of the gas reserve.

## Key findings

| # | Finding | Evidence |
| --- | --- | --- |
| 1 | It is a hop, not a flight: about 244 kg of air at about 400 bar holds a 1,850 kg car in a hover for 6.7 s, and one reference hop uses 55% of it | Sim 1 |
| 2 | The gas storage is the largest stored-energy hazard: about 60 MJ of burst energy (about 14 kg TNT), and a full discharge can chill the gas towards −130 °C | Sim 1 |
| 3 | Cutting all gas mid-air is always fatal at hop heights. Isolating only the failed line, then recovering, cut bad outcomes after a stuck-open valve from 100% to 0–3% | Sims 2, 4 |
| 4 | The fault tolerant time interval for a stuck-open valve is about 200 ms; detection and isolation are budgeted at 20 ms | Sim 3 |
| 5 | A stuck-closed valve during the roll (1.10–1.95 s) almost always ends badly; the same fault outside the roll is always safe | Sim 4, viewer |
| 6 | Valves that close on power loss are safe on the ground but drop the car in the air. Three requirements (TSR-21 to TSR-23) make hop control fail-operational | Component FMEA |
| 7 | SG1 (no unintended thrust) meets the ASIL D hardware targets with representative rates: SPFM 100%, LFM 98.7%, PMHF 0.006 FIT. Common-cause faults dominate what risk remains | Sim 7 |
| 8 | A faked track zone is the one attack path that defeats both channels at once, because both trust the same zone data; an independent zone check closes it | TARA, attack tree |
| 9 | Per-hop risk of a bad landing from faults is 3.3 × 10⁻⁷ against a proposed 10⁻⁷ target, and the SOTIF residual is bounded only at 1.4 × 10⁻³ per hop | Sims 4, 6 |
| 10 | There is no regulatory path yet: Tesla lists the Rocket trim as not approved for public road use | Chapter 13 |

## Status at a glance

| Item | Count | State |
| --- | --- | --- |
| Hazardous events | 11 | Rated; 3 at ASIL D |
| Safety goals | 8 | 3 ASIL D, 2 ASIL C, 3 ASIL B |
| Functional safety requirements | 14 | 13 in scope; 1 allocated to the steer-by-wire item |
| Technical safety requirements | 23 | All allocated and with a verification method |
| Verification items | 25 | 11 with analysis or simulation evidence, 2 showing a gap, 12 not started |
| Failure modes analysed | 31 component-level | 23 at action priority H |
| Threat scenarios | 9 | All at risk value 3 or below after 13 controls |
| Traceability check | Safety and security chains, both directions | Passes (`tools/check_traceability.py`) |

## What would block release

1. SOTIF residual risk is not yet demonstrated (G3 in the safety case).
2. Stuck-closed valve authority (TSR-17) and the recovery planner (TSR-20) show gaps in simulation.
3. No physical test evidence exists; every number rests on the assumptions in Appendix A.
