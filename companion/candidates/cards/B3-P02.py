current = self._policy(self.active_policy())
record = {**record, "decision": outcome(payload, current)}
return {"status": "REPLAYED", "record": record}
