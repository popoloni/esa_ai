# CP07: Git worktree exercise and safety boundary

**Reference:** https://git-scm.com/docs/git-worktree (checked 2026-10-19).

Git worktrees allow multiple checked-out working trees sharing one repository's common Git data. They can help partition separate writable branches but do **not** impose process isolation or replace independent acceptance and human authorization.

If a later authorized task genuinely requires two independent code branches, a reviewer should validate the base commit, ownership, writable paths and merge order before scheduling. This chapter's reference PLAN-007 has **zero ready writers**, so it deliberately does not create worktrees.

For a safe throwaway demonstration, see `build/CP07_GIT_WORKTREE_SMOKE.log` in the checkpoint. The demonstration creates a temporary local repository only; it is not a coding-agent benchmark or proof of sandboxing.
