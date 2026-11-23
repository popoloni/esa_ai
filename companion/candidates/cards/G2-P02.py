def plan_recurring(slots, is_available):
    """Proposed series planner; returns the dates it would
    book.
    """
    return [slot for slot in slots if is_available(slot)]
