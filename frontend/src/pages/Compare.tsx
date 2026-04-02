import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { API_ENDPOINTS } from "../config/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const Compare: React.FC = () => {
  // 获取模型对比数据
  const {
    data: comparisonData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["model-comparison"],
    queryFn: async () => {
      const response = await axios.get(API_ENDPOINTS.visualization.modelComparison);
      return response.data;
    },
    retry: 2,
  });

  // 获取模型评估数据（目前使用模拟数据）
  const { data: _evaluationData } = useQuery({
    queryKey: ["model-evaluation"],
    queryFn: async () => {
      // 这里可以调用评估端点，目前使用模拟数据
      return {
        models: [
          { model: "efficientnet_b0", accuracy: 0.92, params: 5.3 },
          { model: "swin_tiny", accuracy: 0.94, params: 28.3 },
          { model: "swin_tiny_feature", accuracy: 0.89, params: 28.3 },
        ],
      };
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p>加载模型对比数据...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-red-600 text-4xl mb-4">❌</div>
          <h3 className="text-xl font-semibold mb-2">加载失败</h3>
          <p className="text-gray-600 mb-4">无法加载模型对比数据</p>
          <p className="text-sm text-gray-500">{error.message}</p>
        </div>
      </div>
    );
  }

  const models = comparisonData?.models || [];
  const safeModels = models.length > 0 ? models : [];

  const accuracyData = safeModels.map((model: any) => ({
    name: model.model,
    准确率: model.accuracy ? model.accuracy * 100 : 0,
  }));

  const inferenceTimeData = safeModels.map((model: any) => ({
    name: model.model,
    推理时间: model.inference_time_ms || 0,
  }));

  const maxAccuracy =
    safeModels.length > 0 ? Math.max(...safeModels.map((m: any) => (m.accuracy || 0) * 100)) : 0;

  const minInferenceTime =
    safeModels.length > 0
      ? Math.min(...safeModels.map((m: any) => m.inference_time_ms || Infinity))
      : 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">模型性能对比</h1>

      {/* 概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>模型数量</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-center py-4">{models.length}</div>
            <p className="text-center text-gray-600">个可用模型</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>最佳准确率</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-center py-4">{maxAccuracy.toFixed(1)}%</div>
            <p className="text-center text-gray-600">最高分类准确率</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>最快推理</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-center py-4">
              {minInferenceTime.toFixed(1)}ms
            </div>
            <p className="text-center text-gray-600">最短推理时间</p>
          </CardContent>
        </Card>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>准确率对比</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={accuracyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis label={{ value: "准确率 (%)", angle: -90, position: "insideLeft" }} />
                  <Tooltip formatter={(value) => [`${value}%`, "准确率"]} />
                  <Legend />
                  <Bar dataKey="准确率" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>推理时间对比</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={inferenceTimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis label={{ value: "时间 (ms)", angle: -90, position: "insideLeft" }} />
                  <Tooltip formatter={(value) => [`${value}ms`, "推理时间"]} />
                  <Legend />
                  <Bar dataKey="推理时间" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 详细对比表格 */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>详细性能指标</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="py-3 px-4 text-left">模型</th>
                  <th className="py-3 px-4 text-left">类型</th>
                  <th className="py-3 px-4 text-left">准确率</th>
                  <th className="py-3 px-4 text-left">推理时间 (ms)</th>
                  <th className="py-3 px-4 text-left">总参数 (百万)</th>
                  <th className="py-3 px-4 text-left">可训练参数 (百万)</th>
                  <th className="py-3 px-4 text-left">训练状态</th>
                </tr>
              </thead>
              <tbody>
                {models.map((model: any, index: number) => (
                  <tr key={model.model} className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                    <td className="py-3 px-4 font-medium">{model.model}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          model.model.includes("efficientnet")
                            ? "bg-blue-100 text-blue-800"
                            : model.model.includes("swin")
                              ? "bg-purple-100 text-purple-800"
                              : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {model.model.includes("efficientnet")
                          ? "CNN"
                          : model.model.includes("swin")
                            ? "Transformer"
                            : "Hybrid"}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {model.accuracy ? (
                        <div className="flex items-center">
                          <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${model.accuracy * 100}%` }}
                            />
                          </div>
                          <span>{(model.accuracy * 100).toFixed(1)}%</span>
                        </div>
                      ) : (
                        "N/A"
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {model.inference_time_ms ? `${model.inference_time_ms.toFixed(1)}ms` : "N/A"}
                    </td>
                    <td className="py-3 px-4">
                      {model.total_params ? (model.total_params / 1e6).toFixed(1) : "N/A"}
                    </td>
                    <td className="py-3 px-4">
                      {model.trainable_params ? (model.trainable_params / 1e6).toFixed(1) : "N/A"}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          model.trained
                            ? "bg-green-100 text-green-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {model.trained ? "已训练" : "未训练"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* 建议部分 */}
      <Card>
        <CardHeader>
          <CardTitle>模型选择建议</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 border rounded-lg">
              <h3 className="font-bold mb-2">EfficientNet-B0</h3>
              <p className="text-sm text-gray-600 mb-3">
                轻量级CNN模型，推理速度快，适合实时应用。
              </p>
              <ul className="text-sm space-y-1">
                <li>✓ 低计算资源需求</li>
                <li>✓ 快速推理</li>
                <li>✓ 适合移动端部署</li>
              </ul>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-bold mb-2">Swin Transformer Tiny</h3>
              <p className="text-sm text-gray-600 mb-3">
                先进的视觉Transformer，准确率高，适合高精度场景。
              </p>
              <ul className="text-sm space-y-1">
                <li>✓ 高分类准确率</li>
                <li>✓ 强大的特征提取能力</li>
                <li>✓ 适合服务器端部署</li>
              </ul>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-bold mb-2">Swin Transformer (特征提取)</h3>
              <p className="text-sm text-gray-600 mb-3">
                迁移学习方案，固定主干网络，只训练分类头。
              </p>
              <ul className="text-sm space-y-1">
                <li>✓ 训练速度快</li>
                <li>✓ 防止过拟合</li>
                <li>✓ 适合小数据集</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Compare;
