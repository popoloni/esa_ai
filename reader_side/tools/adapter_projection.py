"""Generate *demonstration* harness adapters from a versioned common core.

No client invocation, no permission grant. Target directory must be a repository
in a separately controlled trusted workspace. No symlinks are required.
"""
from pathlib import Path
import argparse, shutil, hashlib

CORE_TEXT = """# Treasury routing — shared reference to AGENTS.md

Read the repository root AGENTS.md, and the current INT-001 in the reader-side tree.
For any proposed repair, do not change the EUR 5,000 threshold or evidence files.
Ask for review after running the reader-side tests; instructions do not enforce permissions.
"""
TARGETS = {
 "copilot": (".github/copilot-instructions.md", """# Treasury routing — Copilot repository instructions

Consult the repository-root AGENTS.md and the reader-controlled INT-001 before implementation.
Do not change protected acceptance or policy documents.
"""),
 "claude": (".claude/rules/routing.md", """---
paths:
  - "src/treasury/**/*.py"
---
# Treasury routing rule

Consult AGENTS.md and INT-001; preserve BR-001/v1; request human review.
"""),
 "cursor": (".cursor/rules/routing.mdc", """---
description: Treasury Python routing code conventions
globs: src/treasury/**/*.py
alwaysApply: false
---
# Treasury routing rule

Consult AGENTS.md and INT-001; keep evidence independent; request human review.
"""),
 "kiro": (".kiro/steering/treasury.md", """# Treasury routing project steering

Read AGENTS.md and the reader-side intent, preserve BR-001/v1, and report tests and uncertainties.
"""),
 "codex": ("AGENTS.md", """"""),
}

def project(repo: Path, target: str):
    if target not in TARGETS: raise ValueError(f"Unknown target: {target}")
    if not (repo/'AGENTS.md').is_file(): raise ValueError("AGENTS.md required")
    if target=="codex": return ["AGENTS.md"]
    rel,content = TARGETS[target]
    out=repo/rel
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(content,encoding='utf-8')
    result=[rel]
    if target=="claude":
        # Claude project skill location verified in vendor docs.
        # Relative resources travel with SKILL.md as one usable skill bundle.
        source=repo/'.agents/skills/acceptance-review'
        dest=repo/'.claude/skills/acceptance-review'
        shutil.copytree(source,dest,dirs_exist_ok=True)
        result.extend(str((dest/item.relative_to(source)).relative_to(repo))
                      for item in sorted(source.rglob('*')) if item.is_file())
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('target',choices=sorted(TARGETS))
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]/'repo')
    args=parser.parse_args()
    for p in project(args.repo,args.target): print(p)

if __name__=='__main__': main()
