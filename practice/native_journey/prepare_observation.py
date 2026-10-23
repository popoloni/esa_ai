#!/usr/bin/env python3
"""Prepare the compact CSV native journey; does not invoke the model.

This author observation uses the existing CSV contract, not a new Spec Kit run.
The project and client state must be fresh. The supplied checks are owner-side.
"""
from pathlib import Path
import argparse, datetime as dt, hashlib, json, os, shutil, subprocess


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--companion',type=Path,required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--project',type=Path,required=True)
    ap.add_argument('--state',type=Path,required=True)
    ap.add_argument('--evidence',type=Path,required=True)
    args=ap.parse_args()
    c=args.companion.resolve(); r=args.runtime.resolve(); p=args.project.resolve(); s=args.state.resolve(); e=args.evidence.resolve()
    if any(x.exists() for x in [p,s,e]): ap.error('Use new project, state and preparation evidence directories')
    shutil.copytree(c/'practice/csv_export/starter',p)
    for name in ['config','data','cache','state','tmp','empty-config']:(s/name).mkdir(parents=True)
    e.mkdir(parents=True)
    binary=r/'opencode/node_modules/.bin/opencode'
    check=c/'practice/csv_export/checks/check.py'
    command=f'python3 -B {check} --candidate {p}'
    edit=['spec.md','plan.md','api.py','presenter.py']
    prefix=p.as_posix().lstrip('/')+'/'
    config={
      '$schema':'https://opencode.ai/config.json','model':'esa-local/esa-qwen3-4b','small_model':'esa-local/esa-qwen3-4b',
      'enabled_providers':['esa-local'],'autoupdate':False,'share':'disabled','compaction':{'auto':False},
      'provider':{'esa-local':{'npm':'@ai-sdk/openai-compatible','name':'ESA local llama.cpp',
        'options':{'baseURL':'http://127.0.0.1:18080/v1','timeout':600000,'headerTimeout':600000},
        'models':{'esa-qwen3-4b':{'name':'Qwen3-4B Q4_K_M local','tool_call':True,'temperature':True,'limit':{'context':16384,'output':2048}}}}},
      'default_agent':'esa-csv',
      'agent':{'esa-csv':{'description':'Small specification-first CSV implementation',
        'mode':'primary','model':'esa-local/esa-qwen3-4b','temperature':0.2,'steps':12,
        'prompt':'Perform the bounded user task using actual tools. Use only permitted files and commands. State observed outcomes accurately. A test result is not human or production approval. Keep specification and plan concise. Do not announce an edit without executing the tool.'}},
      'permission':{'*':'deny','read':{'*':'deny',**{prefix+n:'allow' for n in edit}},
        'edit':{'*':'deny',**{prefix+n:'allow' for n in edit}},
        'external_directory':'deny','glob':'deny','grep':'deny','task':'deny','skill':'deny','webfetch':'deny','websearch':'deny',
        'bash':{'*':'deny',command:'allow'}},'mcp':{}}
    env={'PATH':str(binary.parent)+':'+os.environ.get('PATH','/usr/bin:/bin'),'LANG':'C.UTF-8','TZ':'UTC',
      'NO_UPDATE_NOTIFIER':'1','PYTHONDONTWRITEBYTECODE':'1','OPENCODE_CONFIG':str(e/'OPENCODE_CONFIG.json'),
      'OPENCODE_CONFIG_DIR':str(s/'empty-config'),'OPENCODE_DISABLE_AUTOUPDATE':'true','OPENCODE_DISABLE_DEFAULT_PLUGINS':'true',
      'OPENCODE_DISABLE_LSP_DOWNLOAD':'true','OPENCODE_DISABLE_MODELS_FETCH':'true','OPENCODE_DISABLE_CLAUDE_CODE':'true',
      'OPENCODE_DISABLE_CLAUDE_CODE_PROMPT':'true','OPENCODE_DISABLE_CLAUDE_CODE_SKILLS':'true',
      'XDG_CONFIG_HOME':str(s/'config'),'XDG_DATA_HOME':str(s/'data'),'XDG_CACHE_HOME':str(s/'cache'),
      'XDG_STATE_HOME':str(s/'state'),'TMPDIR':str(s/'tmp'),'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','DO_NOT_TRACK':'1','CI':'1'}
    bundle=[]
    for name in ['CURRENT_CONTRACT.md','api.py','selection.py','demo.py']:
      bundle.append(f'## {name}\n```\n'+(p/name).read_text()+'\n```')
    prompt=f'''Complete one small specification-first journey in {p} using actual tools.
The complete fixed task context is below. Do not reread these unchanged input files; use their full supplied contents. There is no existing spec.md or plan.md. You may read your generated outputs when needed.

1. Write {p}/spec.md: a concise useful feature specification, including actor/status membership, unchanged JSON, ordered CSV fields, header on empty, round-trip special characters, unchanged input, refusal of unsupported format, and the literal-value machine-importer decision. Attribute CSV-CONSUMER-01 to the authored fictional owner in CURRENT_CONTRACT.md. This is an exercise decision, not a real customer approval. Defer spreadsheet viewing, HTTP authentication and deployment.
2. Write {p}/plan.md: at most 12 lines: selected_orders remains the selection authority; compare direct formatter with an optional presenter and choose a proportionate design; name the allowed edit and the exact behavioral check below. Do not invent performance or user benefit claims.
3. Implement CSV in {p}/api.py; you may also create {p}/presenter.py. Preserve all other input files. Use standard-library Python. The native client has not been given a solution or the checker source.
4. Execute exactly this allowed check command with the bash tool (no command chaining):
{command}
5. Read the actual check result, correct an allowed implementation error if needed, and give a short final handoff: actual files, observed check status, the literal-value policy, and untested limits. Stop. Passing selected local checks does not grant release or product approval.

Use native file-writing tools for the specification, plan and code. Do not return file contents only as prose. Steps=12 supplies a last-step instruction, not a hard tool-call limit; the recorder enforces a 900-second invocation bound. Do not start a new phase after that stop.\n\n'''+ '\n\n'.join(bundle)
    write(e/'OPENCODE_CONFIG.json',config);write(e/'ENVIRONMENT.json',env)
    (e/'TASK_PROMPT.txt').write_text(prompt)
    before=inventory(p);write(e/'STARTING_MANIFEST.json',before);shutil.copytree(p,e/'starting_project')
    argv=[str(binary),'--pure','--print-logs','--log-level','DEBUG','run','--title','ESA d9 compact CSV specification to checked implementation','--format','json','--agent','esa-csv','--model','esa-local/esa-qwen3-4b',prompt]
    write(e/'CLIENT_TASK.json',{'argv':argv,'cwd':str(p),'inventory_root':str(p),'allowed_changed_files':edit,'timeout_seconds':900,
      'environment_reference':str(e/'ENVIRONMENT.json'),'prompt_reference':str(e/'TASK_PROMPT.txt'),'prompt_sha256':sha(e/'TASK_PROMPT.txt')})
    protocol={'schema':'esa-native-csv-protocol/v1','prepared_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'preparation_driver_sha256':sha(Path(__file__)),
      'budget':{'total_inference_wall_seconds':2700,'maximum_native_invocations':4,'per_invocation_seconds':900,'policy':'Stop on budget; preserve incomplete outcomes as open.'},
      'route':'Compact authored specification-first CSV route using OpenCode; not a new Spec Kit invocation.',
      'client':'OpenCode 1.19.3','model':'Qwen3-4B Q4_K_M local llama.cpp b11799','source_contract':{'path':str(p/'CURRENT_CONTRACT.md'),'sha256':sha(p/'CURRENT_CONTRACT.md')},
      'exposure':{'native_inputs':['CURRENT_CONTRACT.md','api.py','selection.py','demo.py'],'native_solution_exposed':False,'native_checker_source_exposed':False,
        'author_exposure':'Authoring assistant has seen the supplied checker and prior case description; no reference implementation is supplied to the native client.',
        'disclosed_guidance':'The prompt enumerates existing contract properties and suggests the Python standard library. It supplies no solution patch.'},
      'authority':'CSV-CONSUMER-01 is the existing authored fictional teaching decision. No real business approval or observed user benefit.',
      'permissions':'Application tool rules, not an OS sandbox; localhost model routing does not prove the application makes no other connections.',
      'scope_extension':'Spec.md and plan.md are new teaching records in this separate native project. Existing CSV implementation scope remains api.py plus optional presenter.py.',
      'checker':{'path':str(check),'sha256':sha(check),'argv':['python3','-B',str(check),'--candidate',str(p)]}}
    write(e/'PROTOCOL.json',protocol)
    diagnostics=[]
    for name,cmd in [('git_worktree',['git','rev-parse','--show-toplevel']),('opencode_version',[str(binary),'--version']),('effective_config',[str(binary),'--pure','debug','config']),('effective_agent',[str(binary),'--pure','debug','agent','esa-csv'])]:
      with (e/(name+'.stdout.txt')).open('wb') as out,(e/(name+'.stderr.txt')).open('wb') as err:
        result=subprocess.run(cmd,cwd=p,env=env,stdout=out,stderr=err,timeout=90)
      diagnostics.append({'name':name,'argv':cmd,'exit_code':result.returncode,'stdout':name+'.stdout.txt','stderr':name+'.stderr.txt'})
    write(e/'DIAGNOSTICS.json',diagnostics)
    if diagnostics[0]['exit_code']==0: raise ValueError('Unexpected Git worktree; do not reuse non-Git permission keys.')
    if (e/'opencode_version.stdout.txt').read_text().strip()!='1.19.3':raise ValueError('Unexpected client version')
    with (e/'initial_checks.json').open('wb') as out,(e/'initial_checks.stderr.txt').open('wb') as err:
      rc=subprocess.run(protocol['checker']['argv'],stdout=out,stderr=err).returncode
    write(e/'INITIAL_OBSERVATION.json',{'exit_code':rc,'status':'EXPECTED_CSV_NOT_IMPLEMENTED' if rc==1 else 'INVESTIGATE_START_STATE','project_unchanged':inventory(p)==before})
    print(json.dumps({'preparation':str(e),'project':str(p),'initial_exit':rc,'no_inference':True}))


if __name__=='__main__':main()
