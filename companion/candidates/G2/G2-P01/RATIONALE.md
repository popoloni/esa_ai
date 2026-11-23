# Proposal G2-P01

Retries should not allocate another reservation. This proposal recognizes the prior operation early and returns its existing identifier, keeping the original row untouched. The common successful-retry path is consequently short, and later conflict checks can concentrate on new operations. The review should consider both repeated delivery and callers that reuse an identifier while revising their request.
