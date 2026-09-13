"""
HumanLayer show-me task adapted for OpenAI evals-style usage.

This class provides a Task-like interface and a standalone CLI to run
examples through an OpenAI model (Completion) and produce simple metrics.

It aims to be compatible enough for use in an `evals` registry while
remaining usable as a standalone evaluator.

Usage (standalone):
  export OPENAI_API_KEY=...
  python -m evals.tasks.humanlayer_show_me --data data/show_me.jsonl --model text-davinci-003 --output outputs/evals_show_me_outputs.jsonl

Notes:
- This is a best-effort alignment with OpenAI's evals Task expectations.
- Metrics implemented: exact match, substring match, token overlap ratio.
"""
import os
import json
import argparse
from typing import Dict, Iterator, List, Optional

try:
    import openai
except ImportError:
    openai = None


class HumanLayerShowMeTask:
    """Adapter class exposing Task-like methods for OpenAI evals.

    Methods:
      - examples(): yield example dicts
      - run_example(example): call model and return response text
      - grade(example, response): return grading dict
      - evaluate(...): run through examples, write outputs, return metrics
    """

    def __init__(self, data_path: str = "data/show_me.jsonl", model: str = "text-davinci-003", max_tokens: int = 512, temperature: float = 0.0, output_path: Optional[str] = None, api_key: Optional[str] = None):
        self.data_path = data_path
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.output_path = output_path or "outputs/evals_show_me_outputs.jsonl"
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

        if openai is None:
            raise RuntimeError("openai package is required. Install with `pip install openai`")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required (env or api_key param)")
        openai.api_key = self.api_key

    def examples(self) -> Iterator[Dict]:
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                yield json.loads(line)

    def run_example(self, example: Dict) -> str:
        prompt = example.get("prompt", "")
        resp = openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            n=1,
            stop=None,
        )
        return resp["choices"][0]["text"]

    def grade(self, example: Dict, response: str) -> Dict:
        gold = example.get("expected") or example.get("gold")
        gold_text = (gold or "").strip()
        resp_text = (response or "").strip()

        exact = gold_text == resp_text and gold_text != ""
        contains = gold_text != "" and gold_text in resp_text

        # token overlap (simple)
        gold_tokens = set(gold_text.split()) if gold_text else set()
        resp_tokens = set(resp_text.split()) if resp_text else set()
        overlap = 0.0
        if gold_tokens:
            overlap = len(gold_tokens & resp_tokens) / len(gold_tokens)

        score = 1.0 if exact else (0.75 if contains else overlap)

        return {
            "exact_match": exact,
            "contains_gold": contains,
            "token_overlap": overlap,
            "score": score,
        }

    def evaluate(self) -> Dict:
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        results = []
        metrics = {"examples": 0, "exact_matches": 0, "contains": 0, "avg_token_overlap": 0.0, "avg_score": 0.0}

        for ex in self.examples():
            metrics["examples"] += 1
            resp = self.run_example(ex)
            grade = self.grade(ex, resp)
            results.append({"id": ex.get("id"), "prompt": ex.get("prompt"), "expected": ex.get("expected") or ex.get("gold"), "response": resp, "grade": grade})

            if grade["exact_match"]:
                metrics["exact_matches"] += 1
            if grade["contains_gold"]:
                metrics["contains"] += 1
            metrics["avg_token_overlap"] += grade["token_overlap"]
            metrics["avg_score"] += grade["score"]

        if metrics["examples"] > 0:
            metrics["avg_token_overlap"] /= metrics["examples"]
            metrics["avg_score"] /= metrics["examples"]

        with open(self.output_path, "w", encoding="utf-8") as out_f:
            for r in results:
                out_f.write(json.dumps(r, ensure_ascii=False) + "\n")

        return metrics


# Backwards-compatible thin wrapper class name used in registry
class HumanLayerShowMe(HumanLayerShowMeTask):
    pass


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/show_me.jsonl")
    p.add_argument("--model", default="text-davinci-003")
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--output", default=None)
    p.add_argument("--api-key", default=None)
    args = p.parse_args()

    task = HumanLayerShowMeTask(data_path=args.data, model=args.model, max_tokens=args.max_tokens, temperature=args.temperature, output_path=args.output, api_key=args.api_key)
    metrics = task.evaluate()
    print("Metrics:", json.dumps(metrics, ensure_ascii=False, indent=2))
