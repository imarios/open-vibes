"""Tests for check_phase_done.py. Run: python3 scripts/test_check_phase_done.py"""
import os, subprocess, sys, tempfile, textwrap, unittest, pathlib
HERE = pathlib.Path(__file__).parent
SCRIPT = HERE / "check_phase_done.py"

def make_project(root, *, open_task=False, spec=True, unticked_dod=False, complete=True, retro=True):
    root = pathlib.Path(root)
    (root / "docs/planning/phase_2").mkdir(parents=True)
    (root / "README.md").write_text("# demo\n")
    (root / "docs/DECISIONS.md").write_text("# Decisions\n")
    (root / "docs/planning/BACKLOG.md").write_text("# Backlog\n")
    hdr = "## Phase 2: Lexer" + (" ✅ COMPLETE" if complete else "")
    spec_line = "<!-- Spec: lang.md R1-R3 -->\n" if spec else ""
    lines = ["# Demo", "", "Project-Type: production", "",
             "## Phase 1: Skeleton ✅ COMPLETE", "<!-- Spec: none — scaffolding -->", "- [x] scaffold", "",
             hdr] + ([spec_line.strip()] if spec else []) + [
             "- [x] tokenize", f"- [{' ' if open_task else 'x'}] error lines", "",
             "## Phase 3: Parser", "- [ ] later", ""]
    (root / "docs/planning/PLAN.md").write_text("\n".join(lines))
    (root / "docs/planning/phase_2/DETAILED_PLAN.md").write_text(
        "# Phase 2\n\n## Phase-specific DoD\n\n- [%s] Code only\n" % (" " if unticked_dod else "x"))
    if retro:
        (root / "docs/planning/phase_2/RETRO.md").write_text("# Phase 2 — Retrospective\n")

def run(root, *args):
    p = subprocess.run([sys.executable, str(SCRIPT), "2", "--root", str(root), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

class CheckPhaseDone(unittest.TestCase):
    def test_complete_phase_passes(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d); code, out = run(d, "--test-cmd", "true")
            self.assertEqual(code, 0, out); self.assertIn("ready", out.lower())
    def test_open_task_in_phase_section_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d, open_task=True); code, out = run(d, "--test-cmd", "true")
            self.assertEqual(code, 1); self.assertIn("open task", out.lower())
    def test_open_task_in_other_phase_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d); code, out = run(d, "--test-cmd", "true")
            self.assertEqual(code, 0, out)   # Phase 3's "- [ ] later" must not count
    def test_missing_spec_comment_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d, spec=False); code, out = run(d, "--test-cmd", "true")
            self.assertEqual(code, 1); self.assertIn("spec", out.lower())
    def test_unticked_manual_check_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d, unticked_dod=True); code, out = run(d, "--test-cmd", "true")
            self.assertEqual(code, 1); self.assertIn("detailed_plan", out.lower())
    def test_missing_retro_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d, retro=False); code, out = run(d, "--test-cmd", "true")
            self.assertEqual(code, 1); self.assertIn("retro", out.lower())
    def test_header_without_complete_marker_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d, complete=False); code, out = run(d, "--test-cmd", "true")
            self.assertEqual(code, 1); self.assertIn("complete", out.lower())
    def test_failing_test_command_fails(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d); code, out = run(d, "--test-cmd", "false")
            self.assertEqual(code, 1); self.assertIn("test", out.lower())
    def test_no_detectable_test_command_fails_loudly(self):
        with tempfile.TemporaryDirectory() as d:
            make_project(d); code, out = run(d)
            self.assertEqual(code, 1); self.assertIn("--test-cmd", out)

if __name__ == "__main__":
    unittest.main(verbosity=1)
