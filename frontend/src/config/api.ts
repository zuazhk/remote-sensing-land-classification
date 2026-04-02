export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  models: `${API_BASE_URL}/models`,
  classes: `${API_BASE_URL}/classes`,
  predict: `${API_BASE_URL}/predict`,
  predictBatch: `${API_BASE_URL}/predict/batch`,
  predictCompare: `${API_BASE_URL}/predict/compare`,
  visualization: {
    modelComparison: `${API_BASE_URL}/visualization/model-comparison`,
    confusionMatrix: (modelKey: string) => `${API_BASE_URL}/visualization/confusion-matrix/${modelKey}`,
    rocCurves: (modelKey: string) => `${API_BASE_URL}/visualization/roc-curves/${modelKey}`,
    trainingHistory: (modelKey: string) => `${API_BASE_URL}/visualization/training-history/${modelKey}`,
    featureVisualization: (modelKey: string) => `${API_BASE_URL}/visualization/feature-visualization/${modelKey}`,
  },
  evaluation: {
    metrics: (modelKey: string) => `${API_BASE_URL}/evaluation/${modelKey}`,
  },
  docs: `${API_BASE_URL.replace("/api/v1", "")}/docs`,
  redoc: `${API_BASE_URL.replace("/api/v1", "")}/redoc`,
};
