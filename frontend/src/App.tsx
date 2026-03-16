import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import Home from "./pages/Home";
import Predict from "./pages/Predict";
import Compare from "./pages/Compare";
import Visualization from "./pages/Visualization";
import { Button } from "./components/ui/Button";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow-md">
            <div className="container mx-auto px-4">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center space-x-8">
                  <Link to="/" className="text-xl font-bold text-gray-900">
                    遥感图像分类
                  </Link>
                  <div className="hidden md:flex space-x-4">
                    <Link to="/">
                      <Button variant="ghost">首页</Button>
                    </Link>
                    <Link to="/predict">
                      <Button variant="ghost">图像分类</Button>
                    </Link>
                    <Link to="/compare">
                      <Button variant="ghost">模型对比</Button>
                    </Link>
                    <Link to="/visualization">
                      <Button variant="ghost">可视化分析</Button>
                    </Link>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <a
                    href="http://127.0.0.1:8001/docs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-600 hover:text-gray-900"
                  >
                    API文档
                  </a>
                  <Button variant="outline" size="sm">
                    登录
                  </Button>
                </div>
              </div>
            </div>
          </nav>

          <div className="md:hidden bg-white border-t">
            <div className="flex justify-around py-2">
              <Link to="/" className="flex flex-col items-center text-sm">
                <div className="text-2xl">🏠</div>
                <span>首页</span>
              </Link>
              <Link to="/predict" className="flex flex-col items-center text-sm">
                <div className="text-2xl">🔍</div>
                <span>分类</span>
              </Link>
              <Link to="/compare" className="flex flex-col items-center text-sm">
                <div className="text-2xl">📊</div>
                <span>对比</span>
              </Link>
              <Link to="/visualization" className="flex flex-col items-center text-sm">
                <div className="text-2xl">📈</div>
                <span>可视化</span>
              </Link>
            </div>
          </div>

          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/predict" element={<Predict />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/visualization" element={<Visualization />} />
            </Routes>
          </main>

          <footer className="bg-gray-800 text-white py-8 mt-12">
            <div className="container mx-auto px-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                  <h3 className="text-lg font-bold mb-4">遥感图像分类系统</h3>
                  <p className="text-gray-400">
                    基于深度学习的现代前后端分离版本，专为求职作品集设计。
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-4">技术栈</h3>
                  <ul className="text-gray-400 space-y-2">
                    <li>前端: React + TypeScript + Vite</li>
                    <li>后端: FastAPI + PyTorch</li>
                    <li>模型: EfficientNet, Swin Transformer</li>
                    <li>部署: Docker + Nginx</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-4">链接</h3>
                  <ul className="text-gray-400 space-y-2">
                    <li>
                      <a
                        href="http://127.0.0.1:8001/docs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-white"
                      >
                        API文档
                      </a>
                    </li>
                    <li>
                      <a
                        href="http://127.0.0.1:8001/redoc"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-white"
                      >
                        ReDoc文档
                      </a>
                    </li>
                    <li>
                      <a
                        href="https://github.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-white"
                      >
                        GitHub仓库
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
                <p>© 2025 遥感图像分类系统 - 前后端分离版本. 毕业设计重构项目.</p>
                <p className="text-sm mt-2">
                  本项目基于原始毕业设计重构，保留所有核心功能，采用现代技术栈重新实现。
                </p>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
