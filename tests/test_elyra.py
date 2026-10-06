"""Comprehensive Test Suite for ELYRA Edge AI Runtime & Telemetry Triage.
"""

import pytest
from fastapi.testclient import TestClient

from runtime.config import settings
from runtime.memory import SlidingWindowMemory, Message
from runtime.tools import tool_registry
from runtime.telemetry import TelemetryEngine
from runtime.router import InferenceRouter, ModelProvider
from runtime.server import app

client = TestClient(app)


def test_sliding_window_memory_budget():
    """Verify sliding-window token budgeting and eviction logic."""
    mem = SlidingWindowMemory(max_tokens=100, target_window_tokens=50)
    mem.set_system_prompt("System context instruction.")

    # Add messages exceeding budget
    for i in range(10):
        mem.add_message("user", f"Long prompt query number {i} with substantial token payload length.", priority=1)

    assert mem.total_tokens <= 120  # stays bounded near budget
    assert len(mem.messages) >= 2  # preserves most recent turn
    assert mem.system_prompt is not None


def test_autonomous_tool_execution():
    """Verify tool execution and schema registration."""
    schemas = tool_registry.get_schemas()
    assert len(schemas) >= 3
    tool_names = [s["function"]["name"] for s in schemas]
    assert "get_device_telemetry" in tool_names
    assert "triage_network_status" in tool_names

    # Execute telemetry
    res = tool_registry.execute("get_device_telemetry", {})
    assert "cpu_usage_pct" in res
    assert "memory_used_pct" in res
    assert "platform" in res


def test_telemetry_anomaly_engine():
    """Verify statistical anomaly detection across metric samples."""
    engine = TelemetryEngine(window_size=10)

    # 1. Nominal sample
    res1 = engine.record_sample(cpu_pct=20.0, mem_pct=40.0, latency_ms=15.0)
    assert res1["status"] == "HEALTHY"

    # 2. Critical CPU surge
    for _ in range(5):
        engine.record_sample(cpu_pct=15.0, mem_pct=40.0, latency_ms=15.0)

    res_spike = engine.record_sample(cpu_pct=95.0, mem_pct=40.0, latency_ms=15.0)
    assert res_spike["status"] == "CRITICAL"
    assert res_spike["anomalies_count"] >= 1


def test_inference_router_and_chat_endpoint():
    """Verify FastAPI chat and telemetry API endpoints."""
    # Health endpoint
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"

    # Models endpoint
    res_models = client.get("/v1/models")
    assert res_models.status_code == 200
    assert "default_local" in res_models.json()

    # Tools endpoint
    res_tools = client.get("/v1/tools")
    assert res_tools.status_code == 200

    # Chat endpoint (deterministic edge execution)
    res_chat = client.post("/v1/chat", json={"prompt": "Report edge device CPU telemetry"})
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert "response" in data
    assert "tokens_used" in data
