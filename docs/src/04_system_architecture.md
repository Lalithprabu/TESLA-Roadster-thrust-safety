# 4. System architecture

The architecture rests on two rules. On the ground, thrust is impossible unless two independent channels agree, so the default state is gas isolated and no thrust. In the air, no single fault may remove thrust, so the car can always level itself and land. The rest of this chapter shows how the subsystems, functions, electronics, interfaces and modes deliver both rules, and why each major design decision was taken. This is a reference architecture inferred from public disclosures; Tesla has not published its own.

## 4.1 Architecture principles

| ID | Principle | Driven by |
| --- | --- | --- |
| P1 | Fail closed on the ground: every gas valve is normally closed and needs active power to open | SG1, SG2 |
| P2 | Fail operational in the air: during a hop no single fault closes the gas or stops control for at least 5 s | SG6 |
| P3 | Two independent, dissimilar channels must both agree before gas can reach a nozzle | SG1 |
| P4 | The thrust domain is isolated: nothing outside it can command thrust | SG1, CG1 |
| P5 | Attitude before altitude: on any in-flight fault, level the car first, then descend | SG6 |
| P6 | Never start what cannot be finished after one fault (gas reserve, lift margin) | SG6 |

## 4.2 Logical architecture

![System architecture](figures/F03_system_architecture.png)

*Figure 2. Logical architecture: eleven subsystems in six layers (energy, gas, effectors, sensing, control, protection), with the gas path and the hardwired arm line.*

{{table:subsystems}}

## 4.3 Functional architecture

Fourteen functions make up the item. Each is allocated to a subsystem and inherits the highest ASIL of the safety goals it supports.

| ID | Function | Allocated to | Supports | ASIL |
| --- | --- | --- | --- | --- |
| F1 | Capture driver intent and arming consent | S10 | SG1 | D |
| F2 | Confirm zone authorisation from two independent sources | S8, S9 | SG1, SG7 | D |
| F3 | Measure gas state and predict usable reserve | S3, S9 | SG2, SG6 | D |
| F4 | Plan the manoeuvre and check it can be finished after one fault | S9 | SG6 | B |
| F5 | Estimate attitude, height and position | S8 | SG6 | B |
| F6 | Compute flight control laws | S9 | SG5, SG6 | C |
| F7 | Allocate thrust to nozzles, torque first | S9 | SG5, SG6 | C |
| F8 | Actuate thruster valves | S5 | SG1, SG5 | D |
| F9 | Isolate gas (master and line valves) | S4, S9 | SG1, SG2, SG6 | D |
| F10 | Monitor, arbitrate and command recovery; run the backup hop law | S9 | SG1, SG6 | D |
| F11 | Generate downforce | S6 | SG4 | C |
| F12 | Protect occupants (restraints, external airbags) | S11 | SG8 | B |
| F13 | Store and refill gas | S2, S3 | SG2 | D |
| F14 | Vent gas without net thrust | S3, S4 | SG2 | D |

## 4.4 E/E and software architecture

![E/E architecture](figures/F04_ee_architecture.png)

*Figure 3. E/E architecture: two channels each own one of the two master valves in series; the monitor also owns the valve-driver supply, the hold-up store and the backup hop law.*

| Element | Command channel | Monitor channel |
| --- | --- | --- |
| Computer | Thrust control unit: lockstep multicore microcontroller | Independent safety monitor: dissimilar microcontroller from a different supplier |
| Software | Partitioned real-time OS: control laws, allocation, recovery planner, diagnostics; separate logging partition | Small bare-metal program: envelope checks, arm logic, recovery command, backup attitude-hold and descent law |
| Sensors | Two IMUs, one pressure sensor per gas group, altimeters | Own IMU of a different technology, own pressure sensor per group |
| Gas valves owned | Master valve B, line and thruster valves (direct-wired) | Master valve A (with hold-up store), enable of all valve-driver supplies |
| Power | Primary low-voltage feed | Secondary feed with local buffer |
| ASIL after decomposition | B(D) for SG1; C for SG5; B for SG6 | B(D) for SG1; B for SG6 recovery and backup control |

**ASIL decomposition of SG1.** SG1 (ASIL D) is decomposed into the command channel at ASIL B(D) and the monitor channel at ASIL B(D). The decomposition is valid only if the dependent failure analysis (section 8.5) shows the channels are sufficiently independent; the FMEDA in section 8.3 shows common cause is the dominant residual, which is why that analysis is decisive.

**Network.** Thrust messages run on a private, authenticated bus between the two channels. The vehicle network can send only a mode request, zone data and the crash signal, through a filtering gateway. No cellular, Wi-Fi or diagnostic path reaches the thrust domain in production.

**Fail-safe and fail-operational hardware.** Every gas valve is normally closed and spring-return, so loss of power on the ground always closes it (P1). In Hop mode, dual-wound coils, a second driver per master valve and a local hold-up energy store keep the master valves open through any single loss for at least 5 s, and closing them in flight takes an explicit command (P2, TSR-21).

## 4.5 Interfaces

| ID | Signal | From → to | Type | Rate | Max latency | ASIL | Protection |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IF-01 | Arm enable A | Safety monitor → master valve A switch | Hardwired, energise-to-open | Continuous | 5 ms to close | B(D) | Dedicated wire, read-back, short detection |
| IF-02 | Arm enable B | Thrust control unit → master valve B switch | Hardwired, energise-to-open | Continuous | 5 ms to close | B(D) | As IF-01 |
| IF-03 | Thrust command | Thrust control unit → valve drivers | Direct-wired, or two independent buses (TSR-23) | 1 kHz | 2 ms | C | Counter, CRC, timeout, authentication |
| IF-04 | Driver enable | Safety monitor → valve-driver supply | Hardwired | Continuous | 5 ms | B(D) | Read-back |
| IF-05 | Zone authorisation | Positioning and beacon → mode manager | Vehicle bus via gateway | 10 Hz | 200 ms | D (two sources) | Two sources must agree; signed beacon; independent check in the monitor (CC-13) |
| IF-06 | Attitude and rates | IMUs → both computers | Private bus or direct SPI | 1 kHz | 2 ms | B | Three-way voting, plausibility |
| IF-07 | Gas pressure and temperature | Sensors → both computers | Analogue or private bus | 500 Hz | 5 ms | D | Two dissimilar sensors per group |
| IF-08 | Suction plenum pressure | Sensors → vehicle dynamics controller | Vehicle bus | 200 Hz | 10 ms | C | Range and rate checks |
| IF-09 | Mode request | HMI → mode manager | Vehicle bus via gateway | Event | 50 ms | D | Physical arm switch plus two-step confirm |
| IF-10 | Crash signal | Airbag controller → both computers | Hardwired plus bus | Event | 10 ms | D | Redundant paths |
| IF-11 | Line isolation command | Thrust control unit → line valves | Direct-wired | Event | 20 ms | B | Read-back of valve position |

## 4.6 Operating modes

![Operating modes](figures/F05_operating_modes.png)

*Figure 4. Operating modes: thrusters can fire only in Boost and Hop, entered only from Thrust-armed; any fault leads to recovery.*

| Mode | Thrust | Entry conditions |
| --- | --- | --- |
| Road-safe | Physically impossible: master valves unpowered | Default at power-on and on public roads |
| Track | No; suction allowed | Driver request inside an authorised track zone |
| Thrust-armed | Ready, not firing | Track mode, physical arm switch, gas reserve check passed, clear zone confirmed |
| Boost | Rear thrusters | Armed, wheels on ground, straight-line launch |
| Hop | Perimeter thrusters | Armed, Rocket trim, manoeuvre passes the reserve and lift-margin checks |
| Abort and recover | Remaining gas used to level the car, then land | Any fault during Boost or Hop |
| Vent and maintain | No; tanks emptied through diffusers | Service, or a fault that needs gas removed |
| Crash | No; all vessel valves closed | Crash sensors fire, in any mode |

## 4.7 Timing budget

The tightest timing is the stuck-open valve in flight: the FTTI is about 200 ms with 9 kN lift groups (Sim 3), against a 20 ms detection-to-isolation budget. For SG1 the safe state is held continuously, so no reaction time applies.

| Goal | Fault | FTTI | Detection | Decision | Actuation | Budget | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SG6 | Stuck-open thruster valve in flight | 200 ms | 10 ms (line pressure vs command, IMU residual) | 2 ms | 8 ms line valve closes | 20 ms (ceiling 50 ms) | Sim 3 |
| SG6 | Leak or pressure loss in flight | Depends on leak rate | 20 ms (pressure decay vs model) | 2 ms | Next control cycle | 25 ms | Sim 4 |
| SG6 | Thrust control unit lost in flight | Under 200 ms (estimate) | 10 ms (watchdog) | 5 ms | Backup law takes over | 50 ms | TSR-22 |
| SG5 | Asymmetric thrust in launch | About 100 ms (estimate) | 5 ms (yaw rate vs model) | 1 ms | 8 ms master valve closes | 15 ms | Estimate |
| SG4 | Suction loss at high cornering load | About 150 ms (estimate) | 10 ms (plenum pressure) | 5 ms | Speed and cornering limits | 100 ms | Estimate |
| SG2 | Over-pressure while refilling | Seconds | 100 ms | 10 ms | Stop fill; mechanical relief as backup | 1 s | Estimate |

Loop rates: attitude control and allocation 1 kHz; monitor envelope checks 1 kHz; mode manager 100 Hz; zone authorisation 10 Hz.

## 4.8 Architecture decision record

| ID | Decision | Alternatives considered | Rationale | Consequence |
| --- | --- | --- | --- | --- |
| AD-01 | Two normally closed master valves in series, each powered by a different channel | One master valve with redundant drivers | Enables SG1 decomposition into B(D) + B(D); no single valve or driver fault releases gas | Extra valve mass and pressure drop; leak-down test needed to keep faults from going latent |
| AD-02 | Dissimilar safety monitor from a different supplier | Second identical lockstep computer | Reduces common-cause faults, the dominant residual in the FMEDA | Two code bases and tool chains to maintain |
| AD-03 | Recover, then cut, in flight | Cut all gas on any fault | Sim 2: cutting mid-roll lands the car on its roof; recovery lands it upright | Monitor logic must know the flight phase; cutting stays the safe state on the ground |
| AD-04 | Fail-operational hop control: hold-up store, dual-wound coils, backup law | Rely on fail-closed valves | Component FMEA: loss of power or a computer mid-hop otherwise drops the car | More hardware in the monitor channel; must not weaken SG1 on the ground |
| AD-05 | Isolated thrust domain behind an allowlist gateway | Thrust functions on the shared vehicle network | Removes remote attack paths to a severe damage scenario | Updates to the thrust domain only with tanks empty and car present |
| AD-06 | Gas split into at least two vessel groups with own isolation valves | One manifolded bank | A leak or stuck valve costs part of the reserve, not all of it | More valves and sensors |
| AD-07 | Thrust-neutral emergency venting through paired diffusers | Single vent | Venting must not push the car, especially after a crash | Packaging of opposed diffusers |
| AD-08 | Reserve check before every manoeuvre, offering a lower manoeuvre instead of refusing | Fixed minimum fill | Sim 4: without it, 21% of fault-free random hops starve | Availability cost at low fill |
| AD-09 | Monitor confirms the zone independently (inertial dead-reckoning from the last trusted beacon fix) | Both channels use the same zone data | Attack tree: a faked zone otherwise defeats both channels at once | Beacon infrastructure must sign fixes |
