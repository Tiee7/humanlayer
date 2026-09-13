"""
DeepSeek runner for the show-me task.

This runner expects DeepSeek-style JSONL with fields: id, prompt, gold
(see harnesss/deepseek/prepare_show_me.py to convert the sample data).

It can use OpenAI Completion API to generate responses (if model="openai")
or run in "dry" mode which only copies prompts to outputs for offline use.

Usage:
  export OPENAI_API_KEY=...
  python harnesss/deepseek/deepseek_runner.py --input data/deepseek_show_me.jsonl --output outputs/deepseek_show_me_outputs.jsonl --model openai --openai-model text-davinci-003
"""
import os
import json
import argparse
from typing import Iterator, Dict, Optional

try:
    import openai
except ImportError:
    openai = None


def load_deepseek(path: str) -> Iterator[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            yield json.loads(line)


def call_openai(prompt: str, model: str = "text-davinci-003", max_tokens: int = 512, temperature: float = 0.0, api_key: Optional[str] = None) -> str:
    if openai is None:
        raise RuntimeError("openai package required. pip install openai")
    if api_key:
        openai.api_key = api_key
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is required")
    resp = openai.Completion.create(engine=model, prompt=prompt, max_tokens=max_tokens, temperature=temperature, n=1)
    return resp["choices"][0]["text"]


def evaluate_deepseek(input_path: str, output_path: str, model_type: str = "openai", openai_model: str = "text-davinci-003", max_tokens: int = 512, temperature: float = 0.0, api_key: Optional[str] = None) -> Dict:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    metrics = {"examples": 0, "exact_matches": 0, "contains": 0}

    with open(output_path, "w", encoding="utf-8") as out_f:
        for ex in load_deepseek(input_path):
            metrics["examples"] += 1
            prompt = ex.get("prompt", "")
            gold = ex.get("gold", "")
            if model_type == "openai":
                resp = call_openai(prompt, model=openai_model, max_tokens=max_tokens, temperature=temperature, api_key=api_key)
            else:
                # dry mode: echo prompt
                resp = ""  # leave empty or echo

            exact = gold.strip() == resp.strip() and gold.strip() != ""
            contains = gold.strip() != "" and gold.strip() in resp
            if exact:
                metrics["exact_matches"] += 1
            if contains:
                metrics["contains"] += 1

            out_f.write(json.dumps({"id": ex.get("id"), "prompt": prompt, "gold": gold, "response": resp, "exact": exact, "contains": contains}, ensure_ascii=False) + "\n")

    return metrics


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/deepseek_show_me.jsonl")
    p.add_argument("--output", default="outputs/deepseek_show_me_outputs.jsonl")
    p.add_argument("--model", default="openai", choices=["openai", "dry"]) 
    p.add_argument("--openai-model", default="text-davinci-003")
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--api-key", default=None)
    args = p.parse_args()

    metrics = evaluate_deepseek(args.input, args.output, model_type=args.model, openai_model=args.openai_model, max_tokens=args.max_tokens, temperature=args.temperature, api_key=args.api_key)
    print("DeepSeek-run metrics:", metrics)
