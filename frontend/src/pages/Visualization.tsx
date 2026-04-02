import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { API_ENDPOINTS } from "../config/api";

const Visualization: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>("efficientnet_b0");
  const [activeTab, setActiveTab] = useState<"confusion" | "roc" | "training" | "features">(
    "confusion",
  );
  // 特征可视化状态
  const [selectedLayerIndex, setSelectedLayerIndex] = useState<number>(0);
  const [currentChannelPage, setCurrentChannelPage] = useState<number>(1);
  const [channelsPerPage, setChannelsPerPage] = useState<number>(20);

  // 获取模型列表
  const { data: models } = useQuery({
    queryKey: ["models"],
    queryFn: async () => {
      const response = await axios.get(API_ENDPOINTS.models);
      // API返回的是字典，需要转换为数组
      return Object.entries(response.data).map(([key, value]: [string, any]) => ({
        key,
        name: key,
        ...value,
      }));
    },
  });

  // 获取混淆矩阵数据
  const { data: confusionData } = useQuery({
    queryKey: ["confusion-matrix", selectedModel],
    queryFn: async () => {
      const response = await axios.get(
        API_ENDPOINTS.visualization.confusionMatrix(selectedModel),
      );
      return response.data;
    },
    enabled: activeTab === "confusion",
  });

  // 获取ROC曲线数据
  const { data: rocData } = useQuery({
    queryKey: ["roc-curves", selectedModel],
    queryFn: async () => {
      const response = await axios.get(API_ENDPOINTS.visualization.rocCurves(selectedModel));
      return response.data;
    },
    enabled: activeTab === "roc",
  });

  // 获取训练历史数据
  const { data: trainingData } = useQuery({
    queryKey: ["training-history", selectedModel],
    queryFn: async () => {
      const response = await axios.get(
        API_ENDPOINTS.visualization.trainingHistory(selectedModel),
      );
      return response.data;
    },
    enabled: activeTab === "training",
  });

  // 获取特征可视化数据
  const { data: featureData } = useQuery({
    queryKey: ["feature-visualization", selectedModel],
    queryFn: async () => {
      const response = await axios.get(
        API_ENDPOINTS.visualization.featureVisualization(selectedModel),
      );
      return response.data;
    },
    enabled: activeTab === "features",
  });

  const renderConfusionMatrix = () => {
    if (!confusionData) return <div>加载中...</div>;

    const matrix = confusionData.confusion_matrix || [];
    const classes = confusionData.classes || [];

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">混淆矩阵</h3>
          <div className="text-sm text-gray-600">
            总体准确率:{" "}
            <span className="font-bold">{(confusionData.accuracy * 100).toFixed(1)}%</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="border-collapse">
            <thead>
              <tr>
                <th className="p-2 border"></th>
                {classes.map((cls: string) => (
                  <th key={cls} className="p-2 border bg-gray-50 text-sm font-medium">
                    {cls}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.map((row: number[], rowIndex: number) => (
                <tr key={rowIndex}>
                  <td className="p-2 border bg-gray-50 text-sm font-medium">{classes[rowIndex]}</td>
                  {row.map((cell, colIndex) => (
                    <td
                      key={colIndex}
                      className={`p-2 border text-center ${
                        rowIndex === colIndex
                          ? "bg-green-100 text-green-800"
                          : cell > 0
                            ? "bg-red-100 text-red-800"
                            : ""
                      }`}
                    >
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div>
          <h4 className="font-semibold mb-2">各类别准确率</h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(confusionData.class_accuracy || {}).map(([cls, acc]) => (
              <div key={cls} className="border rounded-lg p-3 text-center">
                <div className="font-medium">{cls}</div>
                <div className="text-2xl font-bold text-blue-600">
                  {((acc as number) * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderROCCurves = () => {
    if (!rocData) return <div>加载中...</div>;

    // 后端API返回的数据结构: { fpr: {class1: [...], class2: [...]}, tpr: {class1: [...], class2: [...]} }
    const fprData = rocData.fpr || {};
    const tprData = rocData.tpr || {};
    const classes = Object.keys(fprData);

    // 构建rocCurvesData对象，格式: { className: { fpr: [...], tpr: [...] } }
    const rocCurvesData: Record<string, { fpr: number[]; tpr: number[] }> = {};
    classes.forEach((cls) => {
      rocCurvesData[cls] = {
        fpr: fprData[cls] || [],
        tpr: tprData[cls] || [],
      };
    });

    const chartData: any[] = [];
    if (classes.length > 0 && rocCurvesData[classes[0]]?.fpr) {
      const numPoints = rocCurvesData[classes[0]].fpr.length;
      for (let i = 0; i < numPoints; i++) {
        const point: any = { fpr: rocCurvesData[classes[0]].fpr[i] };
        classes.forEach((cls) => {
          point[`tpr_${cls}`] = rocCurvesData[cls]?.tpr?.[i] || 0;
        });
        chartData.push(point);
      }
    }

    const colors = [
      "#8884d8",
      "#82ca9d",
      "#ffc658",
      "#ff7300",
      "#387908",
      "#a4de6c",
      "#d0ed57",
      "#8dd1e1",
    ];

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold">ROC曲线</h3>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>ROC曲线</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="fpr"
                      label={{ value: "假正率 (FPR)", position: "insideBottom", offset: -5 }}
                      domain={[0, 1]}
                      ticks={[0, 0.2, 0.4, 0.6, 0.8, 1]}
                    />
                    <YAxis
                      label={{ value: "真正率 (TPR)", angle: -90, position: "insideLeft" }}
                      domain={[0, 1]}
                      ticks={[0, 0.2, 0.4, 0.6, 0.8, 1]}
                    />
                    <Tooltip
                      formatter={(value, name) => {
                        const className = (name || "").toString().replace("tpr_", "");
                        return [Number(value).toFixed(3), `TPR (${className})`];
                      }}
                      labelFormatter={(label) => `FPR: ${Number(label).toFixed(3)}`}
                    />
                    <Legend formatter={(value) => value.toString().replace("tpr_", "")} />

                    <Line
                      type="monotone"
                      dataKey={() => 0}
                      stroke="#cccccc"
                      strokeDasharray="5 5"
                      strokeWidth={1}
                      dot={false}
                      name="随机猜测"
                      legendType="none"
                    />

                    {classes.map((cls, index) => (
                      <Line
                        key={cls}
                        type="monotone"
                        dataKey={`tpr_${cls}`}
                        name={`tpr_${cls}`}
                        stroke={colors[index % colors.length]}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  ROC曲线越靠近左上角，模型性能越好。对角线表示随机猜测。
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>AUC值</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(rocData.auc || {}).map(([cls, auc]) => (
                  <div key={cls} className="flex justify-between items-center p-2 border rounded">
                    <span>{cls}</span>
                    <span className="font-bold">{(auc as number).toFixed(3)}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800">AUC值越接近1表示模型性能越好。通常认为：</p>
                <ul className="text-xs text-green-700 mt-1 space-y-1">
                  <li>• AUC &gt; 0.9: 优秀</li>
                  <li>• 0.8 &lt; AUC ≤ 0.9: 良好</li>
                  <li>• 0.7 &lt; AUC ≤ 0.8: 一般</li>
                  <li>• AUC ≤ 0.7: 较差</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>ROC曲线说明</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-blue-500 mr-2"></div>
                <span>真正率 (TPR/召回率): 正确预测为正例的比例</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-red-500 mr-2"></div>
                <span>假正率 (FPR): 错误预测为正例的比例</span>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  ROC曲线展示了在不同分类阈值下，模型对正负样本的区分能力。
                  曲线下面积(AUC)是一个综合性能指标，AUC值越大表示模型性能越好。
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderTrainingHistory = () => {
    if (!trainingData) return <div>加载中...</div>;

    // 准备图表数据
    const lossChartData =
      trainingData.epochs?.map((epoch: number, index: number) => ({
        epoch,
        train_loss: trainingData.train_loss?.[index],
        val_loss: trainingData.val_loss?.[index],
      })) || [];

    const accuracyChartData =
      trainingData.epochs?.map((epoch: number, index: number) => ({
        epoch,
        train_accuracy: trainingData.train_accuracy?.[index]
          ? trainingData.train_accuracy[index] * 100
          : 0,
        val_accuracy: trainingData.val_accuracy?.[index]
          ? trainingData.val_accuracy[index] * 100
          : 0,
      })) || [];

    const lastTrainLoss = trainingData.train_loss?.[trainingData.train_loss.length - 1];
    const lastValLoss = trainingData.val_loss?.[trainingData.val_loss.length - 1];
    const lastTrainAcc = trainingData.train_accuracy?.[trainingData.train_accuracy.length - 1];
    const lastValAcc = trainingData.val_accuracy?.[trainingData.val_accuracy.length - 1];

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold">训练历史</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>损失变化</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={lossChartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="epoch"
                      label={{ value: "训练轮次", position: "insideBottom", offset: -5 }}
                    />
                    <YAxis label={{ value: "损失值", angle: -90, position: "insideLeft" }} />
                    <Tooltip
                      formatter={(value) => [Number(value).toFixed(4), "损失值"]}
                      labelFormatter={(label) => `第 ${label} 轮`}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="train_loss"
                      name="训练损失"
                      stroke="#8884d8"
                      activeDot={{ r: 8 }}
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="val_loss"
                      name="验证损失"
                      stroke="#82ca9d"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 text-sm text-gray-600">
                <p>最终训练损失: {lastTrainLoss?.toFixed(4)}</p>
                <p>最终验证损失: {lastValLoss?.toFixed(4)}</p>
                <p className="mt-1">训练轮次: {trainingData.epochs?.length || 0}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>准确率变化</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={accuracyChartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="epoch"
                      label={{ value: "训练轮次", position: "insideBottom", offset: -5 }}
                    />
                    <YAxis
                      label={{ value: "准确率 (%)", angle: -90, position: "insideLeft" }}
                      domain={[0, 100]}
                    />
                    <Tooltip
                      formatter={(value) => [`${Number(value).toFixed(1)}%`, "准确率"]}
                      labelFormatter={(label) => `第 ${label} 轮`}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="train_accuracy"
                      name="训练准确率"
                      stroke="#ff7300"
                      activeDot={{ r: 8 }}
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="val_accuracy"
                      name="验证准确率"
                      stroke="#387908"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 text-sm text-gray-600">
                <p>最终训练准确率: {(lastTrainAcc * 100)?.toFixed(1)}%</p>
                <p>最终验证准确率: {(lastValAcc * 100)?.toFixed(1)}%</p>
                <p className="mt-1 font-medium">
                  最佳验证准确率: {(trainingData.best_val_accuracy * 100)?.toFixed(1)}% (第{" "}
                  {trainingData.best_epoch} 轮)
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const renderFeatureVisualization = () => {
    if (!featureData) return <div>加载中...</div>;

    const layers = featureData.layers || [];
    if (layers.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-4">🖼️</div>
          <p>没有可用的特征可视化数据</p>
        </div>
      );
    }

    // 确保选中的层索引有效
    const safeLayerIndex = Math.min(selectedLayerIndex, layers.length - 1);
    const selectedLayer = layers[safeLayerIndex];
    const featureMapUrls = selectedLayer.feature_map_urls || [];

    // 计算分页
    const totalPages = Math.ceil(featureMapUrls.length / channelsPerPage);
    const safeCurrentPage = Math.min(Math.max(1, currentChannelPage), totalPages || 1);
    const startIndex = (safeCurrentPage - 1) * channelsPerPage;
    const endIndex = Math.min(startIndex + channelsPerPage, featureMapUrls.length);
    const currentChannels = featureMapUrls.slice(startIndex, endIndex);

    // 每页显示通道数选项
    const pageSizeOptions = [10, 20, 50, 100];

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold">特征可视化</h3>

        {/* 层选择器 */}
        <Card>
          <CardHeader>
            <CardTitle>选择神经网络层</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {layers.map((layer: any, index: number) => (
                <Button
                  key={index}
                  variant={safeLayerIndex === index ? "default" : "outline"}
                  onClick={() => {
                    setSelectedLayerIndex(index);
                    setCurrentChannelPage(1); // 重置页码
                  }}
                  className="flex flex-col items-start py-3 px-4 h-auto"
                >
                  <span className="font-medium">{layer.layer}</span>
                  <span className="text-xs opacity-75 mt-1">
                    通道数: {layer.channels || layer.feature_map_urls?.length || 0}
                  </span>
                </Button>
              ))}
            </div>
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                当前选择: <span className="font-bold">{selectedLayer.layer}</span>(
                {selectedLayer.channels || featureMapUrls.length}个通道)
              </p>
              <p className="text-xs text-blue-700 mt-1">
                特征图展示了模型在该层的激活模式。浅层通常捕捉边缘、纹理等低级特征，深层捕捉更抽象的高级特征。
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 分页控制 */}
        <Card>
          <CardHeader>
            <CardTitle>通道浏览</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
              <div className="flex items-center space-x-4">
                <div>
                  <label className="block text-sm font-medium mb-1">每页显示</label>
                  <select
                    className="p-2 border border-gray-300 rounded-md"
                    value={channelsPerPage}
                    onChange={(e) => {
                      setChannelsPerPage(Number(e.target.value));
                      setCurrentChannelPage(1);
                    }}
                  >
                    {pageSizeOptions.map((size) => (
                      <option key={size} value={size}>
                        {size} 个通道
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <p className="text-sm text-gray-600">
                    通道 {startIndex + 1} - {endIndex} / {featureMapUrls.length}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setCurrentChannelPage((p) => Math.max(1, p - 1))}
                  disabled={safeCurrentPage <= 1}
                >
                  上一页
                </Button>
                <span className="px-3 py-1 border rounded-md">
                  第 {safeCurrentPage} 页 / 共 {totalPages} 页
                </span>
                <Button
                  variant="outline"
                  onClick={() => setCurrentChannelPage((p) => Math.min(totalPages, p + 1))}
                  disabled={safeCurrentPage >= totalPages}
                >
                  下一页
                </Button>
              </div>
            </div>

            {/* 通道网格 */}
            <div className="mb-6">
              {featureMapUrls.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <div className="text-4xl mb-4">📭</div>
                  <p>该层没有特征图数据</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                  {currentChannels.map((url: string, idx: number) => {
                    const channelIndex = startIndex + idx;
                    return (
                      <div
                        key={channelIndex}
                        className="border rounded-lg overflow-hidden bg-gray-50 hover:shadow-md transition-shadow"
                      >
                        <div className="aspect-square flex items-center justify-center bg-gray-100">
                          <img
                            src={url}
                            alt={`${selectedLayer.layer} 通道 ${channelIndex}`}
                            className="w-full h-full object-contain p-1"
                            onError={(e) => {
                              e.currentTarget.src =
                                "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='224' height='224' viewBox='0 0 224 224'%3E%3Crect width='100%25' height='100%25' fill='%23f0f0f0'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='12' fill='%23999'%3E特征图%3C/text%3E%3C/svg%3E";
                            }}
                          />
                        </div>
                        <div className="p-2 text-center border-t bg-white">
                          <p className="text-xs font-medium truncate">通道 {channelIndex}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            尺寸: {selectedLayer.feature_map_size || "未知"}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* 分页导航（底部） */}
            <div className="flex justify-center">
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentChannelPage(1)}
                  disabled={safeCurrentPage <= 1}
                >
                  首页
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentChannelPage((p) => Math.max(1, p - 1))}
                  disabled={safeCurrentPage <= 1}
                >
                  ←
                </Button>
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (safeCurrentPage <= 3) {
                    pageNum = i + 1;
                  } else if (safeCurrentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = safeCurrentPage - 2 + i;
                  }

                  return (
                    <Button
                      key={pageNum}
                      variant={safeCurrentPage === pageNum ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCurrentChannelPage(pageNum)}
                    >
                      {pageNum}
                    </Button>
                  );
                })}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentChannelPage((p) => Math.min(totalPages, p + 1))}
                  disabled={safeCurrentPage >= totalPages}
                >
                  →
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentChannelPage(totalPages)}
                  disabled={safeCurrentPage >= totalPages}
                >
                  末页
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 说明卡片 */}
        <Card>
          <CardHeader>
            <CardTitle>特征可视化说明</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start">
                <div className="w-6 h-6 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                  1
                </div>
                <div>
                  <p className="font-medium">层选择</p>
                  <p className="text-sm text-gray-600">
                    选择不同的神经网络层查看其激活模式。模型通常包含多个层次，从低级特征（边缘、纹理）到高级特征（对象部分、语义概念）。
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-green-100 text-green-800 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                  2
                </div>
                <div>
                  <p className="font-medium">通道浏览</p>
                  <p className="text-sm text-gray-600">
                    每个层包含多个通道（滤波器），每个通道学习检测不同的特征。使用分页控件浏览所有通道。
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="w-6 h-6 bg-purple-100 text-purple-800 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                  3
                </div>
                <div>
                  <p className="font-medium">特征图解读</p>
                  <p className="text-sm text-gray-600">
                    特征图显示了输入图像在不同通道上的激活强度。亮区表示高激活，暗区表示低激活。这些可视化帮助我们理解模型"看到"了什么。
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">模型可视化分析</h1>

      {/* 模型选择 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>选择模型</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {models?.map((model: any) => (
              <Button
                key={model.key}
                variant={selectedModel === model.key ? "default" : "outline"}
                onClick={() => setSelectedModel(model.key)}
              >
                {model.name}
              </Button>
            ))}
          </div>
          <p className="mt-2 text-sm text-gray-600">当前选择: {selectedModel}</p>
        </CardContent>
      </Card>

      {/* 选项卡 */}
      <div className="flex border-b mb-6">
        {[
          { id: "confusion", label: "混淆矩阵" },
          { id: "roc", label: "ROC曲线" },
          { id: "training", label: "训练历史" },
          { id: "features", label: "特征可视化" },
        ].map((tab) => (
          <button
            key={tab.id}
            className={`px-4 py-2 font-medium ${
              activeTab === tab.id
                ? "border-b-2 border-blue-500 text-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
            onClick={() => setActiveTab(tab.id as any)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 内容区域 */}
      <Card>
        <CardContent className="pt-6">
          {activeTab === "confusion" && renderConfusionMatrix()}
          {activeTab === "roc" && renderROCCurves()}
          {activeTab === "training" && renderTrainingHistory()}
          {activeTab === "features" && renderFeatureVisualization()}
        </CardContent>
      </Card>

      {/* 说明 */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">可视化说明</h3>
        <p className="text-sm text-blue-700">
          可视化分析帮助我们深入理解模型性能、识别分类错误模式、优化模型设计。
          混淆矩阵显示各类别的分类情况，ROC曲线评估模型区分能力，训练历史展示学习过程，特征可视化揭示模型内部表示。
        </p>
      </div>
    </div>
  );
};

export default Visualization;
