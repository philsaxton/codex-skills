#!/usr/bin/env python3
"""Record a project check and the state to which it applies."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time
import uuid

ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage',default='development')
    ap.add_argument('command',nargs=argparse.REMAINDER)
    args=ap.parse_args()
    cfg=json.loads((ROOT/'check-config.json').read_text())
    command=args.command or cfg['suite']
    if command[0]=='--': command=command[1:]
    def state():
        paths=set(cfg['state_files'])
        # Include new test files, so added coverage has an identity too.
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('*.py'))
        return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() if (ROOT/name).is_file() else None for name in sorted(paths)}
    record={'actor':(ROOT/'.owner').read_text().strip(),'stage':args.stage,'command':command,'state':state(),'environment':{'python':platform.python_version(),**{k:os.environ.get(k) for k in cfg['environment_keys']}},'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    start=time.monotonic()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for key in ('TMPDIR','TMP','TEMP'):env[key]=str(ROOT/'scratch')
    proc=subprocess.run(command,cwd=ROOT,env=env,text=True,capture_output=True)
    record.update(exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,elapsed_seconds=time.monotonic()-start,state_after=state())
    dest=ROOT/'evidence'/(uuid.uuid4().hex+'.json')
    dest.write_text(json.dumps(record,indent=2)+'\n')
    print(proc.stdout,end='')
    print(proc.stderr,end='')
    print('Evidence:',dest)
    return proc.returncode

if __name__=='__main__':raise SystemExit(main())
