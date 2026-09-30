import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(title, method, path, payload=None):
    print(f"\n{'='*20} {title} ({method} {path}) {'='*20}")
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            print(f"HTTP Status: {status}")
            print(json.dumps(body, indent=2))
            return body
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 1. Health check
    test_endpoint("Health Check", "GET", "/api/v1/health")

    # 2. Supported Languages
    test_endpoint("Supported Languages", "GET", "/api/v1/languages")

    # 3. Analyze NameError
    test_endpoint("Analyze Python NameError", "POST", "/api/v1/analyze", {
        "language": "python",
        "source_code": "def calculate():\n    print(total)\n    total = 10\n",
        "error_input": "Traceback (most recent call last):\n  File \"main.py\", line 2, in calculate\nNameError: name 'total' is not defined"
    })

    # 4. Analyze SyntaxError
    test_endpoint("Analyze Python SyntaxError", "POST", "/api/v1/analyze", {
        "language": "python",
        "source_code": "x = 15\nif x > 10\n    print('greater')\n",
        "error_input": "  File \"app.py\", line 2\n    if x > 10\n            ^\nSyntaxError: expected ':'"
    })
