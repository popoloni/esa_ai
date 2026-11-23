# Proposal G3-P03

This version keeps cancellation handling within one write transaction and produces the established owner and version responses from that operation. The code has one state-transition path to follow during review. A requester who does not own the booking still receives the not-owner response, and the current owner receives the normal cancellation response. Check the complete transaction alongside those returned statuses.
