"""Static checks for the Windows scripts (they can't run on Linux)."""

import re
import unittest
from pathlib import Path

WINDOWS = Path(__file__).parent.parent / "windows"
BASE = "https://cnpartist.github.io/arminia-termine"


def script(name: str) -> str:
    return (WINDOWS / name).read_text(encoding="utf-8")


class WindowsScriptsTest(unittest.TestCase):
    def test_scripts_exist(self):
        names = sorted(p.name for p in WINDOWS.glob("*.ps1"))
        self.assertEqual(names, ["setup.ps1", "uninstall.ps1", "update.ps1"])

    def test_scripts_are_ascii(self):
        # Windows PowerShell 5.1 misreads UTF-8 files without BOM, and
        # `irm | iex` may decode with the wrong charset: stay plain ASCII.
        for path in WINDOWS.glob("*.ps1"):
            path.read_bytes().decode("ascii")

    def test_published_urls(self):
        self.assertIn(f"'{BASE}/termine.png'", script("update.ps1"))
        self.assertIn(f"'{BASE}'", script("setup.ps1"))

    def test_setup_and_uninstall_use_the_same_task_name(self):
        name = re.compile(r"\$TaskName\s*=\s*'([^']+)'")
        self.assertEqual(name.search(script("setup.ps1")).group(1),
                         name.search(script("uninstall.ps1")).group(1))

    def test_iex_scripts_never_exit_the_users_shell(self):
        for name in ("setup.ps1", "uninstall.ps1"):
            self.assertIsNone(re.search(r"^\s*exit\b", script(name), re.M), name)

    def test_task_runs_hidden(self):
        self.assertIn("conhost.exe", script("setup.ps1"))
        self.assertIn("--headless", script("setup.ps1"))


if __name__ == "__main__":
    unittest.main()
