"""
Shared models for the Roadster thrust-system simulation package.

Independent engineering model built from public information (Tesla reveal,
15 Oct 2026). Every parameter marked ASSUMED is an estimate, not Tesla data.

Coordinate frame (planar roll model, vehicle seen from behind):
    y  lateral (m, +right), z height (m, +up), phi roll angle (rad, CCW +).
    Body "up" unit vector  u = (-sin phi,  cos phi)
    Body "right" unit vector r = ( cos phi,  sin phi)
    A lift thruster at body lateral offset d pushes along u and makes torque d*F.
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- constants
G = 9.81                 # m/s^2
R_AIR = 287.05           # J/(kg K)
GAMMA = 1.4
P_ATM = 1.013e5          # Pa
RHO_AIR = 1.2            # kg/m^3 ambient

# Vandenkerckhove function for gamma = 1.4
GAMMA_FN = np.sqrt(GAMMA) * (2 / (GAMMA + 1)) ** ((GAMMA + 1) / (2 * (GAMMA - 1)))

# ---------------------------------------------------------------- vehicle
MASS = 1850.0            # kg, ASSUMED from "4,000+ lb" (TechCrunch, MKBHD quote)
I_ROLL = 600.0           # kg m^2, ASSUMED roll inertia of a low sports car
SIDE_AREA = 4.0          # m^2, ASSUMED projected side area
CD_SIDE = 1.0            # ASSUMED side-force coefficient

# ---------------------------------------------------------------- gas storage
TANK_VOLUME = 0.600      # m^3, DISCLOSED (600 litres, L. Moravy)
P_FILL_BAR = 400.0       # bar, DERIVED: 250 kg in 600 L at 293 K needs ~400 bar
T_FILL = 293.15          # K
Z_SLOPE = 0.00042        # 1/bar, ASSUMED linear compressibility Z = 1 + a*p (air, ~293 K)
P_REG_BAR = 40.0         # bar, ASSUMED regulated feed pressure to the nozzles
P_MIN_BAR = 50.0         # bar, ASSUMED tank pressure below which full thrust is lost
CF = 1.35                # ASSUMED thrust coefficient incl. nozzle losses

# ---------------------------------------------------------------- thrusters
# Rocket trim: 10 nozzles. In the roll plane they collapse into four lift groups
# (outer/inner, left/right) plus two lateral groups. ASSUMED layout.
LIFT_D = np.array([-0.85, -0.35, 0.35, 0.85])    # m, lateral offsets LO, LI, RI, RO
LIFT_MAX = 9000.0                                # N per lift group (T/W ~ 2.0)
SIDE_MAX = 4000.0                                # N per lateral group
N_LIFT = 4
LO, LI, RI, RO = 0, 1, 2, 3


def z_factor(p_bar):
    return 1.0 + Z_SLOPE * p_bar


def pressure_bar(rho, T):
    """Pressure from density and temperature with linear compressibility."""
    a = rho * R_AIR * T / 1e5          # ideal-gas pressure in bar
    return a / (1.0 - Z_SLOPE * a)


def fill_mass(p_bar=P_FILL_BAR, T=T_FILL, volume=TANK_VOLUME):
    rho = p_bar * 1e5 / (z_factor(p_bar) * R_AIR * T)
    return rho * volume


def c_star(T):
    """Characteristic velocity (m/s) of air at stagnation temperature T."""
    return np.sqrt(GAMMA * R_AIR * np.maximum(T, 60.0)) / GAMMA_FN


def isp(T):
    return CF * c_star(T) / G


class Tank:
    """Lumped adiabatic blowdown tank (vectorised over runs)."""

    def __init__(self, m0, T0=T_FILL, volume=TANK_VOLUME):
        self.m0 = np.asarray(m0, dtype=float)
        self.m = self.m0.copy()
        self.T0 = np.asarray(T0, dtype=float) * np.ones_like(self.m0)
        self.V = volume
        self.rho0 = self.m0 / self.V

    @property
    def T(self):
        # isentropic expansion of the gas left in the tank (no wall heat transfer)
        return self.T0 * (np.maximum(self.m, 1e-6) / self.V / self.rho0) ** (GAMMA - 1)

    @property
    def p_bar(self):
        return pressure_bar(self.m / self.V, self.T)

    def capability(self):
        """Fraction of full thrust available (regulator drops out below P_MIN)."""
        return np.clip((self.p_bar - 5.0) / (P_MIN_BAR - 5.0), 0.0, 1.0)

    def draw(self, thrust_total, dt, leak_kg_s=0.0):
        mdot = thrust_total / (CF * c_star(self.T)) + leak_kg_s
        self.m = np.maximum(self.m - mdot * dt, 0.0)
        return mdot


def smoothstep(s):
    s = np.clip(s, 0.0, 1.0)
    return s * s * (3 - 2 * s)


def smoothstep_d(s):
    inside = (s > 0) & (s < 1)
    return np.where(inside, 6 * s * (1 - s), 0.0)


def smoothstep_dd(s):
    inside = (s > 0) & (s < 1)
    return np.where(inside, 6 - 12 * s, 0.0)


# ---------------------------------------------------------------- hop guidance
# Reference manoeuvre: vertical hop, 360-degree roll near the apex, soft landing.
CLIMB_T = 1.3        # s to reach apex
APEX = 4.5           # m
ROLL_T0 = 0.9        # s roll start (still climbing)
ROLL_DUR = 1.1       # s
DESCENT_T0 = 2.2     # s
DESCENT_RATE = 1.5   # m/s


def guidance(t):
    """Return z_ref, vz_ref, az_ref, phi_ref, w_ref, a_ref (arrays OK)."""
    t = np.asarray(t, dtype=float)
    s = t / CLIMB_T
    z_climb = APEX * smoothstep(s)
    vz_climb = APEX * smoothstep_d(s) / CLIMB_T
    az_climb = APEX * smoothstep_dd(s) / CLIMB_T ** 2
    td = t - DESCENT_T0
    descending = td > 0
    z_ref = np.where(descending, np.maximum(APEX - DESCENT_RATE * td, -0.5), z_climb)
    vz_ref = np.where(descending, -DESCENT_RATE, vz_climb)
    az_ref = np.where(descending, 0.0, az_climb)
    r = (t - ROLL_T0) / ROLL_DUR
    phi_ref = 2 * np.pi * smoothstep(r)
    w_ref = 2 * np.pi * smoothstep_d(r) / ROLL_DUR
    a_ref = 2 * np.pi * smoothstep_dd(r) / ROLL_DUR ** 2
    return z_ref, vz_ref, az_ref, phi_ref, w_ref, a_ref


def wrap_pi(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


# ---------------------------------------------------------------- allocation
def allocate(force_u, torque, available, cap, lift_max=LIFT_MAX):
    """
    Split a body-up force and a roll torque across the four lift groups.

    force_u, torque : (N,) commands
    available       : (N, 4) bool, False for an isolated/failed group
    cap             : (N,) thrust capability fraction from the tank
    Torque has priority (attitude before altitude). Returns (N, 4) thrusts.
    """
    fmax = lift_max * cap[:, None] * available
    F = np.zeros_like(fmax)
    # 1) torque from the strongest available lever on the needed side
    pos = torque > 0
    for side_idx in ([RO, RI], [LO, LI]):
        mask = pos if side_idx[0] == RO else ~pos
        need = np.abs(torque) * mask
        for j in side_idx:
            give = np.minimum(need / np.abs(LIFT_D[j]), fmax[:, j])
            F[:, j] += give
            need = need - give * np.abs(LIFT_D[j])
    # 2) remaining body-up force spread symmetrically (torque-neutral pairs)
    rem = np.maximum(force_u - F.sum(axis=1), 0.0)
    for (a, b) in ((LI, RI), (LO, RO)):
        head_a = fmax[:, a] - F[:, a]
        head_b = fmax[:, b] - F[:, b]
        add = np.minimum(rem / 2, np.minimum(head_a, head_b))
        F[:, a] += add
        F[:, b] += add
        rem = rem - 2 * add
    return F


# ---------------------------------------------------------------- simulator
class HopSim:
    """
    Vectorised planar hop simulator with fault injection.

    faults (per run arrays, optional):
        stuck_open_t   time (s) RO valve sticks fully open (inf = never)
        stuck_closed_t time (s) LO valve sticks closed
        leak_t, leak_rate  time (s) and kg/s of a tank leak
        detect_delay   s from fault to detection + actuation
        strategy       0 = none (undetected), 1 = cut all gas, 2 = isolate + recover
    """

    def __init__(self, n, mass=MASS, inertia=I_ROLL, gas_kg=None, gas_T=T_FILL,
                 cg_offset=0.0, gust=0.0, gust_t=0.0, thrust_scale=1.0,
                 stuck_open_t=np.inf, stuck_closed_t=np.inf,
                 leak_t=np.inf, leak_rate=0.0, detect_delay=0.02, strategy=2,
                 lift_max=LIFT_MAX, dt=0.002, t_end=7.0):
        b = lambda x: np.broadcast_to(np.asarray(x, dtype=float), (n,)).copy()
        self.n = n
        self.m = b(mass)
        self.I = b(inertia)
        self.cg = b(cg_offset)
        self.gust = b(gust)
        self.gust_t = b(gust_t)
        self.kth = b(thrust_scale)
        self.so_t = b(stuck_open_t)
        self.sc_t = b(stuck_closed_t)
        self.leak_t = b(leak_t)
        self.leak_rate = b(leak_rate)
        self.delay = b(detect_delay)
        self.strategy = np.broadcast_to(np.asarray(strategy), (n,)).copy()
        self.tank = Tank(b(fill_mass() if gas_kg is None else gas_kg), b(gas_T))
        self.fmax = lift_max
        self.dt = dt
        self.t_end = t_end

    def run(self, record=False):
        n, dt = self.n, self.dt
        y = np.zeros(n); z = np.zeros(n); vy = np.zeros(n); vz = np.zeros(n)
        phi = np.zeros(n); w = np.zeros(n)
        alive = np.ones(n, bool)                 # still flying
        cut = np.zeros(n, bool)                  # master valve closed
        iso = np.zeros(n, bool)                  # RO line isolated
        recovering = np.zeros(n, bool)
        rec_t = np.full(n, np.inf)
        land = dict(t=np.full(n, np.nan), phi=np.full(n, np.nan),
                    vz=np.full(n, np.nan), vy=np.full(n, np.nan), y=np.full(n, np.nan))
        gas_used_at_land = np.full(n, np.nan)
        hist = [] if record else None
        t = 0.0
        while t < self.t_end and alive.any():
            zr, vzr, azr, phr, wr, ar = guidance(t)
            # recovery guidance: hold nearest upright attitude, descend
            up_target = 2 * np.pi * np.round((phi + 0.25 * w) / (2 * np.pi))   # predict 0.25 s ahead
            phr_v = np.where(recovering, up_target, phr)
            wr_v = np.where(recovering, 0.0, wr)
            ar_v = np.where(recovering, 0.0, ar)
            # descent (nominal after DESCENT_T0, or in recovery): velocity law
            descend = recovering | (t > DESCENT_T0)
            v_des = -np.clip(1.3 * z + 0.3, 0.8, 4.0)
            zr_v = np.where(descend, z, zr)
            vzr_v = np.where(descend, v_des, vzr)
            azr_v = np.where(descend, 0.0, azr)
            # ---- controller (PD with feed-forward)
            e_phi = phr_v - phi
            torque = self.I * (ar_v + 36.0 * e_phi + 12.0 * (wr_v - w))
            az_cmd = azr_v + 4.0 * (zr_v - z) + 4.0 * (vzr_v - vz)
            c = np.cos(phi)
            upright = c > 0.35
            force_u = np.where(upright, self.m * (G + az_cmd) / np.maximum(c, 0.35), 0.0)
            # ---- fault states
            so_active = t >= self.so_t
            sc_active = t >= self.sc_t
            detected_so = t >= self.so_t + self.delay
            # strategies react to a detected stuck-open valve
            newly = detected_so & alive & ~cut & ~iso & ~recovering
            cut |= newly & (self.strategy == 1)
            start_rec = newly & (self.strategy == 2)
            iso |= start_rec
            recovering |= start_rec
            rec_t = np.where(start_rec, t, rec_t)
            # leak or stuck-closed valve: naive monitor cuts, recovery aborts the manoeuvre
            other = ((t >= self.leak_t + self.delay) | (t >= self.sc_t + self.delay))
            other_new = other & alive & ~cut & ~recovering
            cut |= other_new & (self.strategy == 1)
            start2 = other_new & (self.strategy == 2)
            recovering |= start2
            rec_t = np.where(start2, t, rec_t)
            available = np.ones((n, N_LIFT), bool)
            available[:, RO] = ~iso
            available[:, LO] &= ~sc_active          # stuck closed: no thrust
            cap = self.tank.capability() * self.kth
            F = allocate(force_u, torque, available, cap, self.fmax)
            stuck_now = so_active & ~iso & ~cut
            F[:, RO] = np.where(stuck_now, self.fmax * self.tank.capability(), F[:, RO])
            F = np.where(cut[:, None] | ~alive[:, None], 0.0, F)
            # ---- lateral station keeping with the side groups (upright only)
            Fside = np.clip(self.m * (-1.5 * y - 2.5 * vy), -SIDE_MAX, SIDE_MAX)
            Fside = Fside * cap * upright * ~cut * alive
            # ---- forces
            Fsum = F.sum(axis=1)
            leak = np.where(t >= self.leak_t, self.leak_rate, 0.0)
            self.tank.draw(np.where(alive, Fsum + np.abs(Fside), 0.0), dt,
                           np.where(alive, leak, 0.0))
            tq = (F * (LIFT_D[None, :] - self.cg[:, None])).sum(axis=1)
            wind = np.where(t >= self.gust_t, self.gust, 0.0)
            v_rel = wind - vy
            area = SIDE_AREA * np.abs(np.cos(phi)) + 1.8 * np.abs(np.sin(phi))
            Fw = 0.5 * RHO_AIR * CD_SIDE * area * v_rel * np.abs(v_rel)
            ay = (-np.sin(phi) * Fsum + np.cos(phi) * Fside + Fw) / self.m
            azz = (np.cos(phi) * Fsum + np.sin(phi) * Fside) / self.m - G
            al = (tq + 0.1 * Fw) / self.I
            # ---- integrate (semi-implicit Euler)
            vy = np.where(alive, vy + ay * dt, vy)
            vz = np.where(alive, vz + azz * dt, vz)
            w = np.where(alive, w + al * dt, w)
            y = np.where(alive, y + vy * dt, y)
            z = np.where(alive, z + vz * dt, z)
            phi = np.where(alive, phi + w * dt, phi)
            t += dt
            if record:
                hist.append((t, y.copy(), z.copy(), phi.copy(), vz.copy(), F.copy(),
                             self.tank.p_bar.copy(), self.tank.T.copy(), self.tank.m.copy()))
            touch = alive & (z <= 0.0) & (t > 0.3)
            if touch.any():
                land['t'][touch] = t
                land['phi'][touch] = wrap_pi(phi[touch])
                land['vz'][touch] = vz[touch]
                land['vy'][touch] = vy[touch]
                land['y'][touch] = y[touch]
                gas_used_at_land[touch] = (self.tank.m0 - self.tank.m)[touch]
                alive &= ~touch
        land['gas_used'] = gas_used_at_land
        land['gas_left'] = self.tank.m
        return land, hist


def classify(land):
    """Return masks: safe, hard, unsafe_attitude, no_land."""
    phi = np.abs(land['phi'])
    vz = land['vz']
    no_land = np.isnan(phi)
    unsafe_att = (phi > np.radians(30)) & ~no_land
    hard = (~unsafe_att) & (vz < -5.0) & ~no_land
    safe = (~unsafe_att) & (~hard) & ~no_land
    return safe, hard, unsafe_att, no_land
