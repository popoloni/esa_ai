def reevaluate(self, old_key, new_key, policy_version):
    if old_key == new_key:
        raise HistoryError("NEW_KEY_REQUIRED")
    with transaction(self.conn):
        old = self.replay(old_key)
        self._policy(policy_version)
        return self._decide(
            new_key, old["payload"], policy_version, old_key)
