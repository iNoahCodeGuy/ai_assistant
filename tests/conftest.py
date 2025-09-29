# Ensure project src directory is importable in tests
import sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
src = root / 'src'
if str(src) not in sys.path:
    sys.path.insert(0, str(src))
