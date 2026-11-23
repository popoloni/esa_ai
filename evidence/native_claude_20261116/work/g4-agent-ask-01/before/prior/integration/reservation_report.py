"""Read-only reservation report (INTEGRATION-G3/v1, contribution A)."""
import booking


def build_report(path, reservation_id):
    """Combine the historical record and the current state via public booking reads.

    The two reads are separate and not a single concurrent snapshot. Errors propagate.
    """
    record = booking.get_reservation(path, reservation_id)
    if record is None:
        return {"found": False, "reservation": None, "current": None}
    status = booking.reservation_status(path, reservation_id)
    if status is None:
        raise LookupError(
            f"reservation {reservation_id} has a record but no current state")
    return {"found": True, "reservation": record,
            "current": {"state": status["state"], "version": status["version"]}}
