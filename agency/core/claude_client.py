"""Thin wrapper around the Anthropic SDK used by all agents."""
import json
import os
import re
from anthropic import Anthropic


class ClaudeClient:
    def __init__(self, model: str = "claude-opus-4-8"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def complete(self, system: str, prompt: str, max_tokens: int = 4096) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text

    def json_complete(self, system: str, prompt: str, max_tokens: int = 4096) -> dict:
        text = self.complete(system, prompt, max_tokens)
        # Strip markdown fences
        text = re.sub(r"^```(?:json)?\n?", "", text.strip())
        text = re.sub(r"\n?```$", "", text.strip())
        # Extract first JSON object or array
        m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        return json.loads(m.group(1) if m else text)
