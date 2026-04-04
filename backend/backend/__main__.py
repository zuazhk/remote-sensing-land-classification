import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
import uvicorn

host = os.getenv("API_HOST", "0.0.0.0")
port = int(os.getenv("API_PORT", "8000"))

from backend.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )
