#!/usr/bin/env python3
"""Run one fresh CLI worker. Only the CLI host requires outer startup permission."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root',type=Path)
    ap.add_argument('case')
    ap.add_argument('role')
    ap.add_argument('--timeout',type=int,default=420)
    args=ap.parse_args()
    case=args.root/'cases'/args.case
    project=case/'project'
    run=case/'runs'/args.role
    run.mkdir(parents=True,exist_ok=False)
    shutil.copy2(case/'tasks'/(args.role+'.md'),project/'TASK.md')
    (project/'.owner').write_text(args.role+'\n')
    runtime=run/'runtime'
    runtime.mkdir()
    env=os.environ.copy()
    env.update(json.loads((case/'environment.json').read_text()) if (case/'environment.json').exists() else {})
    for name in ('TMPDIR','TMP','TEMP'):env[name]=str(project/'scratch')
    env['PYTHONDONTWRITEBYTECODE']='1'
    command=['codex','--no-daemon','-a','never','-c',f'sqlite_home="{runtime}"','-c',f'log_dir="{runtime}/log"','exec','--ephemeral','--json','-s','workspace-write','-C',str(project),'-o',str(run/'final.txt'),'-']
    metadata={'command':command,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'case':args.case,'role':args.role,'prompt_sha256':hashlib.sha256((case/'prompts'/(args.role+'.txt')).read_bytes()).hexdigest(),'task_sha256':hashlib.sha256((project/'TASK.md').read_bytes()).hexdigest(),'model':'host configured default; no override','effort':'host configured default; no override'}
    start=time.monotonic()
    with (case/'prompts'/(args.role+'.txt')).open() as stdin,(run/'events.jsonl').open('w') as stdout,(run/'stderr.log').open('w') as stderr:
        try:
            result=subprocess.run(command,stdin=stdin,stdout=stdout,stderr=stderr,env=env,timeout=args.timeout)
            metadata['exit_code']=result.returncode
        except subprocess.TimeoutExpired:
            metadata['timeout']=True
    metadata['elapsed_seconds']=time.monotonic()-start
    (run/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metadata.items() if k not in ('command',)}),flush=True)

if __name__=='__main__':main()
