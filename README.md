# Roadster Thrust System: System, Safety and Security Concept

An open, independent concept study of the cold-gas thruster "hop" function revealed on the Tesla Roadster on 15 October 2026. It works the system end to end, the way an automotive programme would: architecture, hazard analysis, functional safety (ISO 26262), SOTIF (ISO 21448), cybersecurity (ISO/SAE 21434), verification and validation, and traceability between all of them. Seven runnable simulations back the analysis.

> **Not affiliated with Tesla or SpaceX.** Tesla has not published the design. Every architecture choice, part, rate and number here is an assumption registered in Appendix A of the document. See [DISCLAIMER.md](DISCLAIMER.md).

## Start here

| You want | Open |
| --- | --- |
| The full document (47 pages) | [`docs/RTS-SSC-001.pdf`](docs/RTS-SSC-001.pdf), or [`docs/RTS-SSC-001.md`](docs/RTS-SSC-001.md) to read on GitHub |
| The system architecture | Chapter 4: logical, functional, E/E, interfaces, modes, timing budget, architecture decision record |
| To watch the hop and its failures | [`viewer/index.html`](viewer/index.html), opens in any browser, no install |
| The requirements and trace data | [`data/`](data/) (CSV, generated from [`tools/requirements_db.py`](tools/requirements_db.py)) |
| To rerun everything | See "Reproduce" below |

## Key findings

1. **It is a hop, not a flight.** About 244 kg of air at about 400 bar holds a 1,850 kg car in a hover for 6.7 s; one reference hop uses 55% of it.
2. **"Cut all gas" is the wrong safe state in the air.** After a stuck-open valve mid-roll, cutting gas lands the car on its roof; isolating the failed line and recovering lands it upright (Sim 2).
3. **The fault tolerant time interval is about 200 ms;** detection and isolation are budgeted at 20 ms (Sim 3).
4. **Valves that close on power loss are safe on the ground and fatal in the air.** Hop control has to be fail-operational (TSR-21 to TSR-23).
5. **SG1 (no unintended thrust) meets ASIL D hardware metrics** with representative rates: SPFM 100%, LFM 98.7%, PMHF 0.006 FIT. Common-cause faults dominate what is left (Sim 7).
6. **A faked track zone is the one attack that defeats both channels at once;** an independent zone check in the safety monitor closes it.
7. **Not yet releasable:** per-hop risk from faults is 3.3 × 10⁻⁷ against a 10⁻⁷ target, and SOTIF residual risk is bounded only at 1.4 × 10⁻³ per hop.

## Repository layout

```
docs/
  RTS-SSC-001.pdf / .md / .html   the consolidated document (generated)
  src/                            chapter sources with {{table:...}} placeholders
  figures/                        architecture, analysis and simulation figures
data/                             requirements, hazards, TARA, verification (generated CSV)
tools/
  requirements_db.py              single source of truth for every ID and link
  check_traceability.py           checks every safety and security link in both directions
  build_docs.py                   fills tables from data and renders MD, HTML and PDF
  figure_roadmap.py               draws the V&V roadmap figure
sim/                              Sims 1-7, shared model, viewer template, run_all.py
results/                          simulation outputs: charts, JSON, component FMEA, cut sets
viewer/index.html                 animated fault viewer (generated)
```

## Traceability

```
Hazardous event -> Safety goal -> FSR -> TSR -> Architecture element -> Verification item -> Evidence
Damage scenario -> Threat -> Cybersecurity goal -> Control -> Verification item
```

11 hazardous events, 8 safety goals, 14 FSRs, 23 TSRs, 22 architecture elements and interfaces, 8 damage scenarios, 9 threats, 6 cybersecurity goals, 13 controls and 25 verification items. Every table in the document is generated from `tools/requirements_db.py`, and the build stops if `check_traceability.py` finds a broken link.

## Reproduce

```bash
pip install -r requirements.txt
python sim/run_all.py           # about 1 minute: results/ and viewer/
python tools/check_traceability.py
python tools/build_docs.py      # docs/RTS-SSC-001.md, .html and .pdf
```

The PDF step uses Playwright with Chromium (`pip install playwright && playwright install chromium`). Use `python tools/build_docs.py --no-pdf` to build Markdown and HTML only.

## Contributing

Challenges are welcome, especially better failure rates, real component data, and errors in the analysis. Open an issue that names the chapter and the ID (for example TSR-17 or A-05). If you change an assumption, rerun the three commands above so every table and figure stays consistent.

## Licence

Code: MIT ([LICENSE](LICENSE)). Documents, figures and data: CC BY 4.0 ([LICENSE-docs.md](LICENSE-docs.md)).

Author: Lalith Prabu. Prepared with AI assistance (Claude by Anthropic) and reviewed by the author before release.
