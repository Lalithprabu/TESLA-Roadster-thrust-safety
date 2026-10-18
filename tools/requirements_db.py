"""
Single source of truth for the RTS-SSC-001 requirements and traceability data.

Running this module writes every table to ../data/*.csv. The document build
(tools/build_docs.py) renders the same tables into the concept document, and
tools/check_traceability.py checks every link, so the document, the CSV files
and the checks cannot drift apart.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

HAZARDS = [  # id, hazardous event, operational situation, S, E, C, ASIL, goal
    ("HE1", "Unintended thruster firing", "Driving on a public road", "S3", "E4", "C3", "D", "SG1"),
    ("HE2", "Unintended thruster firing", "Parking or low speed near people", "S3", "E4", "C2", "C", "SG1"),
    ("HE3", "COPV rupture or uncontrolled venting", "Any driving or parking", "S3", "E4", "C3", "D", "SG2"),
    ("HE4", "Loss of steering", "Any driving (steer-by-wire)", "S3", "E4", "C3", "D", "SG3"),
    ("HE5", "Sudden loss of suction at high cornering load", "Track mode, near 2G", "S3", "E3", "C3", "C", "SG4"),
    ("HE6", "Asymmetric thrust during launch", "Boost, 3-4.6 g straight-line launch", "S3", "E3", "C3", "C", "SG5"),
    ("HE7", "Loss of thrust mid-manoeuvre (gas used up, leak, icing, valve closure)", "Hop", "S3", "E2", "C3", "B", "SG6"),
    ("HE8", "Stuck-open, stuck-closed or wrong-direction thruster", "Hop", "S3", "E2", "C3", "B", "SG6"),
    ("HE9", "Jet blast or car strikes a bystander", "Hop or Boost with a person in the area", "S3", "E2", "C3", "B", "SG7"),
    ("HE10", "Unintended external airbag deployment", "Highway driving", "S2", "E4", "C2", "B", "SG8"),
    ("HE11", "Loss of suction while inverted", "Inverted-ramp stunt", "S3", "E1", "C3", "A", "SG6"),
]

GOALS = [  # id, safety goal, ASIL, safe state, FTTI
    ("SG1", "Prevent thrust unless armed in an authorised zone with a valid driver command", "D", "Master valves closed (Road-safe)", "Preventive"),
    ("SG2", "Prevent COPV rupture or uncontrolled venting from harming anyone", "D", "Vessels isolated; thrust-neutral venting", "Seconds (fill over-pressure)"),
    ("SG3", "Maintain steering control", "D", "Redundant steer-by-wire, degraded mode", "Per steering item"),
    ("SG4", "Prevent a loss of downforce greater than the chassis can handle", "C", "Speed and cornering limits, warning", "About 150 ms (estimate)"),
    ("SG5", "Prevent asymmetric thrust during a launch", "C", "Cut thrust (safe on the ground)", "About 100 ms (estimate)"),
    ("SG6", "Ensure any started manoeuvre can be finished and landed upright after one fault", "B + FHA target 1e-7 per hop", "Level the car, land, then cut", "200 ms (Sim 3)"),
    ("SG7", "Prevent jet blast or the car striking a person", "B", "Refuse to arm", "Preventive"),
    ("SG8", "Prevent external airbag deployment outside Hop mode", "B", "Airbags disarmed", "Preventive"),
]

FSR = [  # id, functional safety requirement, goal, ASIL
    ("FSR-1.1", "Keep the gas path to the nozzles closed unless two independent channels both authorise it", "SG1", "D"),
    ("FSR-1.2", "Authorise thrust only with driver consent, an authorised zone confirmed by two independent sources and passed pre-arm checks", "SG1", "D"),
    ("FSR-1.3", "Accept thrust commands only from authenticated sources inside the thrust domain", "SG1", "D"),
    ("FSR-2.1", "Contain the stored gas under all foreseeable pressure, temperature and impact loads", "SG2", "D"),
    ("FSR-2.2", "On crash or fire, isolate every vessel and vent only without net thrust", "SG2", "D"),
    ("FSR-3.1", "Maintain steering control (allocated to the steer-by-wire item; outside this item)", "SG3", "D"),
    ("FSR-4.1", "Detect loss of downforce and limit speed and cornering before grip is exceeded", "SG4", "C"),
    ("FSR-5.1", "Detect asymmetric thrust during a launch and stop it", "SG5", "C"),
    ("FSR-6.1", "Start a manoeuvre only when the remaining gas can finish it after one fault", "SG6", "B"),
    ("FSR-6.2", "Respond to any in-flight fault with recovery to an upright landing, never with loss of all thrust", "SG6", "B"),
    ("FSR-6.3", "Isolate a faulty thruster path and compensate with the others", "SG6", "B"),
    ("FSR-6.4", "Estimate attitude, height and gas state with tolerance to one sensor fault", "SG6", "B"),
    ("FSR-7.1", "Refuse to arm unless the clear zone is empty and wind is within limits", "SG7", "B"),
    ("FSR-8.1", "Arm external airbags only in Hop mode above 1.5 m", "SG8", "B"),
]

TSR = [  # id, technical safety requirement, ASIL, FSRs, elements, verification ids, evidence
    ("TSR-01", "Two normally closed master valves in series: valve A powered only by the safety monitor, valve B only by the thrust control unit", "B(D) + B(D)", "FSR-1.1", "S4, S9, IF-01, IF-02", "VER-01", "Sim 7 FMEDA"),
    ("TSR-02", "Arming requires Track mode, a physical arm switch, zone authorisation from two independent sources, speed and wind within limits, belts fastened and a clear zone", "D", "FSR-1.2, FSR-7.1", "S8, S9, S10, IF-05, IF-09", "VER-02, VER-20", ""),
    ("TSR-03", "A leak-down test of the master valves runs at every power-on; a failure locks out thrust", "D", "FSR-1.1", "S4, S8, S9", "VER-01", "Sim 7 FMEDA"),
    ("TSR-04", "Thrust messages are authenticated; production cars have no remote thrust path", "D", "FSR-1.3", "S9, IF-03", "VER-03, VER-21", "TARA"),
    ("TSR-05", "Pressure is measured by two dissimilar sensors per gas group, with temperature compensation", "D", "FSR-6.4, FSR-2.1", "S3, S8, IF-07", "VER-04", "Sim 7 FMEA"),
    ("TSR-06", "COPVs meet a burst ratio of 2.25 or more and pass pressure-cycling, fire, drop and impact tests equivalent to UN GTR 13", "Design standard", "FSR-2.1", "S3", "VER-05", ""),
    ("TSR-07", "On crash detection all vessel valves close within 50 ms; venting only through thrust-neutral diffusers away from the cabin", "D", "FSR-2.2", "S3, S4, S11, IF-10", "VER-06", ""),
    ("TSR-08", "Loss of suction is detected from plenum pressure and speed and cornering limits apply within 100 ms, with a warning", "C", "FSR-4.1", "S6, S7, IF-08", "VER-07", ""),
    ("TSR-09", "A stuck-open thruster valve is detected and its line isolated within 20 ms (hard ceiling 50 ms)", "B", "FSR-5.1, FSR-6.3", "S4, S5, S9, IF-11", "VER-08", "Sim 2, Sim 3"),
    ("TSR-10", "A hop starts only if usable gas is at least 1.2 times the predicted need, corrected for mass and gas temperature; otherwise a lower manoeuvre is offered", "B", "FSR-6.1", "S3, S9", "VER-09", "Sim 4"),
    ("TSR-11", "If predicted gas at landing falls below the reserve mid-manoeuvre, recovery starts at once: level attitude first, then land", "B", "FSR-6.2", "S9", "VER-10", "Sim 4"),
    ("TSR-12", "While airborne the safety monitor commands recovery instead of closing the master valves, unless thrust itself is the uncontainable fault", "B", "FSR-6.2", "S9", "VER-11", "Sim 2"),
    ("TSR-13", "Attitude comes from three IMUs with voting; the monitor checks it with a dissimilar sensor", "B", "FSR-6.4", "S8, IF-06", "VER-12", ""),
    ("TSR-14", "External airbags arm only in Hop mode above 1.5 m and are disarmed by two independent signals on landing", "B", "FSR-8.1", "S11", "VER-13", "Sim 5"),
    ("TSR-15", "After isolating any one lift group, the remaining torque-balanced groups lift at least 1.1 times maximum vehicle weight (about 10 kN per group)", "B", "FSR-6.3", "S5", "VER-14", "Sim 3, Sim 4"),
    ("TSR-16", "Before every arming each thruster, line and master valve is cycled against a pressurised test volume; coverage of stuck-open and stuck-closed faults at least 99.9%", "D", "FSR-1.1, FSR-6.3", "S4, S5, S9", "VER-15", "Sim 6, Sim 7"),
    ("TSR-17", "Any single stuck-closed nozzle leaves at least 50% of nominal roll-braking authority (individually controlled nozzles)", "B", "FSR-6.3", "S5, S9", "VER-16", "Gap found (Sim 4)"),
    ("TSR-18", "COPVs, valves and seals are qualified to the lowest gas temperature of a full discharge, or discharge is limited to their qualified temperature", "D", "FSR-2.1", "S3, S4, S5", "VER-17", "Sim 1"),
    ("TSR-19", "Refill air is dried to a dew point below -40 C, checked at the coupling; otherwise the fill is refused", "D", "FSR-2.1", "S2", "VER-18", ""),
    ("TSR-20", "The recovery planner chooses the upright attitude reachable with the least altitude loss, using the predicted stopping angle", "B", "FSR-6.2", "S9", "VER-19", "Gap found (Sim 3)"),
    ("TSR-21", "In Hop mode no single loss of power, coil, switch or computer closes a master valve for at least 5 s (dual-wound coils, second driver, hold-up energy); closing in flight needs an explicit command", "B", "FSR-6.2", "S1, S4, S9", "VER-22", "Sim 7 FMEA"),
    ("TSR-22", "Hop-mode control is fail-operational for at least 5 s: a backup attitude-hold and descent law on independent hardware takes over within 50 ms", "B", "FSR-6.2", "S9", "VER-23", "Sim 7 FMEA"),
    ("TSR-23", "Thruster and line valve commands are direct-wired or carried on two independent buses; a lost command opens nothing new", "B", "FSR-6.2", "S9, IF-03, IF-11", "VER-24", "Sim 7 FMEA"),
]

ELEMENTS = [  # id, name, type, description
    ("S1", "High-voltage energy", "Subsystem", "Battery pack and DC-DC converters powering compressor, fans, valves and compute"),
    ("S2", "Gas supply", "Subsystem", "Onboard compressor, air dryer, ground fill port, check valves"),
    ("S3", "Gas storage", "Subsystem", "COPV bank (about 600 L at 400 bar), per-vessel isolation and relief, pressure and temperature sensing"),
    ("S4", "Distribution", "Subsystem", "Two normally closed master valves in series, regulators, manifold, line valves"),
    ("S5", "Thruster array", "Subsystem", "Rear nozzles (Thrust) or 10 perimeter nozzles (Rocket) with fast electric valves and heaters"),
    ("S6", "Suction", "Subsystem", "Multi-mode fans, ground-sealing skirt, plenum pressure sensors"),
    ("S7", "Chassis", "Subsystem", "Motors, brakes, steer-by-wire, active suspension, active aero"),
    ("S8", "Sensing", "Subsystem", "Three IMUs, altimeters, satellite positioning, wheel speeds, cameras"),
    ("S9", "Control compute", "Subsystem", "Mode manager, vehicle dynamics controller, thrust control unit, independent safety monitor"),
    ("S10", "HMI and arming", "Subsystem", "Yoke, mode selector, physical arm switch, displays and alarms"),
    ("S11", "Protection", "Subsystem", "Restraints, rollover structure, external airbags, thrust-neutral emergency venting"),
    ("IF-01", "Arm enable A", "Interface", "Safety monitor to master valve A switch; hardwired, energise-to-open"),
    ("IF-02", "Arm enable B", "Interface", "Thrust control unit to master valve B switch; hardwired, energise-to-open"),
    ("IF-03", "Thrust command", "Interface", "Thrust control unit to valve drivers; 1 kHz, 2 ms, authenticated"),
    ("IF-04", "Driver enable", "Interface", "Safety monitor to valve-driver supply; hardwired"),
    ("IF-05", "Zone authorisation", "Interface", "Positioning and beacon to mode manager; 10 Hz, two sources"),
    ("IF-06", "Attitude and rates", "Interface", "IMUs to both computers; 1 kHz, voting"),
    ("IF-07", "Gas pressure and temperature", "Interface", "Sensors to both computers; 500 Hz, dual dissimilar"),
    ("IF-08", "Suction plenum pressure", "Interface", "Sensors to vehicle dynamics controller; 200 Hz"),
    ("IF-09", "Mode request", "Interface", "HMI to mode manager; physical switch plus two-step confirm"),
    ("IF-10", "Crash signal", "Interface", "Airbag controller to both computers; hardwired plus bus"),
    ("IF-11", "Line isolation command", "Interface", "Thrust control unit to line valves; 20 ms, read-back"),
]

VERIFICATION = [  # id, covers, method, pass criterion, status
    ("VER-01", "TSR-01, TSR-03", "FMEDA; HIL fault injection; vehicle leak-down test", "SPFM >= 99%, LFM >= 90%, PMHF < 10 FIT; no gas flow after any single fault", "Analysis done"),
    ("VER-02", "TSR-02", "HIL test of every combination of arming inputs", "Arms only when all conditions hold", "Not started"),
    ("VER-03", "TSR-04, CC-01, CC-12", "Architecture review; penetration test", "No external route to a thrust command", "Not started"),
    ("VER-04", "TSR-05", "HIL sensor-fault injection", "Any single sensor fault detected", "Not started"),
    ("VER-05", "TSR-06", "Burst, cycling, fire, drop and impact tests", "Burst ratio >= 2.25; all tests passed", "Not started"),
    ("VER-06", "TSR-07", "Valve timing bench; crash test with charged tanks", "Valves closed <= 50 ms; no projectile; no net vent thrust", "Not started"),
    ("VER-07", "TSR-08", "Track test with controlled skirt leak; HIL", "Limits applied <= 100 ms; car stays on line", "Not started"),
    ("VER-08", "TSR-09", "Sim 3; HIL timing measurement", "<= 20 ms measured; FTTI >= 200 ms confirmed", "Simulated"),
    ("VER-09", "TSR-10", "Sim 4; track test with reduced fill", "No gas-starved landing", "Simulated"),
    ("VER-10", "TSR-11", "Sim 4; HIL", "Leak cases land safely", "Simulated"),
    ("VER-11", "TSR-12", "Sim 2; HIL", "Upright landing after a mid-roll fault", "Simulated"),
    ("VER-12", "TSR-13", "HIL sensor-fault injection", "Single IMU fault masked", "Not started"),
    ("VER-13", "TSR-14", "Sim 5; instrumented drop tests", "Peak <= 15 g from 5 m; no deployment below 1.5 m or on road", "Simulated"),
    ("VER-14", "TSR-15", "Sim 3, Sim 4; thrust stand", "Remaining lift >= 1.1 x weight", "Simulated"),
    ("VER-15", "TSR-16", "Diagnostic coverage analysis; HIL", "Coverage >= 99.9% for stuck-open and stuck-closed", "Analysis done"),
    ("VER-16", "TSR-17", "Sim 4; design study", ">= 50% roll-braking authority remains", "Gap found"),
    ("VER-17", "TSR-18", "Cold-soak and full-discharge tests of COPVs and valves", "No leak, crack or sticking at minimum temperature", "Not started"),
    ("VER-18", "TSR-19, CC-09", "Fill-station test", "Wet air refused", "Not started"),
    ("VER-19", "TSR-20", "Sim 3 sweep; HIL", "No bad outcomes at delays <= 50 ms", "Gap found"),
    ("VER-20", "TSR-02", "Track test with dummy targets in the clear zone", "Arming refused with a target in the zone", "Not started"),
    ("VER-21", "TSR-04, CC-02, CC-03, CC-06, CC-07, CC-08, CC-11", "Fuzzing, penetration test, code review (CG1-CG3)", "No successful attack at CAL 4 depth", "Not started"),
    ("VER-22", "TSR-21", "HIL injection of power, coil, switch and computer loss in Hop mode", "No master valve closes within 5 s of any single fault", "Analysis done"),
    ("VER-23", "TSR-22, CC-10", "HIL controller-loss injection; extended Sim 2", "Backup takes over <= 50 ms; upright landing <= 5 m/s", "Analysis done"),
    ("VER-24", "TSR-23", "HIL bus-loss injection", "No valve opens unintentionally; attitude held", "Analysis done"),
    ("VER-25", "CC-04, CC-05, CC-13", "Spoofing and replay attack on a test track; HIL with simulated satellite and beacon signals", "No arming with a spoofed fix or replayed beacon; monitor flags a zone mismatch within 1 s", "Not started"),
]

ASSUMPTIONS = [  # id, parameter, value, basis, replace with
    ("A-01", "Vehicle mass", "1,850 kg", "'4,000+ lb' quoted at the reveal (TechCrunch)", "Weighbridge data"),
    ("A-02", "Roll inertia", "600 kg m2", "Typical low sports car", "Inertia rig measurement"),
    ("A-03", "Gas storage volume", "600 L", "Disclosed by Tesla (L. Moravy)", "-"),
    ("A-04", "Gas mass", "250 kg reported; 244 kg modelled", "InsideEVs, single source", "Tesla specification"),
    ("A-05", "Fill pressure", "400 bar", "Derived: 250 kg in 600 L at 20 C with Z = 1.17", "COPV rating"),
    ("A-06", "Thruster count and layout", "10 nozzles; four lift groups of 9 kN at +/-0.35 and +/-0.85 m", "Count disclosed; layout assumed", "Nozzle layout and thrust-stand data"),
    ("A-07", "Thrust coefficient", "1.35", "Typical cold-gas nozzle with losses", "Thrust stand"),
    ("A-08", "Regulation", "40 bar feed; full thrust lost below 50 bar tank", "Assumed", "Regulator characterisation"),
    ("A-09", "Number of COPVs", "6 vessels in 3 groups", "'Every usable void' implies many vessels", "Design data"),
    ("A-10", "Control law", "PD with feed-forward, torque-first allocation", "Assumed", "Production control laws"),
    ("A-11", "Component failure rates", "10-300 FIT per part (see component FMEA)", "Representative magnitudes", "Supplier FMEDA data"),
    ("A-12", "Diagnostic coverage", "90-99%; pre-arm test 95% or 99.9%", "Assumed", "Diagnostic coverage analysis"),
    ("A-13", "Vehicle operating life", "10,000 h", "Typical automotive mission profile", "Programme mission profile"),
    ("A-14", "Common-cause shares", "beta = 1% (computers), 2% (master valves)", "Typical beta-factor range for diverse redundancy", "Dependent failure analysis with test data"),
    ("A-15", "Operating domain limits", "Wind < 8 m/s (gusts < 12), -10 to +40 C, dry paved surface", "Proposed by this study", "Validated limits"),
    ("A-16", "Landing system", "Suspension 140 kN/m, 0.20 m travel; airbag 2.6 m2, 0.5 m stroke, 1.8 bar relief", "Assumed", "Drop tests"),
]


DAMAGE = [  # id, damage scenario, impact category, safety goal link
    ("DS1", "Thrusters fire on a public road or near people", "Severe", "SG1"),
    ("DS2", "Loss of control during a hop", "Severe", "SG6"),
    ("DS3", "Thrust enabled outside an authorised zone", "Severe", "SG1, SG7"),
    ("DS4", "COPV over-pressure or rupture while filling", "Severe", "SG2"),
    ("DS5", "Fleet-wide unsafe or disabling software", "Severe", "SG1, SG6"),
    ("DS6", "Vehicle held to ransom; thrust unavailable", "Major", "-"),
    ("DS7", "Owner removes safety limits", "Severe", "SG1, SG6, SG7"),
    ("DS8", "Location and flight logs exposed", "Major", "-"),
]

TARA = [  # id, threat, damage, before factors (time, expertise, knowledge, window, equipment), after factors, controls, goal
    ("TS1", "Remote pivot from telematics to thrust command", "DS1", (4, 6, 3, 0, 4), (19, 8, 7, 0, 7), "CC-01, CC-02", "CG1"),
    ("TS2", "Diagnostic-port injection of mode and zone data", "DS1, DS3", (1, 3, 0, 1, 0), (4, 6, 3, 4, 4), "CC-01, CC-03", "CG1"),
    ("TS3", "Satellite spoofing plus beacon replay", "DS3", (1, 3, 0, 1, 4), (4, 6, 3, 4, 4), "CC-04, CC-05, CC-13", "CG2"),
    ("TS4", "Owner reflashes thrust software", "DS7", (1, 3, 0, 0, 4), (4, 8, 7, 0, 4), "CC-06, CC-07", "CG3"),
    ("TS5", "Malicious or tampered software update", "DS1, DS5", (4, 6, 7, 4, 0), (19, 8, 11, 10, 7), "CC-06, CC-08", "CG3"),
    ("TS6", "Spoofed fill station commands over-pressure", "DS4", (4, 3, 3, 1, 4), (19, 6, 7, 4, 7), "CC-09", "CG4"),
    ("TS7", "Bus jamming during a hop", "DS2", (0, 3, 0, 4, 0), (4, 6, 3, 4, 4), "CC-02, CC-10", "CG5"),
    ("TS8", "Theft of flight logs from the cloud", "DS8", (4, 6, 3, 0, 4), (4, 6, 7, 0, 4), "CC-11", "CG6"),
    ("TS9", "Ransomware through infotainment", "DS6", (4, 6, 3, 0, 4), (4, 6, 7, 0, 4), "CC-01, CC-12", "CG6"),
]

CYBER_GOALS = [  # id, cybersecurity goal, CAL, threats
    ("CG1", "No thrust command or mode change can enter the thrust domain from outside it", "CAL 4", "TS1, TS2"),
    ("CG2", "Zone authorisation cannot be faked by spoofing or replay", "CAL 4", "TS3"),
    ("CG3", "Only genuine, approved software runs in the thrust domain", "CAL 4", "TS4, TS5"),
    ("CG4", "No external party can command a fill above the rated pressure", "CAL 3", "TS6"),
    ("CG5", "Loss or jamming of thrust-domain communication never leads to loss of control", "CAL 3", "TS7"),
    ("CG6", "Personal data and non-safety functions are protected and segregated", "CAL 2", "TS8, TS9"),
]

CONTROLS = [  # id, control, goal, verification
    ("CC-01", "Zonal gateway with allowlist: only mode request, zone data and crash signal reach the thrust domain", "CG1, CG6", "VER-03"),
    ("CC-02", "Private thrust bus with message authentication, counters and timeouts", "CG1, CG5", "VER-21"),
    ("CC-03", "Diagnostic access needs an authenticated service tool and empty tanks", "CG1", "VER-21"),
    ("CC-04", "Signed challenge-response track beacon with distance bounding", "CG2", "VER-25"),
    ("CC-05", "Positioning plausibility: satellite fix checked against wheel odometry and inertial data", "CG2", "VER-25"),
    ("CC-06", "Secure boot with a hardware root of trust in both thrust computers", "CG3", "VER-21"),
    ("CC-07", "Tamper detection forces Road-safe mode and logs the event", "CG3", "VER-21"),
    ("CC-08", "Signed update packages, anti-rollback; thrust-domain updates only with tanks empty and the car present", "CG3", "VER-21"),
    ("CC-09", "Authenticated fill coupling; independent mechanical pressure relief", "CG4", "VER-18"),
    ("CC-10", "Communication loss in flight triggers the backup hop law (TSR-22)", "CG5", "VER-23"),
    ("CC-11", "Log encryption, data minimisation and retention limits", "CG6", "VER-21"),
    ("CC-12", "Domain segmentation: infotainment compromise cannot reach chassis or thrust", "CG6", "VER-03"),
    ("CC-13", "Safety monitor confirms the zone independently by inertial dead-reckoning from the last trusted beacon fix", "CG2", "VER-25"),
]

RISK = {"Severe": {"Very low": 2, "Low": 3, "Medium": 4, "High": 5},
        "Major": {"Very low": 1, "Low": 2, "Medium": 3, "High": 4}}


def feasibility(total):
    """ISO/SAE 21434 Annex G attack-potential mapping."""
    return "High" if total <= 13 else "Medium" if total <= 19 else "Low" if total <= 24 else "Very low"


def tara_rows():
    impact = {d[0]: d[2] for d in DAMAGE}
    rows = []
    for tid, name, ds, b, a, cc, cg in TARA:
        imp = impact[ds.split(",")[0].strip()]
        fb, fa = feasibility(sum(b)), feasibility(sum(a))
        rows.append([tid, name, ds, imp, "-".join(map(str, b)), sum(b), fb, RISK[imp][fb],
                     cc, cg, "-".join(map(str, a)), sum(a), fa, RISK[imp][fa]])
    return rows


def write_all(out=DATA):
    os.makedirs(out, exist_ok=True)
    tables = {
        "hazards": (["id", "hazardous_event", "situation", "S", "E", "C", "asil", "safety_goal"], HAZARDS),
        "safety_goals": (["id", "safety_goal", "asil", "safe_state", "ftti"], GOALS),
        "functional_safety_requirements": (["id", "requirement", "safety_goal", "asil"], FSR),
        "technical_safety_requirements": (["id", "requirement", "asil", "fsr", "allocated_to", "verification", "evidence"], TSR),
        "architecture_elements": (["id", "name", "type", "description"], ELEMENTS),
        "verification": (["id", "covers", "method", "pass_criterion", "status"], VERIFICATION),
        "assumptions": (["id", "parameter", "value", "basis", "replace_with"], ASSUMPTIONS),
        "damage_scenarios": (["id", "damage_scenario", "impact", "safety_goal"], DAMAGE),
        "tara": (["id", "threat", "damage", "impact", "before_factors", "before_points", "before_feasibility",
                  "before_risk", "controls", "cyber_goal", "after_factors", "after_points", "after_feasibility",
                  "after_risk"], tara_rows()),
        "cybersecurity_goals": (["id", "goal", "cal", "threats"], CYBER_GOALS),
        "cybersecurity_controls": (["id", "control", "cyber_goal", "verification"], CONTROLS),
    }
    for name, (head, rows) in tables.items():
        with open(os.path.join(out, f"{name}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(rows)
    return {k: len(v[1]) for k, v in tables.items()}


if __name__ == "__main__":
    print(write_all())
