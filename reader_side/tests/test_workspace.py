import unittest,sys,subprocess,tempfile,shutil,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from scope_guard import check_candidate_path,check_integrity
from adapter_projection import project

ROOT=Path(__file__).resolve().parents[2]

class WorkspaceChecks(unittest.TestCase):
    def test_allowed_edit_path(self):
        self.assertTrue(check_candidate_path('src/treasury/routing.py').is_file())
    def test_absolute_rejected(self):
        with self.assertRaises(ValueError):check_candidate_path('/tmp/anything')
    def test_parent_traversal_rejected(self):
        with self.assertRaises(ValueError):check_candidate_path('src/treasury/../routing.py')
    def test_protected_dir_rejected(self):
        with self.assertRaises(ValueError):check_candidate_path('../reader_side/acceptance/test_routing.py')
    def test_sneaky_unknown_file_rejected(self):
        with self.assertRaises(PermissionError):check_candidate_path('src/treasury/secret.py')
    def test_protected_snapshot_untouched(self):
        self.assertEqual(check_integrity(),[])
    def test_modified_protected_note_rejected_in_isolated_copy(self):
        with tempfile.TemporaryDirectory() as td:
            copied=Path(td)/'copy'
            shutil.copytree(ROOT,copied)
            note=copied/'repo/engineering/context/CONTEXT-001.md'
            note.write_text(note.read_text()+'\ncompromised\n')
            self.assertIn('repo/engineering/context/CONTEXT-001.md',check_integrity(copied))
    def test_unknown_new_file_rejected_in_isolated_copy(self):
        with tempfile.TemporaryDirectory() as td:
            copied=Path(td)/'copy'
            shutil.copytree(ROOT,copied)
            (copied/'repo/untracked.txt').write_text('oops')
            self.assertIn('UNTRACKED:repo/untracked.txt',check_integrity(copied))
    def test_symlink_target_rejected_in_isolated_copy(self):
        with tempfile.TemporaryDirectory() as td:
            copied=Path(td)/'repo'
            shutil.copytree(ROOT/'repo',copied)
            src=copied/'src/treasury/routing.py'
            src.unlink()
            src.symlink_to(copied/'AGENTS.md')
            with self.assertRaises(PermissionError):
                check_candidate_path('src/treasury/routing.py',repo=copied)
    def test_skill_required_fields(self):
        content=(ROOT/'repo/.agents/skills/acceptance-review/SKILL.md').read_text()
        self.assertTrue(content.startswith('---\n'))
        self.assertIn('name: acceptance-review',content)
        self.assertIn('description:',content)
        self.assertLess(len(content.split('description:',1)[1].splitlines()[0].strip()),1025)
        self.assertIn('references/review-rubric.md',content)
    def test_adapter_projection_in_temporary_copy(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)/'repo'
            shutil.copytree(ROOT/'repo',repo)
            for target in ('copilot','claude','cursor','kiro','codex'):
                paths=project(repo,target)
                for rel in paths:
                    self.assertTrue((repo/rel).is_file(),rel)
            src=(repo/'.agents/skills/acceptance-review/SKILL.md').read_bytes()
            self.assertEqual((repo/'.claude/skills/acceptance-review/SKILL.md').read_bytes(),src)
            rubric=Path('references/review-rubric.md')
            canonical_skill=repo/'.agents/skills/acceptance-review'
            projected_skill=repo/'.claude/skills/acceptance-review'
            self.assertIn(rubric.as_posix(),(projected_skill/'SKILL.md').read_text())
            self.assertTrue((projected_skill/rubric).is_file(),
                            'The projected skill must include its referenced review rubric')
            self.assertEqual((projected_skill/rubric).read_bytes(),
                             (canonical_skill/rubric).read_bytes())
            self.assertIn('paths:',(repo/'.claude/rules/routing.md').read_text())
            self.assertIn('alwaysApply: false',(repo/'.cursor/rules/routing.mdc').read_text())

if __name__=='__main__':unittest.main()
