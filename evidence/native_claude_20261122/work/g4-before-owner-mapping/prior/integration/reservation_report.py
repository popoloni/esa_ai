"""Read-only reservation report (INTEGRATION-G3/v1, contribution A)."""
import booking


def build_report(path, reservation_id):
    """Return the historical record and current state, or an absent observation.

    Uses only the public read operations of booking; never initializes or
    mutates storage. Errors propagate. The two reads are not one snapshot.
    """
    reservation = booking.get_reservation(path, reservation_id)
    if reservation is None:
        return {"found": False, "reservation": None, "current": None}
    current = booking.reservation_status(path, reservation_id)
    if current is None:
        raise RuntimeError(
            f"reservation {reservation_id} has a record but no current state")
    return {
        "found": True,
        "reservation": reservation,
        "current": {"state": current["state"], "version": current["version"]},
    }
