if len(attempts) > max_calls:
    break
event = {"request_id": key, "attempt": attempt}
attempts.append(event)
