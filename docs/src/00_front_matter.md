# Roadster Thrust System: System, Safety and Security Concept

**Document RTS-SSC-001 · Issue 3.0 · 18 October 2026 · Concept phase**

An independent systems-engineering, functional-safety (ISO 26262), SOTIF (ISO 21448) and cybersecurity (ISO/SAE 21434) concept study of a cold-gas-thruster "hop" function on a road sports car, inspired by the Tesla Roadster reveal of 15 October 2026.

> **Disclaimer.** Independent educational analysis. Not affiliated with, endorsed by or reviewed by Tesla, Inc. or SpaceX. Tesla's design is not public: every architecture, part, failure rate and number in this document is an assumption or an estimate derived from public reporting, registered in Appendix A. Nothing here describes the real vehicle, and nothing here is certification evidence. Tesla, Roadster and SpaceX are trademarks of their owners.

## Document control

| Field | Value |
| --- | --- |
| Document | RTS-SSC-001, System, Safety and Security Concept |
| Issue | 3.0 (consolidated and independently reviewed) |
| Status | Concept phase; public release |
| Author | Lalith Prabu |
| Prepared with | AI assistance (Claude by Anthropic); author review before release |
| Data sources of truth | `data/*.csv` (requirements and traceability), `results/` (simulation outputs) |
| Licence | Text, figures and tables CC BY 4.0; code MIT |

## Revision history

| Issue | Date | Change |
| --- | --- | --- |
| 3.0 | 18 Oct 2026 | Consolidated single document set. Added architecture decision record, assumptions register, requirements database with automated link check, independent review record. Updated E/E architecture for fail-operational hop control (TSR-21 to TSR-23). |
| 2.1 | 17 Oct 2026 | Representative component FMEA and FMEDA, traceability chain, factor-scored TARA and attack tree. |
| 2.0 | 16 Oct 2026 | Industry structure: operating domain, functional and E/E architecture, timing budget, ASIL decomposition, DFA, SOTIF acceptance, cybersecurity and V&V. Corrected fill pressure 600 to 400 bar. |
| 1.0 | 16 Oct 2026 | First architecture and safety analysis. |

## How this document maps to the standards

| Chapter | Work product | Standard reference |
| --- | --- | --- |
| 1 | Executive summary | — |
| 2 | Decoded feature and public facts | — |
| 3 | Item definition, concept of operations, operating domain | ISO 26262-3 cl. 5; ISO 21448 cl. 5 |
| 4 | System architecture: logical, functional, E/E, interfaces, modes, timing, design decisions | ISO 26262-4 cl. 6 |
| 5 | Performance and energy budget | — |
| 6 | Hazard analysis and risk assessment, safety goals | ISO 26262-3 cl. 6 |
| 7 | Functional and technical safety concept | ISO 26262-3 cl. 7; ISO 26262-4 cl. 6 |
| 8 | Safety analyses: FMEA, FMEDA, FTA, DFA, STPA | ISO 26262-5 cl. 8–9; ISO 26262-9 cl. 7–8 |
| 9 | SOTIF analysis | ISO 21448 cl. 6–7 |
| 10 | Cybersecurity concept and TARA | ISO/SAE 21434 cl. 9, 15, Annex G |
| 11 | Verification and validation plan | ISO 26262-4 cl. 7–8; ISO 21448 cl. 9–11 |
| 12 | Traceability | ISO 26262-8 cl. 6 |
| 13 | Safety case, regulation, review record, open issues | ISO 26262-2 cl. 6 |
| 14 | Simulation report | Supporting evidence |
| A–B | Assumptions register, sources | — |

## Terms and abbreviations

| Term | Meaning |
| --- | --- |
| ASIL | Automotive safety integrity level, A (lowest) to D (highest); B(D) means ASIL B after decomposition of a D goal |
| CAL | Cybersecurity assurance level (ISO/SAE 21434), 1 to 4 |
| COPV | Carbon-fibre overwrapped pressure vessel |
| DC | Diagnostic coverage |
| DFA | Dependent failure analysis |
| FHA | Functional hazard assessment (aviation, ARP4761A) |
| FIT | Failures in time: one failure per 10⁹ hours |
| FSR, TSR | Functional and technical safety requirement |
| FTTI | Fault tolerant time interval: time from fault to hazard if nothing reacts |
| HIL | Hardware-in-the-loop testing |
| SPFM, LFM, PMHF | Single-point fault metric, latent fault metric, probabilistic metric for hardware failures |
| SOTIF | Safety of the intended functionality: hazards with nothing broken |
| STPA | System-theoretic process analysis |
| TARA | Threat analysis and risk assessment |
| TCU | Thrust control unit (the command-channel computer) |
