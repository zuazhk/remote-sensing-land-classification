"""
健康检查端点测试
"""

import pytest


def test_health_endpoint(test_client):
    """测试健康检查端点"""
    response = test_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "ok"
    assert "version" in data


def test_root_endpoint(test_client):
    """测试根端点重定向"""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "docs" in data
    assert "version" in data
    assert data["docs"] == "/docs"


def test_api_docs_available(test_client):
    """测试API文档端点可用"""
    response = test_client.get("/docs")
    assert response.status_code == 200

    response = test_client.get("/redoc")
    assert response.status_code == 200
