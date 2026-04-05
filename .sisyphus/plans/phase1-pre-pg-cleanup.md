# Phase 1: PG 前置清理（查漏补缺）

> **阶段定位**: 在引入 PostgreSQL 数据库、用户鉴权等新功能之前，对现有代码库进行阶段性整理。
> **完成后**: 进入第二阶段 - PG 数据库集成、鉴权系统开发。

---

## 目标

1. 补齐后端测试基础设施（pytest 配置 + 覆盖率）
2. 引入前端测试（Vitest）
3. 搭建 CI 工作流（GitHub Actions）
4. 验证容器化部署流程一致性
5. 更新文档反映当前状态

---

## Task 1: 后端测试基础设施完善

### 1.1 添加 pytest 配置

**文件**: `backend/pyproject.toml`（新增 `[tool.pytest.ini_options]` 段）

```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
timeout = 60
addopts = "-v --tb=short"
```

**验证**: `cd backend && uv run pytest` 能正常发现并运行现有 3 个测试文件

### 1.2 添加覆盖率报告

**操作**: 在 `pyproject.toml` 的 dependencies 中添加 `pytest-cov`

```toml
"pytest-cov>=6.0.0",
```

**配置**: 在 `[tool.pytest.ini_options]` 中添加：
```toml
addopts = "-v --tb=short --cov=backend --cov-report=term-missing --cov-report=html"
```

**验证**: `cd backend && uv run pytest --cov` 生成覆盖率报告

### 1.3 补充关键测试用例（优先级从高到低）

| 优先级 | 测试文件 | 覆盖内容 |
|--------|----------|----------|
| P0 | `test_predict.py` | POST `/api/v1/predict` 单图预测 |
| P0 | `test_train.py` | 训练 CLI 核心逻辑（早停、warmup、历史保存） |
| P1 | `test_visualization.py` | 可视化端点（混淆矩阵、ROC、训练历史） |
| P1 | `test_batch.py` | 批量预测端点 |
| P2 | `test_evaluation.py` | 模型评估端点 |

---

## Task 2: 前端测试（Vitest）

### 2.1 安装 Vitest

**操作**: 确认 `vite-plus` 的 `vp test` 命令是否已内置 Vitest 支持。

**检查步骤**:
```bash
cd frontend && npm ls vitest
```

**如果未安装**:
```bash
cd frontend && npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

### 2.2 配置 Vitest

**文件**: 创建 `frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
})
```

**文件**: 创建 `frontend/src/test/setup.ts`

```typescript
import '@testing-library/jest-dom'
```

### 2.3 编写测试用例（优先级从高到低）

| 优先级 | 测试文件 | 测试内容 |
|--------|----------|----------|
| P0 | `src/components/ui/Button.test.tsx` | 渲染、variants、asChild、点击事件 |
| P0 | `src/components/ui/Card.test.tsx` | 渲染、子组件组合 |
| P1 | `src/pages/Home.test.tsx` | 路由链接、卡片渲染 |
| P1 | `src/pages/Predict.test.tsx` | 模型列表加载、文件上传、预测结果展示 |
| P2 | `src/pages/Compare.test.tsx` | 图表渲染、数据展示 |
| P2 | `src/pages/Visualization.test.tsx` | Tab 切换、数据加载 |

---

## Task 3: CI 工作流（GitHub Actions）

### 3.1 什么是 CI 工作流？

每次你 push 代码或提交 PR 时，GitHub 自动执行以下流程：
1. 拉取你的代码
2. 安装依赖
3. 跑测试
4. 检查构建
5. 告诉你通过了没有

### 3.2 创建 GitHub Actions 工作流

**文件**: 创建 `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install uv
        uses: astral-sh/setup-uv@v5
      - name: Install dependencies
        run: cd backend && uv sync
      - name: Run tests
        run: cd backend && uv run pytest --cov

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run tests
        run: cd frontend && npm test
      - name: Build check
        run: cd frontend && npm run build

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install uv
        uses: astral-sh/setup-uv@v5
      - name: Lint backend
        run: cd backend && uv run ruff check .
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Lint frontend
        run: cd frontend && npm run lint
```

### 3.3 验证

- 推送到 GitHub 后，在仓库的 Actions 标签页查看运行状态
- 所有 job 显示绿色 ✓ 即通过

---

## Task 4: 容器化部署验证

### 4.1 检查 deploy.sh 一致性

**当前状态**: deploy.sh 已配置 PostgreSQL 容器，但后端尚未实际使用数据库。

**验证项**:
- [ ] `./deploy.sh build` 能成功构建前后端镜像
- [ ] `./deploy.sh start` 能正常启动所有服务
- [ ] 后端 API 健康检查通过（`curl http://localhost:8000/api/v1/health`）
- [ ] 前端页面可访问（`curl http://localhost:8080`）

### 4.2 更新 Containerfile

**检查**:
- `backend/Containerfile` - 确保依赖安装完整、权重文件路径正确
- `frontend/Containerfile` - 确保构建产物正确复制到 Nginx

---

## Task 5: 文档更新

### 5.1 README.md

- 添加测试运行说明（后端 `uv run pytest`、前端 `npm test`）
- 添加 CI 状态徽章（可选）
- 更新技术栈描述（添加 Vitest、GitHub Actions）

### 5.2 TRAINING_GUIDE.md

- 确认所有训练相关描述与当前实现一致
- 补充测试和 CI 相关说明

### 5.3 REPORT-v0.3.0.md

- 更新为 v0.3.1 或新建 v0.4.0
- 记录本阶段完成的测试基础设施、CI 工作流

---

## 执行顺序

```
Task 1 (后端测试)  ──┐
                     ├──→ Task 3 (CI 工作流) ──→ Task 4 (部署验证) ──→ Task 5 (文档)
Task 2 (前端测试)  ──┘
```

Task 1 和 Task 2 可并行执行，完成后合并到 Task 3。

---

## 验收标准

- [ ] 后端 `uv run pytest` 全部通过，覆盖率 > 60%
- [ ] 前端 `npm test` 全部通过
- [ ] GitHub Actions CI 绿色通过
- [ ] `./deploy.sh start` 后服务正常运行
- [ ] README 包含测试和 CI 说明

---

## 下一阶段预告（Phase 2）

本阶段完成后，开始以下功能开发：
1. PostgreSQL 数据库集成（SQLAlchemy + Alembic 迁移）
2. 用户注册/登录/鉴权（JWT）
3. 预测历史记录持久化到数据库
4. 用户权限管理
