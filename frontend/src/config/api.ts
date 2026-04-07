// 开发环境使用完整 URL，生产环境（容器部署）使用相对路径（通过 Nginx 代理）
const isDev = import.meta.env.DEV;
export const API_BASE_URL = isDev
  ? (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1")
  : "/api/v1";

// 动态生成文档链接：直接指向后端 8000 端口，绕过前端 Nginx 代理限制
const getDocsUrl = (path: string) => {
  if (isDev) return `http://localhost:8000${path}`;
  return `${window.location.protocol}//${window.location.hostname}:8000${path}`;
};

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  models: `${API_BASE_URL}/models`,
  classes: `${API_BASE_URL}/classes`,
  predict: `${API_BASE_URL}/predict`,
  predictBatch: `${API_BASE_URL}/predict/batch`,
  predictCompare: `${API_BASE_URL}/predict/compare`,
  auth: {
    register: `${API_BASE_URL}/auth/register`,
    login: `${API_BASE_URL}/auth/login`,
  },
  history: `${API_BASE_URL}/history`,
  visualization: {
    modelComparison: `${API_BASE_URL}/visualization/model-comparison`,
    confusionMatrix: (modelKey: string) => `${API_BASE_URL}/visualization/confusion-matrix/${modelKey}`,
    rocCurves: (modelKey: string) => `${API_BASE_URL}/visualization/roc-curves/${modelKey}`,
    trainingHistory: (modelKey: string) => `${API_BASE_URL}/visualization/training-history/${modelKey}`,
    featureVisualization: (modelKey: string) => `${API_BASE_URL}/visualization/feature-visualization/${modelKey}`,
    architecture: (modelKey: string) => `${API_BASE_URL}/visualization/architecture/${modelKey}`,
  },
  evaluation: {
    metrics: (modelKey: string) => `${API_BASE_URL}/evaluation/${modelKey}`,
  },
  docs: getDocsUrl("/docs"),
  redoc: getDocsUrl("/redoc"),
};
