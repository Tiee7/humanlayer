改造说明：

本目录新增了用于 Codex (OpenAI Completion API) 和 DeepSeek 的简单 harness 与数据准备脚本，目的是让该仓库可以被直接用来做快速模型评估或调试。

包含的文件：
- evals/registry/evals/humanlayer_show_me.yaml: OpenAI Evals 风格的注册清单（示例），指向 harnesss/codex/harness_show_me 的调用。
- harnesss/codex/harness_show_me.py: 直接调用 OpenAI Completion API 的最小运行器。需要 OPENAI_API_KEY。
- harnesss/deepseek/prepare_show_me.py: 把 data/show_me.jsonl 转换为 DeepSeek 常用的 id/prompt/gold JSONL。
- data/show_me.jsonl: 三个示例数据点。

如何使用：

1) Codex / OpenAI 快速运行：

  pip install openai
  export OPENAI_API_KEY=...
  python harnesss/codex/harness_show_me.py --data data/show_me.jsonl --model text-davinci-003 --output outputs/codex.jsonl

2) DeepSeek 数据准备：

  python harnesss/deepseek/prepare_show_me.py --input data/show_me.jsonl --output data/deepseek_show_me.jsonl

说明与后续工作建议：
- 这些脚本是最小可运行示例，便于立即上手。如果你希望集成到特定的评估框架（例如 OpenAI evals、EleutherAI 的 lm-eval 或 DeepSeek 的官方 runner），我可以按目标框架改写对应的注册文件与封装类。
- 如果要使用 TypeScript 原代码直接作为评估主体（例如用 Node.js 调用 skill 并评价输出），可以创建等效的 Node.js 脚本并在 README 中加入 npm 依赖和运行示例。
