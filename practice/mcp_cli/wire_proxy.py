"""Record this exercise's actual stdio bytes while relaying to its fixed server.

Only use on the synthetic example: a general tool stream can contain secrets.
This is a diagnostic relay, not an isolation or permission mechanism.
"""
from pathlib import Path
import subprocess
import sys
import threading


def main():
    output = Path(sys.argv[1]).resolve()
    server = Path(__file__).with_name("policy_server.py")
    with (output / "client_to_server.jsonl").open("xb") as sent, (output / "server_to_client.jsonl").open("xb") as received:
        process = subprocess.Popen([sys.executable, "-B", str(server)], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=sys.stderr, cwd=server.parent)

        def send():
            try:
                for line in sys.stdin.buffer:
                    sent.write(line); sent.flush()
                    process.stdin.write(line); process.stdin.flush()
            except (BrokenPipeError, OSError):
                pass
            finally:
                try:
                    process.stdin.close()
                except OSError:
                    pass

        writer = threading.Thread(target=send, daemon=True)
        writer.start()
        try:
            for line in process.stdout:
                received.write(line); received.flush()
                sys.stdout.buffer.write(line); sys.stdout.buffer.flush()
            return process.wait(timeout=10)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()


if __name__ == "__main__":
    sys.exit(main())
