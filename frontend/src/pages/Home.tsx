import React from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/Card";
import { Button } from "../components/ui/Button";

const Home: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">遥感图像土地利用分类系统</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          基于深度学习的现代前后端分离版本，提供图像分类、模型对比和可视化分析功能
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <Card>
          <CardHeader>
            <CardTitle>图像分类</CardTitle>
            <CardDescription>使用深度学习模型对遥感图像进行自动分类</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 mb-6">
              <li>✓ 支持多种模型 (EfficientNet, Swin Transformer)</li>
              <li>✓ 实时预测结果</li>
              <li>✓ 批量图像处理</li>
              <li>✓ 置信度可视化</li>
            </ul>
            <Button asChild className="w-full">
              <Link to="/predict">开始分类</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>模型对比</CardTitle>
            <CardDescription>比较不同模型的性能和准确率</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 mb-6">
              <li>✓ 准确率对比</li>
              <li>✓ 推理时间分析</li>
              <li>✓ 参数量比较</li>
              <li>✓ 混淆矩阵可视化</li>
            </ul>
            <Button asChild variant="outline" className="w-full">
              <Link to="/compare">查看对比</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>可视化分析</CardTitle>
            <CardDescription>深入分析模型性能和学习特征</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 mb-6">
              <li>✓ ROC曲线分析</li>
              <li>✓ 训练历史可视化</li>
              <li>✓ 特征图可视化</li>
              <li>✓ 性能指标图表</li>
            </ul>
            <Button asChild variant="outline" className="w-full">
              <Link to="/visualization">探索分析</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="bg-gray-50 rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-4">系统特性</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">现代架构</h3>
            <p className="text-gray-600">
              前后端分离设计，RESTful API接口，支持跨域访问，响应式前端界面。
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">高性能模型</h3>
            <p className="text-gray-600">
              集成EfficientNet-B0和Swin Transformer等先进模型，在EuroSAT数据集上训练优化。
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">开发者友好</h3>
            <p className="text-gray-600">完整的API文档，清晰的代码结构，易于扩展和维护。</p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">求职作品集</h3>
            <p className="text-gray-600">
              本项目专为求职作品集设计，展示全栈开发能力和深度学习应用经验。
            </p>
          </div>
        </div>
      </div>

      <div className="mt-12 text-center">
        <p className="text-gray-500">
          项目基于原始毕业设计重构，保留所有核心功能，采用现代技术栈重新实现。
        </p>
        <p className="text-sm text-gray-400 mt-2">
          后端API: FastAPI + PyTorch | 前端: React + TypeScript + Vite
        </p>
      </div>
    </div>
  );
};

export default Home;
