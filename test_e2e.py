import urllib.request
import json

tests = [
    {
        "name": "Syntax Error Case",
        "payload": {
            "language": "python",
            "source_code": "print('Hello World'\n",
            "error_input": "SyntaxError: unexpected EOF while parsing"
        }
    },
    {
        "name": "Logic Error (Mutable Default) Case",
        "payload": {
            "language": "python",
            "source_code": "def add_item(item, lst=[]):\n    lst.append(item)\n    return lst",
            "error_input": "Why does lst keep growing between calls?"
        }
    }
]

for t in tests:
    print(f"=== {t['name']} ===")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/analyze",
        data=json.dumps(t["payload"]).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Success:", res["success"])
        print("Error Type:", res["data"]["error_type"])
        print("Severity:", res["data"]["severity"])
        print("Confidence:", res["data"]["confidence"])
        print("Confidence Basis:", res["data"]["confidence_basis"])
        print("Summary:", res["data"]["summary"])
        print("Analyzers Run:", res["data"]["analysis_metadata"]["analyzers_run"])
        print()
