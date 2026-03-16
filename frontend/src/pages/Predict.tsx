import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { useQuery, useMutation } from "@tanstack/react-query";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8001/api/v1";

const Predict: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>("efficientnet_b0");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] = useState<any>(null);
  const [batchResults, setBatchResults] = useState<any>(null);

  // 获取可用模型
  const { data: models } = useQuery({
    queryKey: ["models"],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/models`);
      // 将字典转换为数组
      return Object.entries(response.data).map(([key, value]) => ({
        key,
        ...(value as any),
        name: key,
      }));
    },
  });

  // 预测突变
  const predictMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await axios.post(`${API_BASE}/predict?model=${selectedModel}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return response.data;
    },
    onSuccess: (data) => {
      setPredictionResult(data);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  };

  const handlePredict = async () => {
    if (!selectedFile) {
      alert("请选择图像文件");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile); // 注意：API期望的字段是'file'，不是'image'

    predictMutation.mutate(formData);
  };

  const handleBatchUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file); // 注意：API期望的字段是'files'，不是'images'
    });

    try {
      const response = await axios.post(
        `${API_BASE}/predict/batch?model=${selectedModel}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        },
      );
      setBatchResults(response.data);
      alert(
        `批量预测完成，处理了 ${response.data.total} 张图像，成功 ${response.data.successful} 张`,
      );
    } catch (error) {
      console.error("批量预测失败:", error);
      alert("批量预测失败");
      setBatchResults(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">图像分类预测</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 左侧：上传和配置 */}
        <Card>
          <CardHeader>
            <CardTitle>预测配置</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">选择模型</label>
              <select
                className="w-full p-2 border border-gray-300 rounded-md"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {models?.map((model: any) => (
                  <option key={model.key} value={model.key}>
                    {model.name} - {model.description}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">上传图像</label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-gray-500">
                    {previewUrl ? (
                      <img src={previewUrl} alt="预览" className="max-h-48 mx-auto mb-4 rounded" />
                    ) : (
                      <div className="py-8">
                        <div className="text-4xl mb-2">📁</div>
                        <p>点击或拖拽图像文件到这里</p>
                        <p className="text-sm text-gray-400 mt-1">支持 JPG、PNG 格式，最大 10MB</p>
                      </div>
                    )}
                  </div>
                </label>
                {selectedFile && <p className="mt-2 text-sm">已选择: {selectedFile.name}</p>}
              </div>
            </div>

            <div className="flex space-x-4">
              <Button onClick={handlePredict} disabled={!selectedFile || predictMutation.isPending}>
                {predictMutation.isPending ? "预测中..." : "开始预测"}
              </Button>
              <Button variant="outline" asChild>
                <label>
                  批量预测
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleBatchUpload}
                    className="hidden"
                  />
                </label>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 右侧：结果展示 */}
        <Card>
          <CardHeader>
            <CardTitle>预测结果</CardTitle>
          </CardHeader>
          <CardContent>
            {predictionResult ? (
              <div className="space-y-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">模型信息</h3>
                  <p>模型: {predictionResult.model}</p>
                  {/* 注意：API当前不返回推理时间字段 */}
                </div>

                {predictionResult.result && (
                  <>
                    <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                      <h3 className="font-semibold text-green-800 mb-1">预测结果</h3>
                      <p className="text-2xl font-bold text-green-900">
                        {predictionResult.result.class}
                      </p>
                      <p className="text-green-700">
                        置信度: {(predictionResult.result.confidence * 100).toFixed(1)}%
                      </p>
                      <p className="text-sm text-green-600 mt-1">
                        类别ID: {predictionResult.result.class_id}
                      </p>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-3">所有类别概率</h3>
                      <div className="space-y-2">
                        {Object.entries(predictionResult.result.all_probabilities || {})
                          .sort(([, a], [, b]) => (b as number) - (a as number))
                          .map(([className, confidence], idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-3 bg-white border rounded-lg"
                            >
                              <span>{className}</span>
                              <div className="flex items-center space-x-4">
                                <div className="w-32 bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-blue-600 h-2 rounded-full"
                                    style={{ width: `${(confidence as number) * 100}%` }}
                                  />
                                </div>
                                <span className="font-semibold">
                                  {((confidence as number) * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <div className="text-4xl mb-4">🔍</div>
                <p>上传图像并点击"开始预测"查看结果</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {batchResults && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>批量预测结果</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-800">
                处理了 <span className="font-bold">{batchResults.total}</span> 张图像， 成功{" "}
                <span className="font-bold">{batchResults.successful}</span> 张， 使用模型{" "}
                <span className="font-bold">{batchResults.model}</span>
              </p>
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {batchResults.results.map((item: any, index: number) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium truncate">{item.filename}</span>
                    {item.result.error ? (
                      <span className="px-2 py-1 bg-red-100 text-red-800 text-sm rounded">
                        失败
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-sm rounded">
                        成功
                      </span>
                    )}
                  </div>

                  {item.result.error ? (
                    <div className="text-red-600 text-sm">
                      <span className="font-medium">错误: </span>
                      {item.result.error}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>预测类别: </span>
                        <span className="font-semibold">{item.result.class}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>置信度: </span>
                        <span className="font-semibold">
                          {(item.result.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">类别ID: {item.result.class_id}</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 模型信息 */}
      {models && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>可用模型</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {models.map((model: any) => (
                <div key={model.key} className="border rounded-lg p-4">
                  <h4 className="font-bold">{model.name}</h4>
                  <p className="text-sm text-gray-600">{model.description}</p>
                  <div className="mt-2 text-sm">
                    <span className="inline-block px-2 py-1 bg-gray-100 rounded">{model.type}</span>
                    {model.trained && (
                      <span className="inline-block ml-2 px-2 py-1 bg-green-100 text-green-800 rounded">
                        已训练
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Predict;
