# Observed CP01 repair task

Implement INT-001 in repo/src/treasury/routing.py. Reject zero, negative, malformed and nonfinite EUR values with REJECTED / INVALID_AMOUNT. Preserve valid positive routing, EUR 5000 and BR-001/v1. Modify no other project file and do not alter reader-owned intent or acceptance. Run the red baseline, author a minimal patch, run the same seven cases, and retain the diff and raw outputs. Stop at review ready; no human verdict is fabricated.

Actor: the current ChatGPT assistant using workspace tools. Client: ChatGPT workspace tool session. Model: not separately captured. This is not a Codex CLI, Claude Code, Cursor or Copilot run. The assistant had already inspected the protected reference solution and the acceptance cases while editing the chapter. This is an observed teaching repair, not a blind capability evaluation, an independent review, or a productivity comparison.
