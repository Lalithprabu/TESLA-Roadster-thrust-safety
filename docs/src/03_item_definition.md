# 3. Item definition and concept of operations

## 3.1 Item and boundary

The item is the thrust and suction function: gas supply and storage, distribution, thruster array, suction, the sensing and computers that control them, the arming interface and the protection measures specific to it (subsystems S2–S6 and S8–S11, with their links to S1 and S7). The vehicle platform, steering and airbags are outside the item and appear as interfaces. Thrust functions are allowed only inside a bounded operating domain; everywhere else the car is in Road-safe mode, where thrust is physically impossible.

![System context](figures/F01_system_context.png)

*Figure 1. System context: the item, its eight actors and the only two that can contribute to enabling thrust.*

## 3.2 Use cases

| ID | Use case | Who | Mode | Trim |
| --- | --- | --- | --- | --- |
| UC1 | Normal road driving | Owner | Road-safe | All |
| UC2 | Track driving with suction | Owner | Track | All |
| UC3 | Straight-line boost launch | Owner | Boost | Thrust, Rocket |
| UC4 | Hop or roll manoeuvre | Invited pilot | Hop | Rocket |
| UC5 | Refill the air tanks | Fill-station operator | Road-safe | Thrust, Rocket |
| UC6 | Service, inspect and vent the tanks | Technician | Vent and maintain | Thrust, Rocket |
| UC7 | Crash in any mode | — | Crash | All |
| UC8 | Remote-operated test (development only) | Test engineer | Hop | Prototype |

## 3.3 Operating domain for thrust functions

| Dimension | Allowed | Monitored by |
| --- | --- | --- |
| Location | Authorised track or closed site inside a geofence | Satellite positioning plus signed track beacon |
| People | Nobody inside the clear zone (proposed 50 m for Hop, 20 m for Boost) | Cameras and site procedure |
| Surface | Dry, sealed, paved; no loose gravel | Suction plenum pressure, cameras |
| Wind | Sustained under 8 m/s, gusts under 12 m/s | Site anemometer feed |
| Temperature | −10 to +40 °C ambient | Vehicle sensors |
| Weather | No rain, snow or ice; daylight | Rain sensor, site procedure |
| Occupants | Belted; harness and helmet in Rocket trim | Seat sensors |
| Vehicle state | Gas above reserve; all pre-arm checks passed; no active faults | Mode manager |
| Manoeuvre | Hop apex up to 6 m; Boost in a straight line only | Trajectory planner |

## 3.4 Foreseeable misuse

- Firing thrusters on public roads or in car parks.
- Spoofing or disabling the geofence or beacon (see TS3, TS4 in chapter 10).
- Refilling with wet air, oxygen-enriched air or another gas at an unapproved station.
- Carrying a passenger in the single-seat Rocket trim, or loose cargo during a hop.
- Letting spectators stand inside the clear zone.
