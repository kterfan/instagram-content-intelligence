"""Verify the built wheel independently of the repository import path."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
wheel = sorted((ROOT / "dist").glob("*.whl"), key=lambda path: path.stat().st_mtime)[-1]
with tempfile.TemporaryDirectory() as folder:
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", "--target", folder, str(wheel)], check=True)
    code = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from instagram_content_intelligence.visual import render_rtl_html
from instagram_content_intelligence.cli import build_parser
target = render_rtl_html('فارسی', 'متن مستقل از ریپو', Path(sys.argv[1]) / 'check.html')
assert '@font-face' in target.read_text(encoding='utf-8')
assert 'workflow' in build_parser().format_help()
print('Wheel imports and bundled font render correctly outside the repository.')
"""
    subprocess.run([sys.executable, "-I", "-c", code, folder], cwd=folder, check=True)
