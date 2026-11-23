if row is None:
    return None
def _readonly_uri(path):
    return Path(path).resolve().as_uri() + "?mode=ro"
