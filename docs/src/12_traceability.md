# 12. Traceability

Traceability proves that every hazard is covered by a goal, every goal by requirements, every requirement by an architecture element and a test, and every test by a requirement. Two chains are traced.

- **Safety:** hazardous event → safety goal → functional safety requirement → technical safety requirement → architecture element → verification item → evidence.
- **Security:** damage scenario → threat scenario → cybersecurity goal → control → verification item.

All links live in one place, the requirements database (`tools/requirements_db.py`, written out to `data/*.csv`). The tables in this document are generated from it, so the document and the data cannot drift apart. `tools/check_traceability.py` checks every link in both directions and fails the build if any link is broken.

## 12.1 Safety trace matrix

{{table:trace}}

## 12.2 Security trace matrix

{{table:security_trace}}

## 12.3 Automated check

The output below was produced by the build that made this document.

{{check_output}}

**Rules the check enforces.**

1. Every hazardous event names a safety goal that exists, and every safety goal has at least one hazardous event.
2. Every safety goal has at least one functional safety requirement.
3. Every functional safety requirement is refined by a technical safety requirement, or is explicitly allocated to another item (FSR-3.1, steering).
4. Every technical safety requirement is allocated to an architecture element that exists, and names a verification item that exists and lists it back.
5. Every threat scenario names damage scenarios, a cybersecurity goal and controls that exist, and has residual risk 3 or below.
6. Every cybersecurity goal has a threat and a control; every control treats a threat and names a verification item that lists it back.
7. Every verification item covers only requirements or controls that exist.
