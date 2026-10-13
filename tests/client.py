import argparse
import time
import requests

def test_inference(url: str, n_requests: int = 5):
    endpoint = f"{url.rstrip('/')}/v1/predict"
    
    sample_payload = {
        "features": {
            "Time": 0.0,
            "V1": -1.359807,
            "V2": -0.072781,
            "V3": 2.536347,
            "V4": 1.378155,
            "V5": -0.338321,
            "V6": 0.462388,
            "V7": 0.239599,
            "V8": 0.098698,
            "V9": 0.363787,
            "V10": 0.090794,
            "V11": -0.551600,
            "V12": -0.617801,
            "V13": -0.991390,
            "V14": -0.311169,
            "V15": 1.468177,
            "V16": -0.470401,
            "V17": 0.207971,
            "V18": 0.025791,
            "V19": 0.403993,
            "V20": 0.251412,
            "V21": -0.018307,
            "V22": 0.277838,
            "V23": -0.110474,
            "V24": 0.066928,
            "V25": 0.128539,
            "V26": -0.189115,
            "V27": 0.133558,
            "V28": -0.021053,
            "Amount": 149.62
        }
    }

    latencies = []
    print(f"Target endpoint: {endpoint}")
    print(f"Executing {n_requests} inference requests...\n")

    for i in range(1, n_requests + 1):
        t0 = time.perf_counter()
        response = requests.post(endpoint, json=sample_payload)
        latency_ms = (time.perf_counter() - t0) * 1000
        latencies.append(latency_ms)

        if response.status_code == 200:
            print(f"[{i}/{n_requests}] HTTP {response.status_code} | Latency: {latency_ms:.2f} ms | Output: {response.json()}")
        else:
            print(f"[{i}/{n_requests}] HTTP {response.status_code} | Error: {response.text}")

    avg_latency = sum(latencies) / len(latencies)
    print(f"\nCompleted: Avg RTT Latency = {avg_latency:.2f} ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inference Test Client")
    parser.add_argument("--url", type=str, default="http://localhost:8000", help="Base URL of the inference server")
    parser.add_argument("--n", type=int, default=5, help="Number of inference requests")
    args = parser.parse_args()

    test_inference(args.url, args.n)
