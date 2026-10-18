"""Build the consolidated document RTS-SSC-001 from docs/src/*.md and data/*.csv.

Steps
  1. Regenerate data/*.csv from the requirements database and run the traceability check.
  2. Copy simulation charts from results/ into docs/figures/ and draw the roadmap figure.
  3. Replace every {{table:...}} placeholder with a table generated from the data, so the
     document can never disagree with the data.
  4. Write docs/RTS-SSC-001.md (GitHub-readable), docs/RTS-SSC-001.html and docs/RTS-SSC-001.pdf.

Usage:  python tools/build_docs.py            (PDF needs: pip install playwright markdown)
        python tools/build_docs.py --no-pdf   (Markdown and HTML only)
"""
import csv
import glob
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA, DOCS, RESULTS = (os.path.join(ROOT, d) for d in ("data", "docs", "results"))
SRC, FIG = os.path.join(DOCS, "src"), os.path.join(DOCS, "figures")
DOC_ID = "RTS-SSC-001"
ISSUE = "Issue 3.0 · 18 October 2026"

sys.path.insert(0, HERE)
import requirements_db  # noqa: E402
import figure_roadmap  # noqa: E402


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def d(name):
    return load(os.path.join(DATA, f"{name}.csv"))


def cell(x):
    x = str(x).replace(">=", "≥").replace("<=", "≤").replace("|", "\\|").replace("\n", " ")
    return x.strip() or "—"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def ids(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def build_tables():
    hz, sg, fsr, tsr = d("hazards"), d("safety_goals"), d("functional_safety_requirements"), d("technical_safety_requirements")
    el, ver, asm = d("architecture_elements"), d("verification"), d("assumptions")
    ds, ts, cg, cc = d("damage_scenarios"), d("tara"), d("cybersecurity_goals"), d("cybersecurity_controls")
    fmea = load(os.path.join(RESULTS, "component_fmea.csv"))
    status = {v["id"]: v["status"] for v in ver}
    fsr_goal = {f["id"]: f["safety_goal"] for f in fsr}
    goal_hz = {}
    for h in hz:
        goal_hz.setdefault(h["safety_goal"], []).append(h["id"])

    def alloc(eid):
        return ", ".join(t["id"] for t in tsr if eid in ids(t["allocated_to"]))

    T = {}
    T["subsystems"] = table(["ID", "Subsystem", "Content", "Technical safety requirements allocated"],
                            [[e["id"], e["name"], e["description"], alloc(e["id"])]
                             for e in el if e["type"] == "Subsystem"])
    T["hazards"] = table(["ID", "Hazardous event", "Situation", "S", "E", "C", "ASIL", "Goal"],
                         [[h["id"], h["hazardous_event"], h["situation"], h["S"], h["E"], h["C"], h["asil"], h["safety_goal"]] for h in hz])
    T["goals"] = table(["ID", "Safety goal", "ASIL", "Safe state", "FTTI", "From"],
                       [[g["id"], g["safety_goal"], g["asil"], g["safe_state"], g["ftti"], ", ".join(goal_hz.get(g["id"], []))] for g in sg])
    T["fsr"] = table(["ID", "Functional safety requirement", "Goal", "ASIL"],
                     [[f["id"], f["requirement"], f["safety_goal"], f["asil"]] for f in fsr])
    T["tsr"] = table(["ID", "Technical safety requirement", "ASIL", "From", "Allocated to", "Verified by"],
                     [[t["id"], t["requirement"], t["asil"], t["fsr"], t["allocated_to"], t["verification"]] for t in tsr])
    T["component_fmea"] = table(["Component", "Failure mode", "Effect", "S", "O", "D", "AP", "Goal", "Field diagnostic", "DC %"],
                                [[r["component"], r["mode"], r["effect"], r["S"], r["O"], r["D"], r["AP"], r["goal"],
                                  r["field_diagnostic"], r["DC_pct"]] for r in fmea])
    T["damage"] = table(["ID", "Damage scenario", "Impact", "Linked safety goal"],
                        [[x["id"], x["damage_scenario"], x["impact"], x["safety_goal"]] for x in ds])
    T["tara"] = table(["ID", "Threat scenario", "Damage", "Impact", "Factors before", "Feasibility before", "Risk before",
                       "Controls", "Factors after", "Feasibility after", "Risk after"],
                      [[t["id"], t["threat"], t["damage"], t["impact"], f'{t["before_factors"]} = {t["before_points"]}',
                        t["before_feasibility"], t["before_risk"], t["controls"],
                        f'{t["after_factors"]} = {t["after_points"]}', t["after_feasibility"], t["after_risk"]] for t in ts])
    T["cyber_goals"] = table(["ID", "Cybersecurity goal", "CAL", "Threats"],
                             [[g["id"], g["goal"], g["cal"], g["threats"]] for g in cg])
    T["controls"] = table(["ID", "Control", "Goal", "Verified by"],
                          [[c["id"], c["control"], c["cyber_goal"], c["verification"]] for c in cc])
    T["verification"] = table(["ID", "Covers", "Method", "Pass criterion", "Status"],
                              [[v["id"], v["covers"], v["method"], v["pass_criterion"], v["status"]] for v in ver])
    trace = []
    for t in tsr:
        goals = sorted({fsr_goal[f] for f in ids(t["fsr"])}, key=lambda g: int(g[2:]))
        hzs = [h for g in goals for h in goal_hz.get(g, [])]
        trace.append([t["id"], ", ".join(hzs), ", ".join(goals), t["fsr"], t["allocated_to"], t["verification"],
                      "; ".join(sorted({status[v] for v in ids(t["verification"])}))])
    T["trace"] = table(["TSR", "Hazards", "Goals", "FSR", "Elements", "Verification", "Status"], trace)
    sec = []
    for t in ts:
        vers = sorted({c["verification"] for c in cc if c["id"] in ids(t["controls"])})
        cal = next(g["cal"] for g in cg if g["id"] == t["cyber_goal"])
        sec.append([t["damage"], t["id"], f'{t["cyber_goal"]} ({cal})', t["controls"], ", ".join(vers),
                    f'{t["before_risk"]} → {t["after_risk"]}'])
    T["security_trace"] = table(["Damage", "Threat", "Goal", "Controls", "Verification", "Risk"], sec)
    T["assumptions"] = table(["ID", "Parameter", "Value", "Basis", "Replace with"],
                             [[a["id"], a["parameter"], a["value"], a["basis"], a["replace_with"]] for a in asm])
    return T


def run_check():
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_traceability.py")], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("traceability check failed, document not built:\n" + r.stdout + r.stderr)
    return r.stdout.strip()


def assemble(tables, check):
    parts = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        with open(path, encoding="utf-8") as f:
            parts.append(f.read().strip())
    text = "\n\n".join(parts) + "\n"
    text = text.replace("{{check_output}}", "```\n" + check + "\n```")
    text = re.sub(r"\{\{table:([a-z_]+)\}\}", lambda m: tables[m.group(1)], text)
    left = re.findall(r"\{\{[^}]*\}\}", text)
    if left:
        sys.exit(f"unresolved placeholders: {left}")
    for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if not os.path.exists(os.path.join(DOCS, img)):
            sys.exit(f"missing figure: {img}")
    return text


CSS = """
@page { size: A4; margin: 20mm 16mm 18mm 16mm; }
html { font-family: Inter, 'DejaVu Sans', sans-serif; font-size: 9.6pt; color: #1b1b1a; line-height: 1.45; }
body { margin: 0; }
h1 { font-size: 17pt; margin: 0 0 8pt; padding-top: 2pt; break-before: page; color: #0b0b0b; letter-spacing: -0.01em; }
h1:first-of-type { break-before: avoid; font-size: 22pt; margin-top: 30mm; }
h2 { font-size: 12pt; margin: 16pt 0 5pt; color: #0b0b0b; break-after: avoid; }
h3 { font-size: 10.5pt; margin: 12pt 0 4pt; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 8pt; line-height: 1.3; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: #f0efeb; text-align: left; font-weight: 600; }
th, td { border: 0.6pt solid #d6d4cd; padding: 3pt 4pt; vertical-align: top; }
td:first-child { white-space: nowrap; }
.toc-list, ul { padding-left: 14pt; }
img { max-width: 100%; display: block; margin: 8pt auto 2pt; break-inside: avoid; }
p:has(> img) { break-inside: avoid; break-after: avoid; margin: 0; }
em { color: #52514e; }
blockquote { margin: 10pt 0; padding: 6pt 10pt; border-left: 3pt solid #eb6834; background: #fdf3ee; }
code, pre { font-family: 'DejaVu Sans Mono', monospace; font-size: 8pt; }
pre { background: #f5f4f0; padding: 6pt 8pt; border-radius: 3pt; white-space: pre-wrap; }
a { color: #2a78d6; text-decoration: none; }
.toc { columns: 1; }
.toc li { margin: 1pt 0; }
"""


def to_html(text):
    import markdown
    # table of contents of the chapters, inserted after the front matter
    heads = re.findall(r"^# (.+)$", text, flags=re.M)[1:]
    toc = '<h2 style="break-before: page">Contents</h2>\n\n' + "\n".join("- " + re.sub(r"^(\d+)\.", r"\1\\.", h) for h in heads) + "\n\n"
    first_h1_after_front = text.index("\n# ", text.index("## Terms and abbreviations"))
    text = text[:first_h1_after_front] + "\n\n" + toc + text[first_h1_after_front:]
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{DOC_ID} Roadster Thrust System"
            f"</title><style>{CSS}</style></head><body>{body}</body></html>")


def to_pdf(html_path, pdf_path):
    from playwright.sync_api import sync_playwright
    head = (f"<div style='font-family:Inter,sans-serif;font-size:7.5pt;color:#7a7974;width:100%;padding:0 16mm;"
            f"display:flex;justify-content:space-between'><span>{DOC_ID} · Roadster Thrust System: System, Safety "
            f"and Security Concept</span><span>{ISSUE}</span></div>")
    foot = ("<div style='font-family:Inter,sans-serif;font-size:7.5pt;color:#7a7974;width:100%;padding:0 16mm;"
            "display:flex;justify-content:space-between'><span>Independent educational analysis · not affiliated "
            "with Tesla or SpaceX · CC BY 4.0</span><span>Page <span class='pageNumber'></span> of "
            "<span class='totalPages'></span></span></div>")
    with sync_playwright() as p:
        exe = "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") and os.path.isfile("/opt/pw-browsers/chromium") else None
        browser = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        page = browser.new_page()
        page.goto("file://" + html_path, wait_until="networkidle")
        kw = dict(path=pdf_path, format="A4", print_background=True, display_header_footer=True,
                  header_template=head, footer_template=foot,
                  margin=dict(top="20mm", bottom="18mm", left="16mm", right="16mm"))
        try:
            page.pdf(outline=True, tagged=True, **kw)
        except TypeError:          # older Playwright without outline support
            page.pdf(**kw)
        browser.close()


def main():
    print(requirements_db.write_all())
    check = run_check()
    print(check)
    for f in glob.glob(os.path.join(RESULTS, "fig*.png")):
        shutil.copy(f, FIG)
    figure_roadmap.main()
    text = assemble(build_tables(), check)
    md_path, html_path, pdf_path = (os.path.join(DOCS, f"{DOC_ID}.{e}") for e in ("md", "html", "pdf"))
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(to_html(text))
    print("wrote", os.path.relpath(md_path, ROOT), "and", os.path.relpath(html_path, ROOT))
    if "--no-pdf" not in sys.argv:
        to_pdf(html_path, pdf_path)
        print("wrote", os.path.relpath(pdf_path, ROOT))


if __name__ == "__main__":
    main()
