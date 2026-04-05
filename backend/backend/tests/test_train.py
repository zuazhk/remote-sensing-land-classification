"""训练端点测试

覆盖以下场景：
- start with invalid model_key -> 400
- start with valid请求 -> 200 与 pending 状态
- status for nonexistent task -> 404
- history -> 返回 list（可为空）
- models -> 返回可训练模型字典
- cancel nonexistent task -> 404
"""


def test_train_start_invalid_model(test_client):
    payload = {
        "model_key": "invalid_model",
        "epochs": 1,
        "batch_size": 1,
        "learning_rate": 0.001,
        "image_size": 224,
        "evaluate_after_training": False,
    }
    response = test_client.post("/api/v1/train/start", json=payload)
    assert response.status_code == 400


def test_train_start_valid(test_client):
    """测试启动训练任务 - 只验证请求被接受，不等待训练完成"""
    from unittest.mock import patch

    payload = {
        "model_key": "efficientnet_b0",
        "epochs": 1,
        "batch_size": 1,
        "learning_rate": 0.001,
        "image_size": 224,
        "evaluate_after_training": False,
    }
    # Mock 实际训练函数，避免触发真实训练
    with patch("backend.routes.train.train_cnn_model") as mock_train:
        mock_train.return_value = {"success": True, "result": {}}
        response = test_client.post("/api/v1/train/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in {"pending", "running"}


def test_train_status_nonexistent(test_client):
    response = test_client.get("/api/v1/train/status/nonexistent_task")
    assert response.status_code == 404


def test_train_history(test_client):
    response = test_client.get("/api/v1/train/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_train_models(test_client):
    response = test_client.get("/api/v1/train/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # 至少包含一个已知模型键
    assert "efficientnet_b0" in data
    assert "swin_tiny_feature" in data


def test_train_cancel_nonexistent(test_client):
    response = test_client.delete("/api/v1/train/cancel/nonexistent_task")
    assert response.status_code == 404
