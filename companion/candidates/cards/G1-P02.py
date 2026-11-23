_records = {}
def reserve(path, **request):
    identifier = len(_records.setdefault(str(path), {})) + 1
    _records[str(path)][identifier] = {"reservation_id":
        identifier, **request}
    return Outcome(201, "confirmed", identifier)
