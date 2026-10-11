#!/usr/bin/env python3
"""Serialize an explicit list of independent fresh workers in one host slot."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root',type=Path)
    ap.add_argument('--after',required=True,help='case/role whose completed metadata releases this slot')
    ap.add_argument('assignments',nargs='+',help='case/role in dispatch order')
    args=ap.parse_args()
    case,role=args.after.split('/')
    previous=args.root/'cases'/case/'runs'/role/'run.json'
    while not previous.exists():time.sleep(2)
    if json.loads(previous.read_text()).get('exit_code')!=0:
        raise SystemExit('Predecessor did not complete; queue stopped')
    for assignment in args.assignments:
        case,role=assignment.split('/')
        print('Starting',assignment,flush=True)
        proc=subprocess.run([sys.executable,str(Path(__file__).with_name('run.py')),str(args.root),case,role])
        meta=args.root/'cases'/case/'runs'/role/'run.json'
        if proc.returncode or not meta.exists() or json.loads(meta.read_text()).get('exit_code')!=0:
            raise SystemExit('Worker did not complete; queue stopped at '+assignment)
        if not (args.root/'cases'/case/'project/reports'/(role+'.md')).exists():
            raise SystemExit('Worker report missing; queue stopped at '+assignment)
    print('Queue complete',flush=True)

if __name__=='__main__':main()
