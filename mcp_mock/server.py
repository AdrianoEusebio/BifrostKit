from __future__ import annotations

import json
import sys


def main() -> None:
    raw = sys.stdin.read()
    req = json.loads(raw)

    file_obj = req.get("inputs", {}).get("file", {})
    content = file_obj.get("content", "")

    response = {
        "ok": True,
        "markdown": content + "\n\n<!-- refined by mock MCP -->\n",
    }
    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
