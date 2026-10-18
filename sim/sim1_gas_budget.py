"""
Sim 1 - Gas budget and tank blowdown.

Questions answered
  * How much air is on board at the derived fill pressure?
  * How long can the car hover before the regulator drops out?
  * How cold does the gas get, and what does that do to specific impulse?
  * Stored burst energy and minimum refill energy.
"""
import json
import numpy as np
from common import (Tank, fill_mass, isp, MASS, G, N_LIFT, LIFT_MAX, P_FILL_BAR,
                    TANK_VOLUME, T_FILL, R_AIR, GAMMA, P_ATM, HopSim)
import plotstyle as ps


def hover_blowdown(dt=0.005):
    tank = Tank(np.array([fill_mass()]))
    thrust = MASS * G
    t, rows = 0.0, []
    while True:
        cap = tank.capability()[0]
        rows.append((t, tank.p_bar[0], tank.T[0], tank.m[0], isp(tank.T[0]), cap))
        if cap * N_LIFT * LIFT_MAX < thrust or tank.m[0] <= 0:
            break
        tank.draw(np.array([thrust]), dt)
        t += dt
    return np.array(rows)


def burst_energy_mj(p_bar=P_FILL_BAR, volume=TANK_VOLUME):
    # Brode equation, the standard expression for pressure-vessel blast energy
    return (p_bar * 1e5 - P_ATM) * volume / (GAMMA - 1) / 1e6


def refill_energy_kwh(mass, p_bar=P_FILL_BAR, T=T_FILL):
    # minimum (isothermal) compression work from 1 atm
    return mass * R_AIR * T * np.log(p_bar * 1e5 / P_ATM) / 3.6e6


def main():
    m0 = fill_mass()
    hb = hover_blowdown()
    hover_time = hb[-1, 0]
    land, _ = HopSim(1, strategy=0).run()
    res = {
        "fill_pressure_bar": P_FILL_BAR,
        "gas_mass_kg": round(float(m0), 1),
        "hover_endurance_s": round(float(hover_time), 2),
        "gas_used_hover_kg": round(float(m0 - hb[-1, 3]), 1),
        "end_pressure_bar": round(float(hb[-1, 1]), 1),
        "end_temperature_K": round(float(hb[-1, 2]), 1),
        "isp_start_s": round(float(hb[0, 4]), 1),
        "isp_end_s": round(float(hb[-1, 4]), 1),
        "reference_hop_gas_kg": round(float(land["gas_used"][0]), 1),
        "reference_hop_duration_s": round(float(land["t"][0]), 2),
        "burst_energy_MJ": round(burst_energy_mj(), 1),
        "burst_energy_kg_TNT": round(burst_energy_mj() / 4.184, 1),
        "refill_energy_ideal_kWh": round(float(refill_energy_kwh(m0)), 1),
    }
    ps.setup()
    fig, axes = ps.plt.subplots(1, 2, figsize=(9.6, 3.9))
    t = hb[:, 0]
    axes[0].plot(t, hb[:, 1], color=ps.BLUE)
    axes[0].set_title("Tank pressure (bar)")
    axes[0].set_xlabel("Hover time (s)")
    axes[0].axhline(50, color=ps.GREY, lw=1, ls="--")
    axes[0].text(0.15, 60, "regulator drop-out 50 bar", ha="left", color=ps.INK2, fontsize=9)
    axes[1].plot(t, hb[:, 2] - 273.15, color=ps.ORANGE)
    axes[1].set_title("Gas temperature in tank (°C)")
    axes[1].set_xlabel("Hover time (s)")
    for ax in axes:
        ax.set_xlim(0, t[-1] * 1.02)
    ps.headline(fig, f"A full tank holds a hover for about {hover_time:.1f} s",
                f"{m0:.0f} kg of air at {P_FILL_BAR:.0f} bar; adiabatic blowdown, 1,850 kg car")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig("fig1_gas_budget.png", dpi=160)
    print(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    main()
