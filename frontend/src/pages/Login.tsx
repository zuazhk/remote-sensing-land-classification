import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

type Mode = "login" | "register";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const [mode, setMode] = useState<Mode>("login");
  // Login fields
  const [lUser, setLUser] = useState<string>("");
  const [lPass, setLPass] = useState<string>("");
  // Register fields
  const [rUser, setRUser] = useState<string>("");
  const [rEmail, setREmail] = useState<string>("");
  const [rPass, setRPass] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const onLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(lUser, lPass);
      navigate("/");
    } catch (err) {
      setError("登录失败，请检查用户名和密码");
    }
  };

  const onRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await register(rUser, rEmail, rPass);
      // After registration, switch to login mode
      setMode("login");
      // Prefill username for convenience and prompt to login
      setLUser(rUser);
      setLPass("");
      setError("注册成功，请登录");
    } catch (err) {
      setError("注册失败，请重试");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-semibold text-gray-800">{mode === "login" ? "登录" : "注册"}</h2>
          <button
            className="text-sm text-blue-600 hover:underline"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
          >
            {mode === "login" ? "没有账号？立即注册" : "已有账号？登录"}
          </button>
        </div>
        {mode === "login" ? (
          <form onSubmit={onLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">用户名</label>
              <input
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                value={lUser}
                onChange={(e) => setLUser(e.target.value)}
                placeholder="用户名"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">密码</label>
              <input
                type="password"
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                value={lPass}
                onChange={(e) => setLPass(e.target.value)}
                placeholder="密码"
                required
              />
            </div>
            {error && <div className="text-sm text-red-600">{error}</div>}
            <div>
              <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-md">登录</button>
            </div>
            <div className="text-sm text-gray-600">或使用下方链接返回首页</div>
          </form>
        ) : (
          <form onSubmit={onRegister} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">用户名</label>
              <input
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                value={rUser}
                onChange={(e) => setRUser(e.target.value)}
                placeholder="用户名"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">邮箱</label>
              <input
                type="email"
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                value={rEmail}
                onChange={(e) => setREmail(e.target.value)}
                placeholder="邮箱地址"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">密码</label>
              <input
                type="password"
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                value={rPass}
                onChange={(e) => setRPass(e.target.value)}
                placeholder="密码"
                required
              />
            </div>
            {error && <div className="text-sm text-red-600">{error}</div>}
            <div>
              <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-md">注册</button>
            </div>
            <div className="text-sm text-gray-600">注册后可在登录页通过用户名登录。</div>
          </form>
        )}
        <div className="mt-4 text-sm text-gray-600">返回主页请点击顶部导航栏的 首页。</div>
      </div>
    </div>
  );
};

export default Login;
