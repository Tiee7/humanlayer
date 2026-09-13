更新说明（中文/English）

我已完成：

A) 将 show-me harness 封装并扩展为更接近 OpenAI evals 的 Task 接口（evals/tasks/humanlayer_show_me.py）。
   - 提供 examples(), run_example(), grade(), evaluate() 等方法。
   - 支持直接从命令行运行并输出评估指标与 JSONL 结果。

B) 为 DeepSeek 添加了：
   - harnesss/deepseek/deepseek_runner.py：使用 DeepSeek 风格的 JSONL（id/prompt/gold）进行运行，支持 OpenAI Completion 作为后端或 dry 模式。
   - task_configs/deepseek_show_me.yaml：最小的任务配置示例。

同时我已经保留并更新了之前添加的 prepare 脚本（harnesss/deepseek/prepare_show_me.py）和示例数据（data/show_me.jsonl）。

使用示例（中文）：

1) OpenAI/Evals 风格本地评估：

   pip install openai
   export OPENAI_API_KEY=你的_KEY
   python -m evals.tasks.humanlayer_show_me --data data/show_me.jsonl --model text-davinci-003 --output outputs/evals_show_me_outputs.jsonl

2) DeepSeek 运行（在准备好 deepseek JSONL 后）：

   python harnesss/deepseek/deepseek_runner.py --input data/deepseek_show_me.jsonl --output outputs/deepseek_show_me_outputs.jsonl --model openai --openai-model text-davinci-003

Notes (English):

- The OpenAI-evals adapter is a best-effort implementation: it exposes Task-like methods and a CLI that can be used standalone or referenced from a registry. Full integration with the `openai/evals` framework (metrics hooks, sampling, reporting) can be added if you want me to do so.
- The DeepSeek runner is intentionally minimal and uses the OpenAI Completion API for generation when requested. It also supports a dry mode for local testing without API calls.

Next steps I can take for you:
- Fully implement evals metrics hooks and sampling to match the official evals API (if you want tight integration). 
- Add a Node.js/TypeScript harness that executes the TypeScript skills directly and produces outputs in the same format.
- Add CI to run small smoke tests (requires secrets configuration for OpenAI key if actually calling the API).
