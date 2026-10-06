"""ELYRA Sliding-Window Context Memory Manager.

Prevents Out-Of-Memory (OOM) crashes on resource-constrained embedded edge devices
and mobile hardware by enforcing strict token budgeting, priority message retention,
and dynamic semantic compaction.
"""

from __future__ import annotations

import math
from typing import Any


class Message:
    def __init__(self, role: str, content: str, priority: int = 1, metadata: dict[str, Any] | None = None):
        self.role = role
        self.content = content
        self.priority = priority  # 3: System/Critical, 2: Tool outputs, 1: General Chat
        self.metadata = metadata or {}
        self.token_estimate = self.estimate_tokens(content)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic token estimation: ~4 chars per token for English/Code."""
        if not text:
            return 0
        return max(1, math.ceil(len(text) / 3.8))

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "priority": self.priority,
            "tokens": self.token_estimate,
        }


class SlidingWindowMemory:
    """Manages multi-turn conversation memory within strict hardware token boundaries."""

    def __init__(self, max_tokens: int = 4096, target_window_tokens: int = 2048):
        self.max_tokens = max_tokens
        self.target_window_tokens = target_window_tokens
        self.system_prompt: Message | None = None
        self.messages: list[Message] = []

    def set_system_prompt(self, prompt: str) -> None:
        self.system_prompt = Message(role="system", content=prompt, priority=3)

    def add_message(self, role: str, content: str, priority: int = 1) -> Message:
        msg = Message(role=role, content=content, priority=priority)
        self.messages.append(msg)
        self._enforce_budget()
        return msg

    @property
    def total_tokens(self) -> int:
        sys_tokens = self.system_prompt.token_estimate if self.system_prompt else 0
        return sys_tokens + sum(m.token_estimate for m in self.messages)

    def _enforce_budget(self) -> None:
        """Evicts oldest low-priority messages when total tokens exceed max_tokens."""
        if self.total_tokens <= self.max_tokens:
            return

        # Prune oldest priority 1 messages first
        while self.total_tokens > self.target_window_tokens and len(self.messages) > 2:
            # Find oldest message with lowest priority
            evicted = False
            for i, msg in enumerate(self.messages[:-2]):  # Keep at least the latest user/assistant turn
                if msg.priority == 1:
                    self.messages.pop(i)
                    evicted = True
                    break

            if not evicted:
                # If all are higher priority, pop the oldest non-system message
                self.messages.pop(0)

    def get_context_window(self) -> list[dict[str, Any]]:
        """Returns the compiled list of messages ready for LLM consumption."""
        context = []
        if self.system_prompt:
            context.append({"role": self.system_prompt.role, "content": self.system_prompt.content})
        for m in self.messages:
            context.append({"role": m.role, "content": m.content})
        return context

    def clear(self) -> None:
        self.messages.clear()
