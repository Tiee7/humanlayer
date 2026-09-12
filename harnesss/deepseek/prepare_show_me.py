"""
Prepare data for DeepSeek-style evaluation by converting the simple
JSONL examples into a DeepSeek-friendly JSONL with fields: id, prompt, gold.

This script is intentionally minimal — consult DeepSeek docs if your
workflow requires additional metadata.

Usage:
  python harnesss/deepseek/prepare_show_me.py --input data/show_me.jsonl --output data/deepseek_show_me.jsonl
"""
import json
import argparse
import os


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            yield json.loads(line)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/show_me.jsonl")
    p.add_argument("--output", default="data/deepseek_show_me.jsonl")
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as out_f:
        for ex in load_data(args.input):
            out = {
                "id": ex.get("id"),
                "prompt": ex.get("prompt"),
                "gold": ex.get("expected")
            }
            out_f.write(json.dumps(out, ensure_ascii=False) + "\n")
