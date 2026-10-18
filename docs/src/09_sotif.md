# 9. SOTIF analysis

ISO 21448 deals with hazards that arise when nothing is broken: the sensors, models or control laws are simply not good enough for the situation. For a hop these are the main risk, because the physics is unforgiving and the domain is new.

## 9.1 Triggering conditions

| ID | Triggering condition | Functional insufficiency | Possible hazard | Measure |
| --- | --- | --- | --- | --- |
| TC-01 | Gust above the planned limit during the roll | Control authority too low | Inverted landing | Wind limit in the operating domain (A-15); gust term in the reserve check |
| TC-02 | Gas colder than predicted after a fast refill | Reserve over-estimated | Gas runs out before landing | Temperature-corrected reserve (TSR-10) |
| TC-03 | Mass or centre of gravity outside the assumed range (luggage, passenger) | Controller tuned for wrong inertia | Roll overshoot | Seat and load sensing; refuse hop if out of range |
| TC-04 | Ground effect and jet reflection near the surface | Thrust model wrong below about 1 m | Bounce or tilt at take-off and landing | Ground-effect term; thrust-stand data |
| TC-05 | Loose gravel or debris | Jets throw debris; suction skirt lifts | Bystander injury; tilt | Surface check in the operating domain |
| TC-06 | Satellite multipath at the track | Position error | Arming outside the zone | Beacon plus inertial cross-check (CC-13) |
| TC-07 | Vibration or ice affects pressure sensing | Biased gas estimate | Wrong reserve decision | Dual dissimilar sensors (TSR-05) |
| TC-08 | Driver input during the hop | Mode confusion | Unexpected manoeuvre | Driver inputs ignored in Hop mode except abort |
| TC-09 | Nozzle thrust scatter above the 3% (1σ) modelled in Sim 4 | Allocation error | Drift and roll error | Closed-loop thrust estimation; thrust-stand calibration |
| TC-10 | Landing surface slope or step | Landing law assumes level ground | Roll on touchdown | Landing pad specification |

## 9.2 Known unsafe scenarios found so far

Sim 4 found no bad outcomes in 2,186 fault-free hops under random fill, temperature, mass, centre-of-gravity, gust and thrust scatter once the reserve check was in place. Without the reserve check, 21% of fault-free hops ran out of gas: that was the largest SOTIF finding of this study and led directly to TSR-10.

## 9.3 Acceptance criterion and validation target

| Item | Value |
| --- | --- |
| Acceptance criterion | Fewer than 10⁻⁷ catastrophic outcomes per hop from SOTIF causes, the same as for random hardware faults |
| Evidence today | Zero bad outcomes in 2,186 fault-free simulated hops gives an upper bound of 1.4 × 10⁻³ per hop at 95% confidence |
| Validation target | About 3 × 10⁷ hop-equivalents with no catastrophic outcome (zero-event rule: n ≥ 3 / 10⁻⁷) |
| How to get there | Mostly simulation with importance sampling of the triggering conditions above, anchored by about 10³ instrumented physical hops that validate the models |

## 9.4 Validation strategy

1. **Model validation.** Thrust-stand tests of each nozzle and of nozzle groups near the ground; tank blowdown tests at cold and hot fills; drop tests for the landing model.
2. **Scenario-based simulation.** A 6-degree-of-freedom model, validated in step 1, run over the triggering-condition space with importance sampling at the edges (gust in the roll, cold gas, mass offset).
3. **HIL.** The real thrust control unit and safety monitor in closed loop with the validated model.
4. **Tethered hops.** Physical hops on a crane tether with an empty cabin, then with ballast, then with a test pilot.
5. **Field monitoring.** Every hop logged; any recovery, refusal or limit exceedance reviewed.
