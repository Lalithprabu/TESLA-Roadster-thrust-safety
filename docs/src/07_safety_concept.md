# 7. Functional and technical safety concept

## 7.1 Functional safety requirements

Each safety goal is refined into functional safety requirements that say *what* the system must do, without naming hardware.

{{table:fsr}}

## 7.2 Safety mechanisms

| Mechanism | Detects | Reaction | Goal | Covered by |
| --- | --- | --- | --- | --- |
| Two-channel arming with master valves in series | Wrong arming decision by either computer | The other channel's valve stays closed | SG1 | TSR-01, TSR-02 |
| Power-on leak-down test of master valves | Latent stuck-open or leaking master valve | Thrust locked out | SG1, SG2 | TSR-03 |
| Pre-arm valve function test | Stuck-open or stuck-closed thruster, line or master valve | Arming refused | SG1, SG6 | TSR-16 |
| Line pressure against command, IMU residual | Stuck-open thruster valve in flight | Line isolated within 20 ms, others compensate | SG5, SG6 | TSR-09, TSR-15 |
| Gas reserve prediction | Too little gas to finish after one fault | Lower manoeuvre offered or recovery started | SG6 | TSR-10, TSR-11 |
| Monitor envelope check | Attitude, rate or height outside the planned envelope | Recovery commanded, not gas cut | SG6 | TSR-12, TSR-20 |
| IMU voting with dissimilar check | Single attitude-sensor fault | Faulty sensor masked | SG6 | TSR-13 |
| Fail-operational hop hardware | Power, coil, switch or computer loss mid-hop | Master valves held open; backup law takes over | SG6 | TSR-21, TSR-22, TSR-23 |
| Plenum pressure monitoring | Suction loss | Speed and cornering limits, warning | SG4 | TSR-08 |
| Crash isolation | Crash or fire | All vessel valves close; thrust-neutral venting | SG2 | TSR-07 |
| Dual dissimilar pressure sensing | Pressure sensor fault | Faulty reading masked; fill or hop refused | SG2, SG6 | TSR-05 |
| Fill-coupling dew-point check | Wet refill air | Fill refused | SG2 | TSR-19 |
| Airbag arming window | Deployment outside Hop mode | Airbags stay disarmed | SG8 | TSR-14 |

## 7.3 Degradation and warning concept

| Situation | System response | Driver information |
| --- | --- | --- |
| Any fault detected on the ground | Road-safe mode; thrust locked out until service | Warning; thrust functions greyed out |
| Gas below reserve before a hop | Lower manoeuvre offered | Message with the largest manoeuvre available |
| Fault during Boost | Thrust cut; car stays on its wheels | Warning |
| Fault during a hop | Recover with remaining gas: level first, then descend and land | Recovery indicator; harness pre-tension |
| Second fault during recovery | Backup law holds attitude and descends; external airbags armed | As above |
| Suction loss in Track mode | Speed and cornering limits within 100 ms | Warning |

## 7.4 Technical safety requirements

Technical safety requirements say *how*, allocate each function to an architecture element of chapter 4 and name the verification item that will prove it. They are generated from the requirements database (`data/technical_safety_requirements.csv`).

{{table:tsr}}
