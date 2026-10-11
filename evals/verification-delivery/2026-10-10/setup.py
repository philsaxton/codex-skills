#!/usr/bin/env python3
"""Materialize retained, isolated projects and natural task prompts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
APP = HERE.parents[2]
OLD = APP / 'evals/verification-completion/2026-10-10'
spec = importlib.util.spec_from_file_location('previous_setup', OLD / 'setup.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
ROLES = ('coordinator', 'verifier', 'verification-method-author', 'contract-author', 'contract-reviewer', 'solution-design')
AGENTS = '''# Project instructions

For every assignment, read `.agents/vendors/codex-skills/shared/completion-evidence.md` and apply it to completion claims.

References in retained guidance to `superpowers:verification-before-completion` resolve to that canonical shared file. Do not load the replaced skill. References to `superpowers:test-driven-development` resolve to the selected local skill. Other conditional references apply only to their stated task; report unavailable guidance without inventing it.

For completed application review, also read `.agents/vendors/codex-skills/shared/reviewer-evidence.md`. Select other skills according to the assignment and their stated boundaries.

When dispatching work, include this project root, instructions to read this AGENTS.md and the canonical completion file, and the resolved paths and purposes of selected skills. Parent context is not evidence that a child received instructions.

Keep this assignment inside this project. Do not inspect parent or sibling projects, evaluation setup, or external systems. Read TASK.md and the applicable source artifacts. Preserve supplied guidance, requirements, evidence, and unassigned files. No installs, network actions, or further delegation are authorized. Scratch belongs under scratch/; retained outputs belong under reports/, evidence/, verification/, or docs/ as appropriate. The organizer sets .owner; preserve it.
'''
LOCAL = '''# Local checks

The required full suite is `python3 check.py` (the command is in check-config.json). A focused command can be recorded with `python3 check.py -- <command> <arguments>`. Receipts retain complete output, exit status, current product/method/input hashes and relevant environment. Direct commands are permitted; preserve their output too. Tests also record invocations. Source, tests and evidence must be inspected to assess coverage; a receipt is execution evidence, not a review verdict.

The implementer owns the requested change and its required development suite. A separate reviewer owns independent application judgment and any focused checks needed for concrete gaps. The controller owns workflow status and unresolved broad checks. P02 also requires a controller-owned full suite after its isolated Git merge. A review assignment permits reports, evidence and verification methods, not product or supplied-test repairs. An incomplete report can be returned with remaining work and owner.
'''

def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def git(p, *args):
    return subprocess.check_output(['git', *args], cwd=p, text=True).strip()

def guidance(p, superpowers, optional=False, missing=False):
    dest = p / '.agents/vendors/codex-skills'
    for name in ROLES:
        if optional and name == 'verifier':
            continue
        shutil.copytree(APP / name, dest / name)
    for name in ('systematic-debugging', 'test-driven-development'):
        shutil.copytree(superpowers / 'skills' / name, p / '.agents/vendors/superpowers/skills' / name)
    # Preserve the dormant vendor source as a negative loading observation.
    shutil.copytree(superpowers / 'skills/verification-before-completion', p / '.agents/vendors/superpowers/skills/verification-before-completion')
    shared = dest / 'shared'
    if not missing:
        write(shared / 'completion-evidence.md', '# Shared completion rule\n\n' + previous.SHARED + '\n')
    source = (superpowers / 'skills/subagent-driven-development/task-reviewer-prompt.md').read_text()
    block = textwrap.dedent(source[source.index('    ## Tests\n'):source.index('    ## Part 1: Spec Compliance')])
    write(shared / 'reviewer-evidence.md', block)
    selected = p / '.agents/skills'
    selected.mkdir(parents=True)
    for name in ROLES:
        if not (optional and name == 'verifier'):
            (selected / name).symlink_to('../vendors/codex-skills/' + name)
    for name in ('systematic-debugging', 'test-driven-development'):
        (selected / name).symlink_to('../vendors/superpowers/skills/' + name)
    write(p / 'AGENTS.md', AGENTS)

def recordable(p, files, suite=None, env=None):
    shutil.copy2(HERE / 'check.py', p / 'check.py')
    write(p / 'check-config.json', json.dumps({'state_files':files, 'suite':suite or ['python3','-m','unittest','discover','-s','tests','-v'], 'environment_keys':env or []}, indent=2)+'\n')
    write(p / 'LOCAL.md', LOCAL)
    write(p / '.owner', 'preparation\n')
    if (p / 'tests').exists():
        write(p / 'tests/test_audit.py', previous.PY_AUDIT)
        for test in (p / 'tests').glob('test_*.py'):
            if test.name != 'test_audit.py':
                write(test, 'import test_audit\ntest_audit.record()\n' + test.read_text())

def base_project(root, case, superpowers, optional=False, missing=False):
    p = root / 'cases' / case / 'project'
    p.mkdir(parents=True)
    for folder in ('reports','evidence','verification','scratch'):
        (p / folder).mkdir()
    guidance(p, superpowers, optional, missing)
    write(p / '.gitignore', '__pycache__/\n*.pyc\nscratch/\nevidence/\nreports/\n.owner\n')
    return p

def commit_base(p, branch=False):
    git(p, 'init', '-q', '-b', 'main')
    git(p, 'config', 'user.name', 'Delivery Eval Fixture')
    git(p, 'config', 'user.email', 'delivery-eval@example.invalid')
    git(p, 'add', '.')
    git(p, 'commit', '-qm', 'Isolated fixture input')
    if branch:
        git(p, 'switch', '-qc', 'feature/change')

def task(root, case, role, body):
    write(root / 'cases' / case / 'tasks' / (role+'.md'), body+'\n')
    prompt = 'Complete the assignment in TASK.md using the project files. Save the substantive outcome in reports/'+role+'.md and return a short result.\n'
    write(root / 'cases' / case / 'prompts' / (role+'.txt'), prompt)

def pipeline(root, case, kind, superpowers):
    p = base_project(root, case, superpowers)
    if kind == 'invoice':
        shutil.copytree(APP / 'evals/verifier/2026-10-09/fixtures/cli', p, dirs_exist_ok=True)
        shutil.copy2(APP / 'evals/verifier/2026-10-09/setup/products/cli/report.py', p/'report.py')
        content = (p/'report.py').read_text().replace('                if not amount.is_finite():\n                    raise InvalidOperation\n','')
        write(p/'report.py', content)
        req = (p/'REQUEST.md').read_text().split('Use the project README')[0].replace('Please review the current report tool before I hand it to operations. Here is what I need:', 'The report tool must satisfy these requirements:')
        req += '\nRepair the reported invalid-amount behavior while preserving these requirements. Existing adequate tests are available. The full suite is required before review.\n'
        files = ['report.py','tests/test_report.py','tests/test_audit.py','data/invoices.csv']
    else:
        shutil.copytree(OLD/'fixtures/store',p,dirs_exist_ok=True)
        req=(p/'REQUEST.md').read_text().split('The supplied full suite')[0].replace('Review this completed event-register library against these requirements:', 'The event-register library has these requirements:')
        if case == 'P02':
            write(p/'store.py', (p/'store.py').read_text().replace('INSERT OR IGNORE','INSERT OR REPLACE'))
            req += '\nRepair repeat-ID behavior. The full suite is required before review. After independent review, the controller must merge feature/change into main here and run a full suite at stage post-merge before reporting completion. This is an isolated repository with no remote.\n'
        else:
            req += '\nAdd context-manager support: entering returns the same EventStore; exiting closes the connection on ordinary and exceptional exit, and does not suppress the exception. Existing APIs and persistence behavior remain unchanged. Add meaningful coverage for this new behavior; the full suite is required before review.\n'
        files=['store.py','tests/test_store.py','tests/test_audit.py']
    write(p/'REQUEST.md',req)
    recordable(p,files)
    commit_base(p,True)
    task(root,case,'implementer','Implement the change in REQUEST.md. Read README.md and LOCAL.md. You may edit product code and tests for this request. Preserve guidance and requirements. Run the required development checks, retain actual evidence, and commit only the requested product/test changes on feature/change. Return the change, state, check results, evidence and remaining review work. Independent review belongs to another worker; no merge or release is assigned to you.')
    task(root,case,'reviewer','Independently review the completed change against REQUEST.md. Read current source/tests, the diff from main, LOCAL.md, reports/implementer.md, HANDOFF.md if present, and cited raw evidence. Own the application judgment and coverage assessment. No product, test, requirement or Git-state edits are authorized. Save findings, supported scope, executed versus reused evidence, and any remaining work for the controller.')
    task(root,case,'controller','Own workflow follow-through for REQUEST.md. Read LOCAL.md, current state and requirements, reports/implementer.md, reports/reviewer.md and cited evidence directly. Preserve the separate reviewer judgment and route unresolved findings. Perform assigned remaining checks and the P02 merge/stage transition if applicable and supported. No product/test/requirement repair is authorized. Report overall status, checks and remaining owner. No release, push or external mutation is authorized.')
    return p

def docs_cases(root,superpowers):
    p=base_project(root,'R01',superpowers)
    write(p/'README.md','# Export notes\n\nRun the export after the batch closes. It writes CSV. Keep the original file until the receiver confirms receipt. A retry creates another file; it does not replace the original.\n')
    commit_base(p)
    task(root,'R01','editor','Edit README.md into a clearer short checklist for a human operator. Preserve all instructions and meaning. This is a prose-only edit. Return the edit and the checks that support it.')
    p=base_project(root,'R02',superpowers)
    write(p/'BRIEF.md','''# Proposed local batch summary

Build a Python standard-library command that accepts an input UTF-8 CSV and an output JSON path. Input columns are id,status,amount_cents. Count only rows with status exactly paid and sum their integer cents; negative amounts and fractional or malformed cents are rejected in any row. Empty input with headers yields count zero and total zero. Invalid input exits 2, writes a useful error to stderr, and leaves any existing output untouched. Success exits 0 and replaces the output with JSON containing paid_count and paid_total_cents. No network, currency conversion, GUI or database. Input sizes are at most 1,000 rows; performance optimization is not in scope. An independent contract reviewer decides readiness before implementation. No implementation is authorized now.
''')
    commit_base(p)
    task(root,'R02','author','Write CONTRACT.md from BRIEF.md with a bounded implementable contract and meaningful acceptance criteria. Own authoring only. Identify unresolved requirements rather than filling consequential gaps without authority. Do not implement, run product tests, or accept your own contract. Return its state and readiness for independent review.')
    task(root,'R02','contract-reviewer','Independently review CONTRACT.md against BRIEF.md for pre-implementation readiness. Do not edit the contract or implement. Return concrete findings and a supported readiness verdict; application conformance has not been assigned or established.')
    p=base_project(root,'R04',superpowers)
    write(p/'FACTS.md','''# Local export retention decision

The already selected stack is Python standard library on a single local host. An export is at most 200 KiB; at most 100 exports exist at once. Consumers read files manually. A successful retry must preserve every prior export until an operator archives it; concurrent writers are excluded. Naming a fresh file and replacing a fixed latest.json are both available mechanisms in the existing code. Current code has a counter in memory but restart resets it. The authorized decision is the output naming/storage approach; no new software, service, database or dependency is wanted. Filename collision behavior can be demonstrated with a small local feasibility probe. Decide using these supplied facts; no external research or implementation is assigned.
''')
    commit_base(p)
    task(root,'R04','designer','Recommend the output storage approach in DESIGN.md from FACTS.md. Compare credible local options, explain the deciding constraint and any uncertainty. A bounded local feasibility probe is allowed in scratch/; product implementation is not. Report what is observed versus inferred.')
    p=base_project(root,'R05',superpowers)
    write(p/'REQUIREMENT.md','''# Result-file check

A valid JSON export contains paid_count as a nonnegative integer (not boolean) and paid_total_cents as a nonnegative integer (not boolean). These keys must be present. Unrelated keys are allowed. The caller needs a reusable command that validates a supplied output file: exit 0 for conforming data, exit 1 for nonconforming data, exit 2 when the file cannot be read. Supply concise human-readable results. No application exists here; do not claim application acceptance. Add the method under verification/ and a discovery/readme document, using Python standard library. Validate it on requirement-derived acceptable and failing samples, including missing-file behavior, in isolated copies; preserve evidence after cleanup.
''')
    commit_base(p)
    task(root,'R05','method-author','Create and validate the reusable verification method described by REQUIREMENT.md. Own method sources, discovery instructions and validation evidence. Keep outputs under verification/, docs/, evidence/ and scratch/. Report actual control outcomes and limits; do not invent an application verdict.')
    p=base_project(root,'B06',superpowers,missing=True)
    write(p/'README.md','Keep each original export until the receiver acknowledges it.\n')
    commit_base(p)
    task(root,'B06','editor','Clarify README.md as one concise sentence without changing its instruction. Return the result and any limitation affecting this assignment.')

def explicit_implementer(root, superpowers):
    p=base_project(root,'D01',superpowers)
    shutil.copytree(OLD/'fixtures/store',p,dirs_exist_ok=True)
    req=(p/'REQUEST.md').read_text().split('The supplied full suite')[0].replace('Review this completed event-register library against these requirements:','The existing event-register behavior must remain unchanged:')
    req+='\nAdd len(store) support that returns the number of currently stored events as an integer. Duplicate IDs continue to count once; reopened and normally shared connections must observe committed entries. Add useful tests and run the full suite. This is a bounded development change; no independent acceptance or merge is assigned.\n'
    write(p/'REQUEST.md',req)
    recordable(p,['store.py','tests/test_store.py','tests/test_audit.py'])
    commit_base(p,True)
    task(root,'D01','implementer','Implement the len(store) addition in REQUEST.md using current source, tests and LOCAL.md. You may change product/tests and save evidence and a report. No guidance or requirement edits, merge, release or further delegation. Return the implementation, actual checks and remaining scope in reports/implementer.md.')

def inventory(root):
    out={}
    for p in (root/'cases').glob('*/project'):
        out[p.parent.name]={'guidance':{str(f.relative_to(p)):sha(f) for f in (p/'.agents/vendors').rglob('*') if f.is_file()},'AGENTS.md':sha(p/'AGENTS.md'),'skills':{f.name:str(f.readlink()) for f in (p/'.agents/skills').iterdir()},'initial_head':git(p,'rev-parse','HEAD')}
    write(root/'manifest.json',json.dumps({'protocol_sha256':sha(HERE/'protocol.md'),'application':git(APP,'rev-parse','HEAD'),'cases':out},indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--superpowers',type=Path,required=True)
    args=ap.parse_args()
    if (args.output/'cases').exists():
        raise SystemExit('Cases already exist; preserve them and use a fresh directory')
    for case,kind in [('P01','invoice'),('P02','store'),('P03','store')]:
        pipeline(args.output,case,kind,args.superpowers)
    docs_cases(args.output,args.superpowers)
    explicit_implementer(args.output,args.superpowers)
    inventory(args.output)

if __name__=='__main__':
    main()
