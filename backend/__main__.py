import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
# 这样 'backend' 包就可以被导入
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import uvicorn

from backend.config import API_HOST, API_PORT
from backend.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info",
    )
