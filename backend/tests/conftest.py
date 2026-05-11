import sys
from pathlib import Path

# Добавить backend в path для импортов
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path.parent))
