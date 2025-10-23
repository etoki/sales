#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except Exception as e:
    print("`openai` パッケージの読み込みに失敗しました。`pip install openai` を実行してください。", file=sys.stderr)
    raise

MODEL = "gpt-5-mini"
PROMPT_FILE = "prompt.txt"

def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("環境変数 OPENAI_API_KEY が設定されていません。", file=sys.stderr)
        return 2

    client = OpenAI()

    prompt_path = Path(__file__).resolve().parent / PROMPT_FILE
    if not prompt_path.exists():
        print(f"固定プロンプトファイルが見つかりません: {prompt_path}", file=sys.stderr)
        return 1

    prompt = prompt_path.read_text(encoding="utf-8")

    try:
        resp = client.responses.create(
            model=MODEL,
            input=prompt
        )
        print(resp.output_text)
        return 0
    except KeyboardInterrupt:
        print("\nユーザーにより中断されました。", file=sys.stderr)
        return 130
    except Exception as e:
        # 予期せぬエラー
        print(f"[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
