
import json
import re
import sys

try:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")

    install_pattern = (
        r"(^|[;&|]\s*)"
        r"(npm\s+(install|i|add)|"
        r"yarn\s+add|"
        r"pnpm\s+add)\b"
    )

    if re.search(install_pattern, command):
        print(
            "SAP Safety Hook: Package installation blocked. "
            "Request approval before adding dependencies.",
            file=sys.stderr
        )
        sys.exit(2)

    print(
        "SAP Safety Hook: Bash command checked.",
        file=sys.stderr
    )
    sys.exit(0)

except Exception as error:
    print(f"SAP Safety Hook error: {error}", file=sys.stderr)
    sys.exit(1)
