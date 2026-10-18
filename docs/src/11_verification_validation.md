# 11. Verification and validation plan

## 11.1 Strategy

Verification asks "did we build it right?" against each requirement. Validation asks "did we build the right thing?" against the safety goals and the acceptance criteria. Both follow the V-model, from analysis at concept stage to vehicle tests.

| Level | Methods | Main questions |
| --- | --- | --- |
| Concept | FMEA, FMEDA, FTA, DFA, STPA, TARA, simulation | Is the architecture capable of meeting the goals? |
| Component | Valve, sensor and vessel qualification; burst, cycle, cold and fire tests | Do parts meet their failure-rate and environmental assumptions? |
| Software | Requirements-based tests, MC/DC coverage for ASIL D parts, static analysis, fuzzing | Does the code do what the requirements say, and nothing else? |
| Integration (HIL) | Real computers in closed loop with a validated model; fault and attack injection | Do detection and reaction meet the timing budget? |
| Vehicle | Thrust stand, tethered hops, drop tests, crash tests with charged tanks, track tests | Does the whole car behave as predicted? |
| Validation | Scenario-based simulation at scale, field monitoring | Is residual risk below 10⁻⁷ per hop? |

## 11.2 Verification items

Every technical safety requirement and every cybersecurity control has at least one verification item, and every verification item lists what it covers. The table is generated from `data/verification.csv`.

{{table:verification}}

## 11.3 Test scenarios

| ID | Scenario | Fault or condition | Pass criterion | Covers |
| --- | --- | --- | --- | --- |
| SC-01 | Public-road drive with a forged arm request | Arm request injected on the vehicle bus | No master valve opens | TSR-01, TSR-02, TSR-04 |
| SC-02 | Power-on with a leaking master valve | Seat leak on valve A | Thrust locked out | TSR-03 |
| SC-03 | Stuck-open thruster at the apex | One nozzle forced open | Line isolated ≤ 20 ms; upright landing | TSR-09, TSR-15 |
| SC-04 | Stuck-closed nozzle during the roll | One nozzle forced closed at 1.3 s | Upright landing at ≤ 5 m/s | TSR-17, TSR-20 |
| SC-05 | Leak from one vessel group mid-climb | 5 kg/s leak | Recovery starts at once; upright landing | TSR-10, TSR-11 |
| SC-06 | Thrust control unit reset mid-hop | Controller power removed | Backup law takes over ≤ 50 ms | TSR-22 |
| SC-07 | Supply dip mid-hop | Low-voltage feed drops for 200 ms | No master valve closes | TSR-21 |
| SC-08 | Valve bus lost mid-hop | Bus disconnected | No valve opens unintentionally; attitude held | TSR-23 |
| SC-09 | Crash with charged tanks | Frontal crash test | Vessels isolated ≤ 50 ms; no projectile; no net vent thrust | TSR-06, TSR-07 |
| SC-10 | Satellite spoofing at the track gate | Fake fix inside the zone | Arming refused; monitor flags mismatch | CC-04, CC-05, CC-13 |
| SC-11 | Hard landing from 5 m | Drop test with external airbag | Peak ≤ 15 g | TSR-14 |
| SC-12 | Cold refill then immediate hop | Gas 20 K colder than nominal | Reserve check corrects for temperature | TSR-10, TSR-18 |

## 11.4 Simulation credibility

The simulations in this study are concept-stage evidence. Before they can support a release decision they need the following.

| Credibility factor | Status today | Needed |
| --- | --- | --- |
| Model fidelity | Planar roll-plane rigid body; lumped tank | 6-degree-of-freedom model with nozzle plume and ground effect |
| Parameter basis | Assumptions A-01 to A-16 | Measured mass properties, thrust-stand and blowdown data |
| Code verification | Energy and momentum checks; deterministic seeds | Independent review; unit tests against analytic cases |
| Validation | None against hardware | Correlation with tethered hops within agreed tolerances |
| Tool qualification | Open-source Python | Tool confidence level assessed per ISO 26262-8 cl. 11 |

## 11.5 Roadmap

![V&V roadmap](figures/F11_vv_roadmap.png)

*Figure 9. Verification and validation roadmap from this concept study (Sims 1–7) to release.*

## 11.6 Evidence status

Of 25 verification items, 5 have analysis evidence, 6 have simulation evidence, 2 show a gap that needs design work (VER-16, VER-19) and 12 have not started. No physical test evidence exists.
