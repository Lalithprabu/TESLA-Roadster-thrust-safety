# 6. Hazard analysis and risk assessment

## 6.1 Method

Hazardous events are rated with ISO 26262-3 severity (S), exposure (E) and controllability (C) classes. Because a hop is closer to a short flight than to driving, each in-flight failure condition is also classified the aviation way (ARP4761A functional hazard assessment) and given a probability target per hop. Where the two methods disagree, the stricter result governs.

Rating rules used throughout:

- **Severity.** Any event that can kill an occupant or a bystander is S3. A hop from 4.5 m that ends inverted or at more than 5 m/s vertical speed is treated as potentially fatal.
- **Exposure.** Public-road situations are E4. Track use with the thrusters armed is E3 for Boost, which any Thrust-trim owner can use, and E2 for Hop, which needs the invite-only Rocket trim at an authorised site. The inverted-ramp stunt is E1.
- **Controllability.** No driver can correct an unexpected thrust event or an in-flight fault within the time available (C3), except low-speed manoeuvring, where braking can partly help (C2).

## 6.2 Hazardous events

{{table:hazards}}

## 6.3 Functional hazard assessment for flight phases

| Failure condition | Phase | Effect | Class | Target per hop |
| --- | --- | --- | --- | --- |
| Total loss of thrust | Climb, apex, roll | Fall from up to 6 m, possibly inverted | Catastrophic | Below 10⁻⁷ |
| Uncontained asymmetric thrust | Any airborne phase | Uncontrolled roll; inverted landing | Catastrophic | Below 10⁻⁷ |
| Loss of attitude information | Any airborne phase | Uncontrolled attitude | Catastrophic | Below 10⁻⁷ |
| Single stuck-closed nozzle | Roll | Reduced roll braking; possible overshoot | Hazardous | Below 10⁻⁵ |
| Partial loss of lift | Descent | Hard landing at 3–5 m/s | Major | Below 10⁻³ |
| Lateral drift beyond 3 m | Any | Car leaves the landing area | Major | Below 10⁻³ |

## 6.4 Safety goals

{{table:goals}}

## 6.5 Rationale for difficult ratings

**Why SG6 is ASIL B with a quantitative target.** By the ISO 26262 tables, a fatal loss of control during a hop is S3, C3 and E2, which yields ASIL B. That rating reflects how rarely the hop situation occurs across the whole fleet, not how dangerous each hop is. For the person in the car, a hop is a flight. An ASIL B rating on its own would allow a per-hop risk far above what aviation accepts for a catastrophic failure. This study therefore keeps ASIL B for the development process and adds the FHA target of 10⁻⁷ per hop as a quantitative requirement, checked in Sim 6 and section 9.3. If the operator markets the hop as a routine feature (E3 or E4), SG6 rises to ASIL C or D.

**Why HE11 is merged into SG6.** Loss of suction while inverted (ASIL A on its own) has the same safe state as an in-flight fault: level the car and land. It is handled by SG6's recovery requirements.

**Why SG3 is outside the item.** Steering is a separate steer-by-wire item with its own ASIL D goal. It appears here only as an interface; FSR-3.1 records the allocation.

**Why HE1 and HE2 share SG1.** They are the same malfunction in different situations; the goal takes the worse rating (ASIL D).
