#!/usr/bin/env python3
"""Mechanically verify that a phase is done, from evidence in the repository.

    check_phase_done.py <N> [--sub-project NAME] [--test-cmd CMD] [--root DIR]

Cycle 100 runs this before committing a phase. It checks what a machine can
observe; judgment calls stay with the team. Exit 0 = ready to commit, 1 = not.
Stdlib only, no third-party imports, so it runs anywhere the methodology does.
"""
import argparse, pathlib, re, shutil, subprocess, sys

def phase_section(plan_text, n):
    """Return (header_line, body) for '## Phase N:' or (None, None)."""
    m = re.search(rf"^## Phase {n}:.*$", plan_text, re.M)
    if not m: return None, None
    rest = plan_text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return m.group(0), rest[: nxt.start() if nxt else len(rest)]

def detect_test_cmd(root):
    if (root / "pyproject.toml").exists():
        return "poetry run pytest -q" if shutil.which("poetry") else "pytest -q"
    if (root / "package.json").exists(): return "npm test --silent"
    if (root / "Cargo.toml").exists(): return "cargo test -q"
    if (root / "go.mod").exists(): return "go test ./..."
    return None

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phase", type=int)
    ap.add_argument("--sub-project", default=None, help="sub-project directory name (multi-project repos)")
    ap.add_argument("--test-cmd", default=None, help="command that runs the test suite; auto-detected if omitted")
    ap.add_argument("--root", default=".", help="repository root")
    a = ap.parse_args()
    root = pathlib.Path(a.root).resolve()
    planning = root / "docs/planning" / (a.sub_project or "")
    phase_dir = planning / f"phase_{a.phase}"
    plan = planning / "PLAN.md"
    fails = []
    def check(ok, msg):
        print(("  ✓ " if ok else "  ✗ ") + msg)
        if not ok: fails.append(msg)

    print(f"Phase {a.phase} — {plan.relative_to(root) if plan.exists() else plan}")
    if not plan.exists():
        check(False, f"PLAN.md not found at {plan}"); return finish(fails, a.phase)
    text = plan.read_text(errors="replace")
    header, body = phase_section(text, a.phase)
    check(header is not None, f"'## Phase {a.phase}:' header found in PLAN.md")
    if header is None: return finish(fails, a.phase)
    check("✅ COMPLETE" in header, "phase header carries ✅ COMPLETE (cycle 090)")
    open_tasks = re.findall(r"^\s*- \[ \].*$", body, re.M)
    check(not open_tasks, f"no open task in the phase section ({len(open_tasks)} open task{'s' if len(open_tasks)!=1 else ''})")
    check(re.search(r"<!--\s*Spec:", body[:400]) is not None, "spec comment under the header (<!-- Spec: … --> or <!-- Spec: none — scaffolding -->)")

    dp = phase_dir / "DETAILED_PLAN.md"
    check(dp.exists(), f"{dp.relative_to(root)} exists")
    if dp.exists():
        unticked = re.findall(r"^\s*- \[ \].*$", dp.read_text(errors="replace"), re.M)
        check(not unticked, f"no unticked manual check in DETAILED_PLAN.md ({len(unticked)} unticked)")
    retro = phase_dir / "RETRO.md"
    check(retro.exists(), f"{retro.relative_to(root)} exists (cycle 095)")
    for req in [root / "README.md", root / "docs/DECISIONS.md", planning / "BACKLOG.md"]:
        check(req.exists(), f"{req.relative_to(root)} exists")

    cmd = a.test_cmd or detect_test_cmd(root)
    if cmd is None:
        check(False, "no test command detected — pass --test-cmd")
    else:
        r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
        check(r.returncode == 0, f"test suite passes: `{cmd}`" + ("" if r.returncode == 0 else f"\n{(r.stdout + r.stderr).strip()[-800:]}"))
    return finish(fails, a.phase)

def finish(fails, n):
    if fails:
        print(f"\nNOT READY — {len(fails)} check{'s' if len(fails)!=1 else ''} failed. Do not commit Phase {n}.")
        return 1
    print(f"\nReady to commit Phase {n}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
