"""Read-only reports that keep reservation history and current state separate."""

import booking


def build_report(path, reservation_id):
    """Use separate public reads; storage errors propagate without initialization."""
    reservation = booking.get_reservation(path, reservation_id)
    if reservation is None:
        return {"found": False, "reservation": None, "current": None}

    current = booking.reservation_status(path, reservation_id)
    return {"found": True, "reservation": reservation, "current": current}
