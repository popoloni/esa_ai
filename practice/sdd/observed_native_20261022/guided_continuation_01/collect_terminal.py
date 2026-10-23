"""Collect actual terminal SDD bytes and history; do not grade or change the task.

Run only after the command receipt and native export have been retained. The
collector uses exclusive creation for its records and never writes the native
project. A later controller/independent review interprets the collected result.
"""
from pathlib import Path
import datetime as dt
import difflib
import hashlib
import json
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "companion/validation"))
from record_observed_command import inventory


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    with path.open("x", encoding="utf-8") as out:
        json.dump(data, out, indent=2)
        out.write("\n")


def main():
    attempt = HERE / "attempt_01"
    task = json.loads((HERE / "CLIENT_TASK_01.json").read_text())
    receipt = json.loads((attempt / "RECEIPT.json").read_text())
    native = json.loads((attempt / "native-session.json").read_text())
    prior = json.loads((HERE / "PRIOR_NATIVE_SESSION.json").read_text())
    project = Path(task["inventory_root"])
    before_tree = HERE.parent / "sdd_native_recovery_01/starting_tree"
    before = {p: item["sha256"] for p, item in json.loads(
        (HERE / "STARTING_MANIFEST.json").read_text())["files"].items()}
    current = inventory(project)
    observed_at = dt.datetime.now(dt.timezone.utc).isoformat()
    changed = sorted(p for p in set(before) | set(current)
                     if before.get(p) != current.get(p))
    diffs = []
    copied = {}
    for relative in changed:
        source = project / relative
        old_source = before_tree / relative
        old = old_source.read_bytes() if relative in before else b""
        if relative in before:
            assert digest(old) == before[relative], relative
        new = source.read_bytes() if source.is_file() and not source.is_symlink() else b""
        if relative in current and not current[relative].startswith("SYMLINK:"):
            target = attempt / "final_artifacts" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as out:
                out.write(new)
            copied[relative] = {"bytes": len(new), "sha256": digest(new)}
        diffs.extend(difflib.unified_diff(
            old.decode("utf-8", errors="replace").splitlines(keepends=True),
            new.decode("utf-8", errors="replace").splitlines(keepends=True),
            fromfile="before/" + relative, tofile="after/" + relative))
    with (attempt / "FINAL_DIFF.patch").open("x") as out:
        out.write("".join(diffs))
    save(attempt / "FINAL_INVENTORY.json", {
        "checked_at_utc": observed_at, "files": current,
        "changed_files": changed, "copied_artifacts": copied,
        "before_matches_command_receipt": before == receipt["before"],
        "after_matches_command_receipt": current == receipt["after"],
        "original_files_unchanged": all(current.get(p) == sha for p, sha in before.items()),
        "out_of_scope_changes": sorted(set(changed) - set(task["allowed_changed_files"])),
        "scope": "Declared project tree only; not an operating-system containment test."})

    events = [json.loads(line) for line in (attempt / "stdout.txt").read_text().splitlines()
              if line.strip()]
    tools = []
    for event in events:
        if event.get("type") != "tool_use":
            continue
        part = event["part"]
        state = part.get("state", {})
        output = state.get("output", "")
        input_value = state.get("input", {})
        item = {"timestamp_ms": event.get("timestamp"), "session_id": event.get("sessionID"),
                "call_id": part.get("callID"), "tool": part.get("tool"),
                "status": state.get("status"), "input": input_value,
                "output_bytes": len(output.encode()), "output_sha256": digest(output.encode()),
                "exit": state.get("metadata", {}).get("exit"),
                "truncated": state.get("metadata", {}).get("truncated")}
        if part.get("tool") == "bash" and input_value.get("command") == "cat inputs/NATIVE_CONTEXT_BUNDLE.md":
            item["matches_complete_preflight_packet"] = output.encode() == (
                before_tree / "inputs/NATIVE_CONTEXT_BUNDLE.md").read_bytes()
        tools.append(item)
    save(attempt / "NATIVE_TOOL_OBSERVATIONS.json", {
        "source": "stdout.txt", "tools": tools,
        "scope": "Completed or error events actually emitted by this continuation; prior-session steps are excluded."})
    first_actions = [event for event in events if event.get("type") in {"text", "tool_use", "error"}]
    if first_actions:
        save(attempt / "FIRST_CONTINUATION_MODEL_ACTION.json", first_actions[0])

    old_messages = {message["info"]["id"]: message for message in prior["messages"]}
    new_messages = {message["info"]["id"]: message for message in native["messages"]}
    history = []
    for identifier, old_message in old_messages.items():
        found = new_messages.get(identifier)
        history.append({"message_id": identifier, "role": old_message["info"]["role"],
                        "retained": found is not None,
                        "parts_exactly_unchanged": bool(found and found["parts"] == old_message["parts"])})
    appended_users = [message for identifier, message in new_messages.items()
                      if identifier not in old_messages and message["info"]["role"] == "user"]
    expected_prompt = (HERE / "CONTINUATION_PROMPT_01.txt").read_text()
    # Pinned cli_run.ts quotes each argument containing a space before passing
    # its non-interactive message to session.prompt. Preserve that distinction.
    expected_cli_prompt = ('"' + expected_prompt.replace('"', '\\"') + '"'
                           if " " in expected_prompt else expected_prompt)
    appended_text = [part.get("text", "") for message in appended_users for part in message["parts"]
                     if part["type"] == "text"]
    save(attempt / "CONTINUATION_HISTORY_CHECK.json", {
        "session_id": native["info"]["id"],
        "same_declared_session": native["info"]["id"] == task["continuation_session_id"],
        "prior_export_sha256": digest((HERE / "PRIOR_NATIVE_SESSION.json").read_bytes()),
        "prior_messages": history, "appended_user_message_count": len(appended_users),
        "appended_prompt_matches_literal_argv_text": appended_text == [expected_prompt],
        "appended_prompt_matches_pinned_cli_serialization": appended_text == [expected_cli_prompt],
        "native_prompt_texts": appended_text,
        "serialization_qualification": "Pinned cli_run.ts lines 289–291 wrap an argument containing spaces in quotes and escape internal quotes. The declared 120-token count concerns the raw appended argument; system/tools/envelopes reserves include serialization overhead. The exact exported user part is retained here.",
        "scope": "Retained native message/part history; not proof that every context token affected the model's reasoning."})
    texts = []
    messages = []
    for identifier, message in new_messages.items():
        if identifier in old_messages or message["info"]["role"] != "assistant":
            continue
        messages.append(message["info"])
        for part in message["parts"]:
            if part["type"] == "text":
                texts.append({"message_id": identifier, "part_id": part.get("id"),
                              "text": part.get("text", ""), "time": part.get("time")})
    save(attempt / "CONTINUATION_ASSISTANT_PARTS.json", {
        "source": "native-session.json", "assistant_messages": messages, "text_parts": texts,
        "scope": "This continuation only. Incomplete messages do not supply completed usage or a terminal model verdict."})
    if texts:
        with (attempt / "FIRST_CONTINUATION_TEXT.txt").open("x") as out:
            out.write(texts[0]["text"])
    save(attempt / "COLLECTION_RECEIPT.json", {
        "collected_at_utc": observed_at, "collector_sha256": digest(Path(__file__).read_bytes()),
        "model_call": False, "project_written": False,
        "native_export_sha256": digest((attempt / "native-session.json").read_bytes()),
        "command_receipt_sha256": digest((attempt / "RECEIPT.json").read_bytes()),
        "human_review": "ABSENT", "acceptance": "Not determined by this collector."})
    print(json.dumps({"changed_files": changed, "native_tool_events": len(tools),
                      "new_assistant_messages": len(messages), "new_text_parts": len(texts),
                      "original_files_unchanged": all(current.get(p) == sha for p, sha in before.items())}, indent=2))


if __name__ == "__main__":
    main()
