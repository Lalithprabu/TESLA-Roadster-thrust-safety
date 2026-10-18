# 13. Safety case, regulation, review record and open issues

## 13.1 Safety case structure

![Safety case](figures/F10_safety_case_gsn.png)

*Figure 10. Safety case in goal structuring notation. The top claim (G0) is that the hop and boost functions are acceptably safe within the operating domain. Strategy S1 argues over each safety goal, SOTIF and cybersecurity.*

| Claim | Status | Evidence today | Evidence still needed |
| --- | --- | --- | --- |
| G1 SG1–SG3 are met | Supported at concept stage | FMEDA and cut sets (Sim 7): SPFM 100%, LFM 98.7%, PMHF 0.006 FIT | HIL fault injection; DFA with test data; steering item's own case (SG3) |
| G2 SG4–SG8 are met | Partly supported | Sims 2–5: recover-then-cut, reserve check, airbag loads | SG6 per-hop risk 3.3 × 10⁻⁷ against a 10⁻⁷ target; track tests |
| G3 SOTIF residual risk is at most 10⁻⁷ per hop | Not supported | Sim 4 bounds it at 1.4 × 10⁻³ per hop | Validated model and rare-event simulation campaign |
| G4 Residual cyber risk is 3 or below | Supported at concept stage | TARA with 13 controls | Penetration tests (VER-21, VER-25) |

## 13.2 Regulatory pathway

No regulation today covers a road car that fires thrusters or leaves the ground. The likely path is to keep the two worlds separate.

| Domain | Situation | Likely route |
| --- | --- | --- |
| Road type approval (US FMVSS, EU, UN) | No standard addresses thrusters, stored compressed air for propulsion or external airbags | Road-legal trims with thrust physically disabled in Road-safe mode; Rocket trim sold as not approved for public road use, as Tesla already states [B9] |
| Pressure vessels | Compressed-air propulsion vessels on cars have no dedicated rule | Qualify to the closest standards: UN GTR 13 and UN R134 (hydrogen vessels), UN R110 (CNG) and ISO 11119-3 (composite cylinders) |
| Aviation (FAA, EASA) | Whether a few-second hop counts as flight is unresolved | Operate only at closed sites under event or test permissions; seek early regulator engagement |
| Cybersecurity and updates | UN R155 and R156 apply to type-approved vehicles | Apply both to all trims |
| Track use | Track operators set their own rules | Site procedures, clear zones and marshals, written into the operating domain |

## 13.3 Independent review record

This issue was reviewed against the earlier issues and the public sources. Each finding below has been closed in this document.

| ID | Finding | Correction | Where |
| --- | --- | --- | --- |
| RV-01 | Fill pressure of 600 bar mixed up the 600 L volume with pressure | 400 bar adopted, consistent with the 250 kg gas figure | Ch. 5, A-05 |
| RV-02 | Burst energy over-stated at 90 MJ | Recalculated: about 60 MJ (about 14 kg TNT) | Ch. 5 |
| RV-03 | Launch gas use over-stated at 57–84 kg | Recalculated: 32–46 kg (0.9 s) and 46–67 kg (0.59 s) | Ch. 5 |
| RV-04 | Normally closed valves drop the car if power or a computer is lost mid-hop | TSR-21 to TSR-23 added; E/E architecture updated | Ch. 4, 7, 8 |
| RV-05 | Both channels trusted the same zone data, a common-mode attack path | Independent zone confirmation CC-13 and AD-09 added | Ch. 4, 10 |
| RV-06 | ASIL B for SG6 looked too low for a flight-like manoeuvre | Rationale written; FHA target 10⁻⁷ per hop added as a quantitative requirement | Ch. 6 |
| RV-07 | Coarse FMEDA (Sim 6) not at component level | Superseded by component-level cut-set FMEDA (Sim 7) | Ch. 8 |
| RV-08 | First PMHF result was implausibly small because common-cause faults were missing | β-factor common-cause events added | Ch. 8, A-14 |
| RV-09 | "SpaceX-built" overstated the sources | Changed to "developed with SpaceX" | Ch. 1, 2 |
| RV-10 | Single-source facts presented as confirmed | Each fact tagged with its source; unconfirmed items marked | Ch. 2, App. B |
| RV-11 | Requirements, trace and tables kept in several places could drift | One requirements database; document tables generated from it; automated two-way link check | Ch. 12 |

## 13.4 Open issues

| ID | Issue | Owner action | Blocks |
| --- | --- | --- | --- |
| OI-01 | SG6 per-hop risk 3.3 × 10⁻⁷ is above the 10⁻⁷ target | Individually controlled nozzles (TSR-17), better recovery planner (TSR-20) | Release |
| OI-02 | SOTIF residual risk not demonstrated | Validated 6-degree-of-freedom model and scenario campaign (ch. 9) | Release |
| OI-03 | Stuck-closed nozzle during the roll fails about one case in three | Design study for nozzle layout and roll authority | Release |
| OI-04 | Failure rates and β-factors are assumed | Supplier FMEDA data; DFA with test data | Safety case G1 |
| OI-05 | Cold-gas effects on valves and seals unknown | Full-discharge cold tests | Safety case G1 |
| OI-06 | Regulatory classification of a hop | Early engagement with road and aviation regulators | Market entry |
| OI-07 | No requirement stops thrust after touchdown (UCA-8) | Add a landing-detection requirement in the next issue | Next issue |
| OI-08 | A fall from 6 m gives 16.5 g even with external airbags, above the 15 g criterion; the operating domain allows a 6 m apex | Cut the apex limit to 5 m (14 g) or improve the landing system | Operating domain |
