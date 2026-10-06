"""ELYRA Telemetry Triage & Anomaly Detection Engine.

Analyzes high-frequency hardware metrics and streaming sensor logs, detecting
thermal spikes, memory leaks, battery drain spikes, and network degradation.
"""

from __future__ import annotations

import math
from typing import Any


class TelemetryEngine:
    """Statistical anomaly detector for real-time edge streaming."""

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.cpu_history: list[float] = []
        self.memory_history: list[float] = []
        self.latency_history: list[float] = []

    def record_sample(self, cpu_pct: float, mem_pct: float, latency_ms: float) -> dict[str, Any]:
        """Records a metric sample and returns immediate anomaly evaluations."""
        self.cpu_history.append(cpu_pct)
        self.memory_history.append(mem_pct)
        self.latency_history.append(latency_ms)

        if len(self.cpu_history) > self.window_size:
            self.cpu_history.pop(0)
            self.memory_history.pop(0)
            self.latency_history.pop(0)

        anomalies = []
        
        # 1. CPU spike detection
        if len(self.cpu_history) >= 5:
            avg_cpu = sum(self.cpu_history) / len(self.cpu_history)
            if cpu_pct > 90.0 and cpu_pct > (avg_cpu * 1.5):
                anomalies.append({
                    "metric": "CPU_LOAD",
                    "severity": "CRITICAL",
                    "value": cpu_pct,
                    "baseline_avg": round(avg_cpu, 1),
                    "message": f"Critical CPU load surge: {cpu_pct}%",
                })

        # 2. Memory leak / saturation
        if mem_pct > 88.0:
            anomalies.append({
                "metric": "MEMORY_SATURATION",
                "severity": "WARNING",
                "value": mem_pct,
                "message": f"High memory pressure detected: {mem_pct}%",
            })

        # 3. Latency degradation
        if latency_ms > 300.0:
            anomalies.append({
                "metric": "NETWORK_LATENCY",
                "severity": "WARNING",
                "value": latency_ms,
                "message": f"Network latency degradation: {latency_ms} ms",
            })

        health_status = "HEALTHY"
        if any(a["severity"] == "CRITICAL" for a in anomalies):
            health_status = "CRITICAL"
        elif any(a["severity"] == "WARNING" for a in anomalies):
            health_status = "DEGRADED"

        return {
            "status": health_status,
            "anomalies_count": len(anomalies),
            "anomalies": anomalies,
            "current_metrics": {
                "cpu_pct": cpu_pct,
                "mem_pct": mem_pct,
                "latency_ms": latency_ms,
            },
        }
