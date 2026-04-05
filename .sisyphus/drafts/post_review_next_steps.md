# Draft: Phase 1 - PG 前置清理（查漏补缺）

## Requirements (confirmed)
- **阶段定位**: 在引入 PostgreSQL 数据库、用户鉴权等新功能之前，对现有代码库进行阶段性整理和查漏补缺。
- **模型状态确认**: 模型权重、训练记录、特征可视化数据均已正确，**不需要重新训练**。
- **前端测试**: 使用 Vitest（Vite Plus 生态原生测试框架），与现有构建工具链完全匹配。
- **CI 工作流**: 使用 GitHub Actions，实现 push/PR 时自动运行后端 pytest + 前端 Vitest + 构建检查。
- 决策：清理完成后，进入下一阶段（pg 数据库、鉴权等功能开发）。

## Technical Decisions
- 前端测试框架：Vitest（Vite 原生，零配置迁移）
- 后端测试：pytest（已有基础，补充配置和覆盖率）
- CI 平台：GitHub Actions（免费、生态成熟）
- 计划文件：`.sisyphus/plans/phase1-pre-pg-cleanup.md`

## Research Findings
- 代码库探索（bg_4ff77845）:
  - 前端：frontend/src，React Router v6 路由注册，TanStack Query 数据获取，Button/Card 可复用 UI 组件
  - API 配置集中在 frontend/src/config/api.ts，支持开发/生产环境切换
  - Visualization.tsx 是复杂数据驱动 UI 的核心页面
  - 后端：FastAPI，backend/backend/ 双层包结构

- 测试基础设施评估（bg_432c8275）:
  - 后端：pytest 已有 3 个测试文件（test_config.py, test_models.py, test_health.py），conftest.py 提供 test_client fixture
  - 后端缺失：pytest.ini 配置、覆盖率报告、CI 自动化
  - 前端：**完全没有测试**

## Open Questions（已确认）
- ✅ 前端测试：使用 Vitest
- ✅ CI 工作流：使用 GitHub Actions
- ✅ 计划名称：phase1-pre-pg-cleanup
- ⏳ GitHub 仓库是否已启用 Actions？（需确认）
- ⏳ 前端测试优先级：先测核心组件（Button/Card）还是先测页面逻辑（Predict/Compare）？

## Scope Boundaries
- **IN（本阶段要做）**:
  - 后端：添加 pytest 配置、覆盖率报告
  - 前端：引入 Vitest，编写核心组件和页面测试
  - CI：GitHub Actions 工作流（后端 pytest + 前端 Vitest + 构建检查）
  - 文档：更新 README、TRAINING_GUIDE 反映当前状态
  - 部署：验证容器化流程一致性

- **OUT（本阶段不做，下一阶段）**:
  - PostgreSQL 数据库集成
  - 用户鉴权系统
  - 模型重新训练
  - 模型权重修改

## Clearance CHECKLIST
- 核心目标明确？ ✅
- 范围边界清晰（IN/OUT）？ ✅
- 无关键歧义？ ✅
- 技术方案确定？ ✅
- 测试策略确认？ ✅
- 无阻塞问题？ ⏳（待确认 GitHub Actions 是否已启用）

## Research References
- bg_4ff77845 – 代码库模式探索
- bg_432c8275 – 后端测试基础设施评估

## Next Actions
- [Plan-1] 生成正式计划文件 `.sisyphus/plans/phase1-pre-pg-cleanup.md`
- [Plan-2] 确认后开始执行（Start Work）或高准确度审查（High-Accuracy Review）

## Output Notes
- 本计划是 PG 数据库、鉴权等功能加入前的**最后一轮清理**
- 完成后直接进入新功能开发阶段
