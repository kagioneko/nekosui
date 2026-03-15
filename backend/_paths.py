"""neurostate-engine などの依存リポジトリをsys.pathに追加する"""

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).parent
_WORKSPACE = _BACKEND_DIR.parent.parent  # ai-lab/workspace/

_REPOS = [
    _WORKSPACE / "neurostate-engine",
    _WORKSPACE / "neurostate-sdk",
    _WORKSPACE / "bias-engine-mcp",
    _WORKSPACE / "memory-engine-mcp",
]

for _repo in _REPOS:
    _str = str(_repo)
    if _repo.exists() and _str not in sys.path:
        sys.path.insert(0, _str)
