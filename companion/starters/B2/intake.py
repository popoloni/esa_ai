from routing import assess
class ProviderUnavailable(RuntimeError): pass
class ProviderProtocolError(ValueError): pass
def evaluate_batch(requests, provider, *, max_attempts=2, max_calls=4):
    raise NotImplementedError("Implement bounded classification and result attribution")
