"""预测端点测试"""

import io
from unittest.mock import patch


def test_predict_missing_model(test_client):
    files = {"file": ("sample.jpg", io.BytesIO(b"fakeimage"), "image/jpeg")}
    response = test_client.post("/api/v1/predict", files=files)
    assert response.status_code == 422


def test_predict_invalid_model(test_client):
    files = {"file": ("sample.jpg", io.BytesIO(b"fakeimage"), "image/jpeg")}
    response = test_client.post(
        "/api/v1/predict", data={"model": "not_a_model"}, files=files
    )
    assert response.status_code == 422


def test_predict_invalid_file_type(test_client):
    files = {
        "file": ("sample.pdf", io.BytesIO(b"%PDF-1.4 fake pdf"), "application/pdf")
    }
    response = test_client.post(
        "/api/v1/predict", data={"model": "efficientnet_b0"}, files=files
    )
    assert response.status_code == 422


def test_predict_compare_endpoint_exists(test_client):
    with patch("backend.routes.predict.classifiers", {"efficientnet_b0": None}):
        response = test_client.post(
            "/api/v1/predict/compare",
            files={"file": ("sample.jpg", io.BytesIO(b"fakeimage"), "image/jpeg")},
        )
    assert response.status_code in (200, 500)


def test_predict_batch_empty_files(test_client):
    response = test_client.post(
        "/api/v1/predict/batch", data={"model": "efficientnet_b0"}, files=[]
    )
    assert response.status_code in (400, 422)
