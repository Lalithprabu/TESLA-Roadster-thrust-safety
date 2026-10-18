# 14. Simulation report

Seven simulations support the analysis. They are deliberately simple, so anyone can read, run and challenge them: about 1,400 lines of Python using NumPy and Matplotlib, all in `sim/`. `python sim/run_all.py` reproduces every number and chart in this chapter in under two minutes on a laptop. Random seeds are fixed, so results are repeatable.

## 14.1 Common model

| Element | Model |
| --- | --- |
| Vehicle | Planar rigid body in the roll plane: height, lateral position and roll angle, 1,850 kg, 600 kg·m² (A-01, A-02) |
| Thrusters | Four lift groups of 9 kN at ±0.35 m and ±0.85 m from the centreline (A-06); first-order valve lag; ±3% thrust scatter |
| Gas | Adiabatic blowdown of a lumped tank with real-gas density, regulated 40 bar feed, specific impulse falling with gas temperature (A-05, A-07, A-08) |
| Guidance | Reference hop: climb to 4.5 m in 1.3 s, 360° roll near the apex, descent at up to 4 m/s slowing to 0.8 m/s near the ground |
| Control | PD attitude and height control with feed-forward; torque-first allocation to the available groups (A-10) |
| Faults | Stuck-open, stuck-closed or leaking group at any time; detection delay as a parameter |
| Monitor strategies | None; cut all gas; isolate the faulty group and recover |
| Outcome | Safe if the car lands with roll below 30° and vertical speed below 5 m/s |

## 14.2 Sim 1: gas budget

![Gas budget](figures/fig1_gas_budget.png)

*Figure 11. Tank pressure, gas temperature and usable thrust during a full-tank hover.*

A full bank of 244 kg at 400 bar holds the car in a hover for 6.7 s. Pressure falls to 28 bar and gas temperature to 142 K. Specific impulse falls from 69 s to 48 s as the gas cools. The reference hop needs 134 kg (55% of the fill). Stored burst energy is 60 MJ, about 14 kg of TNT.

## 14.3 Sim 2: stuck-open valve, three monitor strategies

![Stuck valve](figures/fig2_stuck_valve.png)

*Figure 12. Roll angle and height after an outer lift group sticks open at 1.45 s, when the car is nearly inverted.*

| Strategy | Touchdown | Roll at touchdown | Vertical speed | Outcome |
| --- | --- | --- | --- | --- |
| No fault | 4.15 s | 0° | 1.0 m/s | Safe |
| Fault not detected | 2.69 s | −49° | 11.8 m/s | Unsafe |
| Cut all gas | 2.74 s | 152° (on the roof) | 10.6 m/s | Unsafe |
| Isolate the line and recover | 3.34 s | 0° | 3.9 m/s | Safe |

Cutting all gas, the classic "safe state", lands the car on its roof. This single result drives AD-03 and TSR-12.

## 14.4 Sim 3: fault tolerant time interval

![FTTI](figures/fig3_ftti.png)

*Figure 13. Share of bad outcomes against detection-plus-isolation delay, over fault times from 0.6 s to 3.0 s.*

| Lift group | Bad at 20 ms | Bad at 100 ms | Bad at 300 ms | Delay where bad outcomes pass 10% |
| --- | --- | --- | --- | --- |
| 9 kN | 4.1% | 2.0% | 20.4% | 200 ms |
| 11 kN | 2.0% | 0% | 0% | 440 ms |

The FTTI is about 200 ms with 9 kN groups, so a 20 ms budget leaves a tenfold margin. The residual bad outcomes at short delays come from faults in the middle of the roll, where the recovery planner sometimes chooses the longer way back to level. That is the gap recorded against TSR-20. Larger 11 kN groups remove almost all stuck-open failures.

## 14.5 Sim 4: Monte Carlo over 12,000 hops

![Monte Carlo](figures/fig4_monte_carlo.png)

*Figure 14. Bad-outcome rates for four architecture options over the same 12,000 random draws.*

Each draw varies fill (40–100%), gas temperature, mass, inertia, centre of gravity, gusts and thrust scatter, and injects a stuck-open, leak or stuck-closed fault at an elevated rate so that each fault type gets enough samples.

| Option | Hops refused | Bad per flown hop | Bad, no fault | Bad given stuck open | Bad given leak | Bad given stuck closed |
| --- | --- | --- | --- | --- | --- | --- |
| A: no reserve check, cut on fault | 0% | 31.6% | 21.2% | 100% | 100% | 100% |
| B: reserve check, cut on fault | 79.1% | 12.7% | 0% | 100% | 100% | 100% |
| C: reserve check, isolate and recover | 79.1% | 1.6% | 0% | 3.3% | 4.5% | 36.0% |
| D: C with 11 kN lift groups | 79.1% | 1.4% | 0% | 0% | 5.4% | 32.6% |

The high refusal rate reflects the deliberately wide fill range: the reference hop needs at least 86% fill. In service the reserve check would offer a lower manoeuvre instead of refusing (AD-08). The two key results are that the reserve check removes gas starvation and that isolating and recovering saves almost every stuck-open and leak case. The stuck-closed result of about one in three is the main open design issue (OI-03).

## 14.6 Sim 5: landing loads

![Landing](figures/fig5_landing.png)

*Figure 15. Peak deceleration against drop height, suspension alone and with an external airbag.*

| Drop height | Suspension only, peak | With airbag, peak |
| --- | --- | --- |
| 2 m | 17.1 g | 11.3 g |
| 4 m | 26.4 g | 11.3 g |
| 5 m | 30.2 g | 14.0 g |
| 6 m | 33.6 g | 16.5 g |

The airbag's relief vents hold its pressure at 1.8 bar, which caps the peak at about 11 g up to 4 m. Above about 4 m the airbag reaches the end of its stroke and loads rise again. That supports a 5 m limit on apex height (OI-08).

## 14.7 Sim 6: per-hop risk (first FMEDA superseded)

![Per-hop risk](figures/fig6_per_hop_risk.png)

*Figure 16. Per-hop probability of a bad landing from random faults, for three design options, against the 10⁻⁷ target.*

Combining Sim 4's conditional outcomes with fault rates and pre-arm test coverage gives the per-hop risk of a bad landing. With 11 kN groups and a 99.9%-coverage pre-arm valve test it is 3.3 × 10⁻⁷, still above the 10⁻⁷ target; stuck-closed faults dominate. Sim 6 also contains a first, coarse FMEDA, which Sim 7 supersedes.

## 14.8 Sim 7: component FMEA and cut-set FMEDA

Sim 7 holds the component DFMEA (31 failure modes, chapter 8.2) and solves the SG1 fault tree for its 36 minimal cut sets. It gives SPFM 100%, LFM 98.7% and PMHF 0.006 FIT, with the computers' common-cause term dominating (Figure 6).

## 14.9 Limits of the models

- Planar model: no pitch or yaw coupling, no lateral wind profile, no plume or ground-effect modelling.
- Lumped tank: no temperature gradients, no heat transfer from vessel walls (this makes the gas colder than reality, a conservative assumption for thrust and a non-conservative one for valve icing).
- Ideal valves with first-order lag; no valve chatter or water hammer.
- Failure rates, coverages and β-factors are assumed (A-11, A-12, A-14).
- No model has been validated against hardware. The results show *relative* merits of architecture options; absolute values need test data.

## 14.10 Interactive viewer

`viewer/index.html` replays the simulated trajectories in a browser with no installation. It plays 14 precomputed scenarios (the no-fault hop, stuck-open valves with each monitor strategy and several detection delays, stuck-closed valves, leaks, gas starvation and a crosswind gust) and a scan of stuck-closed fault timing that shows the 1.10–1.95 s danger window. A hosted version is the "Roadster Hop Fault Lab".
