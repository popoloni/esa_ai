#!/usr/bin/env python3
"""Download the two pinned public local-inference artifacts; verify before use.

The large runtime dependencies belong outside the book package. Evidence records
contain only public source URLs, observed bytes, hashes and timings. No model
inference, credential lookup, or external model-service call is made here.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ARTIFACTS = [
    {
        "name": "llama-b11799-bin-ubuntu-x64.tar.gz",
        "url": "https://github.com/ggml-org/llama.cpp/releases/download/b11799/llama-b11799-bin-ubuntu-x64.tar.gz",
        "sha256": "4920c65448350c28f8ce7b35eec91566807e0f111c25a0df2d5fc12a1ed1716a",
        "expected_bytes": 22300522,
        "maximum_bytes": 30000000,
        "publisher": "ggml-org/llama.cpp",
        "revision": "0756e83fc1529e207af783782905bc98a8ef0770",
    },
    {
        "name": "Qwen3-4B-Q4_K_M.gguf",
        "url": "https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/a9a60d009fa7ff9606305047c2bf77ac25dbec49/Qwen3-4B-Q4_K_M.gguf",
        "sha256": "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5",
        "maximum_bytes": 3000000000,
        "publisher": "Qwen",
        "revision": "a9a60d009fa7ff9606305047c2bf77ac25dbec49",
    },
]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def download(item, destination, evidence):
    target = destination / item["name"]
    partial = destination / (item["name"] + ".attempt01.partial")
    record_path = evidence / (item["name"] + ".download.json")
    if target.exists() or partial.exists() or record_path.exists():
        raise FileExistsError("Refusing to overwrite an existing attempt: " + str(target))
    start = time.monotonic()
    record = {"schema": "esa-public-dependency-download/v1", "artifact": item,
              "started_at_utc": now(), "status": "STARTED", "bytes_received": 0}
    evidence.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    digest = hashlib.sha256()
    try:
        request = urllib.request.Request(item["url"], headers={"User-Agent": "ESA-local-lab/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response, partial.open("xb") as output:
            record["http_status"] = response.status
            record["declared_content_length"] = response.headers.get("Content-Length")
            while block := response.read(1024 * 1024):
                record["bytes_received"] += len(block)
                if record["bytes_received"] > item["maximum_bytes"]:
                    raise ValueError("Public artifact exceeds declared size ceiling")
                digest.update(block)
                output.write(block)
        record["observed_sha256"] = digest.hexdigest()
        if record["observed_sha256"] != item["sha256"]:
            raise ValueError("Downloaded artifact does not match the publisher-pinned SHA-256")
        if "expected_bytes" in item and record["bytes_received"] != item["expected_bytes"]:
            raise ValueError("Downloaded artifact has a different declared release size")
        partial.replace(target)
        record["status"] = "PASS_HASH_VERIFIED"
    except Exception as exc:
        record["status"] = "FAILED_RETAINED"
        record["error_type"] = type(exc).__name__
        # Do not retain redirect URLs, which may contain temporary signatures.
        record["error_summary"] = str(exc).split("https://", 1)[0][:300]
        record["observed_partial_sha256"] = digest.hexdigest()
    finally:
        record["finished_at_utc"] = now()
        record["elapsed_seconds"] = time.monotonic() - start
        record_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"artifact": item["name"], "status": record["status"],
                      "bytes": record["bytes_received"], "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
    return record["status"] == "PASS_HASH_VERIFIED"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    args.evidence.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda item: download(item, args.destination, args.evidence), ARTIFACTS))
    raise SystemExit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
