# 5. Performance and energy budget

The budget turns the disclosed figures into the physical limits every later chapter depends on. All values come from Sim 1 (chapter 14) using the assumptions in Appendix A; the most sensitive is the fill pressure (A-05), which Tesla has not disclosed.

| Quantity | Value | How it is obtained |
| --- | --- | --- |
| Gas volume | 600 L | Disclosed [B1] |
| Fill pressure | About 400 bar | Assumed (A-05); 600 bar would need a stronger vessel class than reported |
| Gas mass at fill | About 244 kg | Real-gas density at 400 bar, 293 K (compressibility Z ≈ 1.17); consistent with the 250 kg figure in [B3] |
| Weight to hold in a hover | About 18.1 kN | 1,850 kg vehicle (A-01) |
| Specific impulse of the jets | 69 s at fill, falling to 48 s as the gas cools | Ideal nozzle expansion of air from the regulated supply |
| Hover endurance, full tanks | 6.7 s | Adiabatic blowdown until supply pressure falls below the regulator minimum |
| Gas left unusable at the end | About 40 kg | Tank pressure falls to about 28 bar |
| Gas temperature at the end of a full discharge | About 142 K (−131 °C) | Adiabatic expansion in the tanks |
| Reference hop (4.5 m apex, 360° roll, soft landing) | 134 kg, 4.15 s, 55% of the fill | Sim 1, Sim 2 |
| Minimum fill to start the reference hop with a 1.2 reserve factor | 86% | Sim 4 |
| Launch, 0–60 mph in 0.9 s (Thrust trim) | 32–46 kg of gas | Thrust needed beyond tyre grip, 13–19% of the fill |
| Launch, 0–60 mph in 0.59 s (Rocket trim) | 46–67 kg of gas | 19–27% of the fill |
| Stored energy if a full bank bursts | About 60 MJ (about 14 kg of TNT) | Isentropic expansion energy of the stored gas |
| Energy to refill, ideal | About 34 kWh | Isothermal compression; a real compressor needs two to three times more |

**What the budget means for the architecture.**

1. *It is a hop, not a flight.* A full bank gives under seven seconds of hover, and one reference hop uses more than half of it. There is no gas for a second attempt, so the reserve check (TSR-10) and recovery on the remaining gas (TSR-11) are essential, not optional.
2. *The vessels are a stored-energy hazard that can be released in milliseconds*, unlike the battery's chemical energy, which is released over seconds to minutes. SG2 is ASIL D for this reason, and vessel placement, shielding and thrust-neutral venting (AD-07) are architecture decisions, not packaging details.
3. *Cold is a design load.* Valves, seals and liners must work at the coldest gas temperature of a full discharge (TSR-18), and refill air must be dry (TSR-19), or ice can jam a valve when it is needed most.
4. *The car cannot refill itself quickly.* An on-board compressor powered from the traction battery would take far longer than a station refill; the operating concept assumes a fill station at the track (UC5).
