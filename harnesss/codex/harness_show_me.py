"""
Codex (OpenAI) harness for the HumanLayer "show-me" skill.

This is a minimal runner that loads examples from data/show_me.jsonl and
queries the OpenAI Completion API (Codex/DaVinci). It writes model
outputs to a JSONL file.

Requirements:
  pip install openai

Usage:
  OPENAI_API_KEY=... python harnesss/codex/harness_show_me.py --data data/show_me.jsonl --model text-davinci-003
"""
import os
import json
import argparse
from typing import Dict

try:
    import openai
except ImportError:
    raise SystemExit("Please install openai: pip install openai")


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            yield json.loads(line)


class ShowMeHarness:
    def __init__(self, data_path, model="text-davinci-003", max_tokens=512, temperature=0.0, output_path=None):
        self.data_path = data_path
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.output_path = output_path or "outputs/codex_show_me_outputs.jsonl"

    def run(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY environment variable is required")
        openai.api_key = api_key

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as out_f:
            for example in load_data(self.data_path):
                prompt = example.get("prompt")
                if prompt is None:
                    continue
                resp = openai.Completion.create(
                    engine=self.model,
                    prompt=prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    n=1,
                    stop=None,
                )
                text = resp["choices"][0]["text"]
                result = {
                    "id": example.get("id"),
                    "prompt": prompt,
                    "response": text,
                    "raw": resp,
                }
                out_f.write(json.dumps(result, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/show_me.jsonl")
    p.add_argument("--model", default="text-davinci-003")
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--output", default=None)
    args = p.parse_args()

    harness = ShowMeHarness(data_path=args.data, model=args.model, max_tokens=args.max_tokens, temperature=args.temperature, output_path=args.output)
    harness.run()
