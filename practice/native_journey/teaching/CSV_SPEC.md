# CSV-001/v1: authored teaching specification

**Status:** teaching edit for readability, not native client output or real
product approval. The actual [native specification](../observed/project/spec.md)
is retained separately. The [existing contract](../observed/project/CURRENT_CONTRACT.md)
remains the authority.

## Intended result

An API caller can request CSV for the same actor-visible, optionally
status-filtered orders that the existing JSON response returns, in the same
order. The existing JSON response and source rows remain unchanged.

CSV returns `text/csv; charset=utf-8` and a string body. Its columns are
`order_id`, `status`, `customer`, `amount_eur`, `note`, in that order. An empty
result still includes the header. A standard CSV parser must recover the
selected field values, including commas, quotes, newlines and Unicode.
Every unsupported format raises `ValueError`.

## Consumer decision and deferred work

The authored fictional owner decision **CSV-CONSUMER-01** in the existing
contract selects a machine importer. Preserve values literally, including
formula-like text such as `=SUM(A1:A2)`; silently adding an apostrophe would
change that contract. Spreadsheet viewing needs its own consumer policy and
checks. This decision does not claim spreadsheet safety.

The local exercise starts after authentication. Establishing the actor, HTTP
integration, scale, deployment and actual user benefit remain unvalidated.

## Observable examples

Alice with status `open` receives `A1` from the supplied fixture, including its
multiline note. Bob's `B1` does not appear in that response. A caller with no
matching rows receives the header only. Changing presentation must preserve
those memberships and the JSON behavior.
