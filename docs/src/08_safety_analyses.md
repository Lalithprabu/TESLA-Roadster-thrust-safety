# 8. Safety analyses

Five analyses check the architecture from different directions: the FMEA works up from component failures, the fault tree works down from the worst outcome, the FMEDA puts numbers on the hardware, the dependent failure analysis looks for faults that defeat both channels at once, and STPA looks for unsafe control decisions with nothing broken.

## 8.1 Subsystem FMEA

| Subsystem | Failure mode | Worst effect | Main safety mechanism | Goal |
| --- | --- | --- | --- | --- |
| S2 Compressor and fill | Over-pressure; wet air | Vessel overload; ice in valves | Fill limit plus mechanical relief; dew-point check | SG2 |
| S3 Gas storage | Rupture; leak | Blast; loss of reserve in flight | Burst ratio, shielding; pressure decay monitor | SG2, SG6 |
| S4 Distribution | Master or line valve stuck open or closed | Unintended thrust; loss of a lift group | Series masters; pre-arm test; line isolation | SG1, SG6 |
| S5 Thrusters | Valve stuck open, stuck closed or slow | Asymmetric thrust | Line isolation and compensation | SG5, SG6 |
| S6 Suction | Fan or skirt failure | Sudden loss of downforce | Plenum pressure monitoring, limits | SG4 |
| S8 Sensing | IMU, pressure or positioning error | Wrong control or wrong zone | Voting, dissimilar checks | SG1, SG6 |
| S9 Control | Wrong command; computer lost | Unintended thrust; loss of control | Two channels; backup hop law | SG1, SG6 |
| S10 HMI and arming | Stuck arm switch; false request | Arming without consent | Two-step confirm plus physical switch | SG1 |
| S11 Protection | Airbag fires on the road | Driver startled; loss of view | Arming window, two disarm signals | SG8 |

## 8.2 Component design FMEA

The component FMEA uses the AIAG-VDA method: severity (S), occurrence (O) and detection (D) are each rated 1–10 and combined into an action priority (H, M or L) from the AIAG-VDA table. Parts are representative types, not Tesla's parts (A-11). Of 31 failure modes, 23 are at action priority H. That is expected at concept stage, because most modes have S = 9 or 10 and design verification does not yet exist. The table below is generated from `results/component_fmea.csv`.

{{table:component_fmea}}

**Findings that changed the architecture.**

1. *Master valve closes in flight (coil or power loss).* A normally closed valve is the right choice on the ground but drops the car in the air. This led to TSR-21 and AD-04.
2. *Thrust control unit lost in flight.* With no backup control law, the monitor can only cut gas, which Sim 2 shows is fatal. This led to TSR-22.
3. *Valve command bus lost.* A shared bus is a single point for every nozzle. This led to TSR-23.
4. *Pressure regulator freezes.* A full discharge chills the gas to about 142 K. This is covered by TSR-18 and TSR-19.

## 8.3 FMEDA and hardware metrics for SG1

The fault tree for SG1 (no unintended thrust) was solved for minimal cut sets, and each cut set was assigned a rate from the component failure rates, diagnostic coverage and pre-arm test interval: q = λ·[DC·τ/2 + (1 − DC)·T/2], with τ = 1 h between pre-arm tests and T = 10,000 h vehicle life (A-12, A-13).

| Metric | Result | ASIL D target | Met |
| --- | --- | --- | --- |
| Safety-related failure rate | 1,236 FIT | — | — |
| Single-point fault metric (SPFM) | 100.0% (rounded; only the computer common-cause term is single-point) | ≥ 99% | Yes |
| Latent fault metric (LFM) | 98.7% | ≥ 90% | Yes |
| Probabilistic metric for hardware failures (PMHF) | 0.006 FIT | < 10 FIT | Yes |
| Minimal cut sets | 36: one of order 1, two of order 2, 24 of order 3, nine of order 4 | — | — |

![Fault tree](figures/F06_fault_tree_unsafe_landing.png)

*Figure 5. Fault tree for an unsafe landing after a hop (SG6): a thrust fault (too little impulse, misapplied thrust or a disturbance) must combine with a failed recovery.*

![SG1 cut sets](figures/F07_sg1_cut_sets.png)

*Figure 6. The largest SG1 cut sets by rate. Common-cause failure of the two computers dominates; every independent combination is at least three orders of magnitude smaller.*

**How to read these numbers.** The metrics pass by a wide margin, but they rest on assumed failure rates and β-factors (1% for the computers and 2% for the master valves, A-14). The ranking matters more than the absolute values: the residual is dominated by common-cause faults, so the dependent failure analysis is the decisive evidence for SG1. An earlier, coarser FMEDA (Sim 6) gave PMHF 0.053 FIT; it is superseded by this component-level result.

## 8.4 Fault tree for SG6

An unsafe landing needs a thrust fault and a failed recovery together (Figure 5). That AND gate is the reason recovery logic matters so much. Per-hop probabilities from Sim 6, with 11 kN lift groups and a 99.9%-coverage pre-arm valve test, are:

| Branch | Probability per hop |
| --- | --- |
| Stuck-closed thruster valve, latent at take-off, during the roll | 1.8 × 10⁻⁷ |
| Leak | 1.4 × 10⁻⁷ |
| Stuck-open thruster valve | 1.4 × 10⁻⁸ |
| **Total from random hardware faults** | **3.3 × 10⁻⁷** (target 10⁻⁷, not yet met) |

Stuck-closed nozzles during the roll dominate. Meeting the target needs either individually controlled nozzles that keep at least 50% roll-braking authority (TSR-17) or a better recovery planner (TSR-20). Both show gaps in simulation today.

## 8.5 Dependent failure analysis

| Coupling factor | Could defeat | Measure | Residual |
| --- | --- | --- | --- |
| Same microcontroller design or compiler | Both computers | Dissimilar monitor, different supplier and tool chain (AD-02) | β about 1% |
| Same low-voltage supply | Both computers; both master valves | Separate feeds; monitor's own buffer; hold-up store (TSR-21) | Low |
| Same zone data | Both channels' arming decisions | Independent zone check in the monitor (CC-13, AD-09) | Low after CC-13 |
| Same valve type and batch | Both master valves | Different valve suppliers or seat designs; leak-down test (TSR-03) | β about 2% |
| Cold from gas expansion | Valves, seals, regulator | Cold qualification (TSR-18); dry air (TSR-19) | Needs test |
| Ice or contamination in the gas | All valves | Filter and dew-point check (TSR-19) | Low |
| Vessel burst fragments | Harness, both computers | Segregation, shielding and routing rules | Needs layout |
| Vibration and shock of landing | Connectors, sensors | Qualification to landing loads (Sim 5) | Needs test |
| Same software requirement error | Both channels | Different teams and requirements derived independently from FSRs | Process measure |
| Cyber attack on a shared input | Both channels | Isolated domain, authenticated bus (chapter 10) | See TARA |

## 8.6 STPA unsafe control actions

STPA covers hazards that need no failure: the controller does exactly what it was designed to do, but the decision is wrong for the situation.

| Control action | Not provided | Provided when unsafe | Wrong timing or order | Stopped too soon or applied too long |
| --- | --- | --- | --- | --- |
| Arm thrust | — | UCA-1: arming with a person in the clear zone (SG7) | UCA-2: arming before the pre-arm test finishes (SG1) | — |
| Open master valves | UCA-3: master valves not held open mid-hop (SG6) | UCA-4: open on a public road (SG1) | — | UCA-5: closed mid-hop by a supply dip (SG6) |
| Fire thrusters for a hop | — | UCA-6: hop with too little gas for recovery (SG6) | UCA-7: roll starts before climb rate settles (SG6) | UCA-8: thrust held after touchdown, car slides (SG7) |
| Command recovery | UCA-9: fault detected, no recovery commanded (SG6) | UCA-10: recovery on a false alarm wastes gas (SG6) | UCA-11: recovery after the FTTI has passed (SG6) | UCA-12: recovery ends before the car is level (SG6) |
| Cut all gas | — | UCA-13: cut while airborne (SG6) | — | — |
| Deploy external airbags | UCA-14: no deployment on a hard landing (SG8) | UCA-15: deployment on the road (SG8) | UCA-16: deployment too early, airbag vents before contact (SG8) | — |

Every unsafe control action maps to an existing requirement: UCA-1 to TSR-02; UCA-2 to TSR-16; UCA-3, UCA-5 and UCA-13 to TSR-12 and TSR-21; UCA-4 to TSR-01 and TSR-02; UCA-6 to TSR-10; UCA-7 to TSR-11 and TSR-20; UCA-8 to a landing-detection requirement to be added in the next issue (open issue OI-07); UCA-9 to UCA-12 to TSR-09, TSR-11, TSR-12 and TSR-20; UCA-14 to UCA-16 to TSR-14.
