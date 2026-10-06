"""ELYRA FastAPI Edge Server & WebSocket Telemetry Gateway.

Serves local REST API endpoints and sub-second WebSocket streams for the ELYRA Android APK
and mobile edge clients.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .memory import SlidingWindowMemory
from .router import InferenceRouter
from .telemetry import TelemetryEngine
from .tools import tool_registry

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Autonomous Mobile Edge AI Runtime & Telemetry Assistant",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = InferenceRouter()
telemetry_engine = TelemetryEngine()
global_memory = SlidingWindowMemory(
    max_tokens=settings.max_context_tokens,
    target_window_tokens=settings.sliding_window_tokens
)
global_memory.set_system_prompt(
    "You are ELYRA, an autonomous on-device edge AI assistant and telemetry diagnostic agent. "
    "Respond concisely with high technical precision."
)


class ChatRequest(BaseModel):
    prompt: str
    model: str | None = None
    offline_only: bool = False


class TelemetrySample(BaseModel):
    cpu_pct: float
    mem_pct: float
    latency_ms: float


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.app_name,
        "version": settings.version,
        "local_ollama_active": router.check_local_ollama_availability(),
        "memory_tokens": global_memory.total_tokens,
    }


@app.get("/v1/models")
def list_available_models():
    return {
        "default_local": settings.default_local_model,
        "fallback_cloud": settings.fallback_cloud_model,
        "ollama_connected": router.check_local_ollama_availability(),
        "supported_architectures": ["qwen2.5", "llama3.2", "phi3.5", "deepseek-r1-distill"],
    }


@app.get("/v1/tools")
def list_tools():
    return {"tools": tool_registry.get_schemas()}


@app.post("/v1/chat")
def chat_turn(req: ChatRequest):
    """Executes a single conversational turn with sliding-window memory management."""
    global_memory.add_message("user", req.prompt, priority=1)
    result = router.execute_inference(
        memory=global_memory,
        model_name=req.model,
        offline_only=req.offline_only,
    )
    return result


@app.post("/v1/telemetry/sample")
def record_telemetry(sample: TelemetrySample):
    """Ingests real-time hardware telemetry and evaluates anomalies."""
    result = telemetry_engine.record_sample(
        cpu_pct=sample.cpu_pct,
        mem_pct=sample.mem_pct,
        latency_ms=sample.latency_ms,
    )
    return result


@app.websocket("/v1/stream/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """Real-time sub-second telemetry stream for the Android APK visualizer."""
    await websocket.accept()
    try:
        while True:
            diag = tool_registry.execute("get_device_telemetry", {})
            eval_res = telemetry_engine.record_sample(
                cpu_pct=diag.get("cpu_usage_pct", 0),
                mem_pct=diag.get("memory_used_pct", 0),
                latency_ms=12.5,
            )
            payload = {
                "timestamp": time.time(),
                "telemetry": diag,
                "analysis": eval_res,
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(settings.telemetry_interval_sec)
    except WebSocketDisconnect:
        pass
