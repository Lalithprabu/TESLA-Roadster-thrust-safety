# 10. Cybersecurity concept

A thrust system is a cybersecurity problem with physical consequences: a successful attack on it can fire jets on a public road. The analysis follows ISO/SAE 21434 and is designed to support a UN R155 type approval and a UN R156 software-update management system.

## 10.1 Assets

| ID | Asset | Property to protect |
| --- | --- | --- |
| A1 | Thrust commands and valve states | Integrity, availability in flight |
| A2 | Mode and arming state | Integrity |
| A3 | Zone authorisation (satellite fix, beacon) | Integrity, authenticity |
| A4 | Thrust-domain software and calibration | Integrity, authenticity |
| A5 | Cryptographic keys | Confidentiality, integrity |
| A6 | Gas state and fill commands | Integrity |
| A7 | Flight and location logs | Confidentiality |
| A8 | Update packages | Integrity, authenticity |
| A9 | Diagnostic and service access | Integrity, access control |

## 10.2 Security architecture

![Security zones](figures/F08_security_zones.png)

*Figure 7. Security zones: the thrust domain is isolated behind a zonal gateway that passes only three signal types; connectivity and infotainment have no path to it.*

## 10.3 Damage scenarios

{{table:damage}}

## 10.4 Threat analysis and risk assessment

Attack feasibility uses the attack-potential method of ISO/SAE 21434 Annex G. Five factors are scored: elapsed time, specialist expertise, knowledge of the item, window of opportunity and equipment. A total of 0–13 points is High feasibility, 14–19 Medium, 20–24 Low and 25 or more Very low. Risk value (1–5) comes from impact and feasibility. Residual risk above 3 is not accepted, and the traceability check enforces this rule.

{{table:tara}}

![Attack tree](figures/F09_attack_tree.png)

*Figure 8. Attack tree for "thrusters fire on a public road". A faked track zone is the one path that defeats both channels at once, because both trust the same zone data; the independent zone check (CC-13) closes it.*

## 10.5 Cybersecurity goals

{{table:cyber_goals}}

## 10.6 Cybersecurity controls

{{table:controls}}

## 10.7 Operations and post-development

| Activity | Practice | Regulation |
| --- | --- | --- |
| Cybersecurity management system | Organisation-level processes, roles and audits | UN R155 |
| Software update management | Signed updates; thrust domain updated only with tanks empty and the car present; version records per vehicle | UN R156 |
| Vulnerability monitoring | Supplier bulletins, bug bounty, fleet security monitoring | ISO/SAE 21434 cl. 8 |
| Incident response | Fleet-wide remote lockout of thrust functions (to Road-safe only, never to enable) | ISO/SAE 21434 cl. 13 |
| End of cybersecurity support | Thrust functions disabled when support ends | ISO/SAE 21434 cl. 14 |

The remote lockout can only *disable* thrust. No remote command can enable it, which keeps the incident-response path from becoming an attack path.
