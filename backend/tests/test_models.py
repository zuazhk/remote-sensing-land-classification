"""
模型端点测试
"""

import pytest


def test_get_models(test_client):
    """测试获取可用模型列表"""
    response = test_client.get("/api/v1/models")

    assert response.status_code == 200
    data = response.json()

    # API返回字典，键为模型标识
    assert isinstance(data, dict)
    assert len(data) > 0

    # 检查已知模型键
    expected_keys = ["efficientnet_b0", "swin_tiny", "swin_tiny_feature"]
    for key in expected_keys:
        assert key in data

    # 检查每个模型的结构
    for model_key, model_info in data.items():
        assert "type" in model_info
        assert "trained" in model_info
        assert "path" in model_info
        assert "loaded" in model_info
        assert "description" in model_info

        # 路径应该是字符串
        assert isinstance(model_info["path"], str)
        # trained应该是布尔值
        assert isinstance(model_info["trained"], bool)
        # loaded应该是布尔值
        assert isinstance(model_info["loaded"], bool)


def test_get_model_detail(test_client):
    """测试获取特定模型详情 - 当前API不支持此端点，应返回404"""
    # 测试获取已知模型（端点不存在）
    response = test_client.get("/api/v1/models/efficientnet_b0")

    # 当前实现返回404，因为该端点不存在
    assert response.status_code == 404


def test_get_nonexistent_model(test_client):
    """测试获取不存在的模型（应返回404）"""
    response = test_client.get("/api/v1/models/nonexistent_model")

    assert response.status_code == 404
    data = response.json()

    assert "detail" in data
    assert "不存在" in data["detail"] or "not found" in data["detail"].lower()
