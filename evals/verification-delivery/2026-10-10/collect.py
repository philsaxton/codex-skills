#!/usr/bin/env python3
"""Summarize observed executions for independent human/model assessment."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);args=ap.parse_args()
    rows=[]
    for case in sorted((args.root/'cases').iterdir()):
        p=case/'project'
        runs=[]
        for run in sorted((case/'runs').glob('*')):
            events=[json.loads(line) for line in (run/'events.jsonl').read_text().splitlines() if line.strip()]
            commands=[event['item'] for event in events if event['type']=='item.completed' and event.get('item',{}).get('type')=='command_execution']
            runs.append({'role':run.name,'metadata':json.loads((run/'run.json').read_text()) if (run/'run.json').exists() else {'running':True},'commands':[{'command':x['command'],'exit_code':x.get('exit_code')} for x in commands],'usage':[e.get('usage') for e in events if e['type']=='turn.completed'],'final':(run/'final.txt').read_text() if (run/'final.txt').exists() else None})
        receipts=[]
        for f in sorted((p/'evidence').glob('*.json')):
            data=json.loads(f.read_text())
            if isinstance(data,dict) and 'command' in data:
                receipts.append({'file':f.name,**{k:data.get(k) for k in ('actor','command','stage','state','environment','exit_code','elapsed_seconds')}})
        status=subprocess.check_output(['git','status','--short','--branch'],cwd=p,text=True)
        diff=subprocess.check_output(['git','diff','--stat','main'],cwd=p,text=True)
        reports={f.name:f.read_text() for f in (p/'reports').glob('*.md')}
        audit=(p/'evidence/test-invocations.jsonl')
        rows.append({'case':case.name,'runs':runs,'receipts':receipts,'audit':audit.read_text() if audit.exists() else '', 'status':status,'diff_stat_from_main':diff,'reports':reports})
    dest=args.root/'observations.json'
    dest.write_text(json.dumps(rows,indent=2)+'\n')
    print(dest)
    for row in rows:
        print(row['case'],[(r['role'],r['metadata'].get('exit_code', 'running'),len(r['commands'])) for r in row['runs']], 'receipts',len(row['receipts']))

if __name__=='__main__':main()
