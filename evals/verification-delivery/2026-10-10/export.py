#!/usr/bin/env python3
"""Export nonprivate execution metadata and evidence identities, not a verdict."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
    manifest=json.loads((args.root/'manifest.json').read_text())
    result={'runtime':manifest.get('runtime', {'source':'Not recorded; preserve the actual runtime settings before dispatch.'}),'scoring':'Independent assessment is in assessment.md and results.md; this file records observations only.','cases':[]}
    for case in sorted((args.root/'cases').iterdir()):
        p=case/'project';cfg=manifest['cases'][case.name]
        row={'case':case.name,'initial_head':cfg['initial_head'],'cli_runs':[],'reports':{},'test_invocations':[],'receipts':{},'guidance_mismatches':[]}
        for name,expected in {**cfg['guidance'],'AGENTS.md':cfg['AGENTS.md']}.items():
            f=p/name
            if not f.is_file() or sha(f)!=expected:row['guidance_mismatches'].append(name)
        for run in sorted((case/'runs').glob('*')):
            meta=json.loads((run/'run.json').read_text())
            events=[json.loads(line) for line in (run/'events.jsonl').read_text().splitlines() if line.strip()]
            items=[e['item'] for e in events if e.get('type')=='item.completed']
            counts={kind:sum(x['type']==kind for x in items) for kind in sorted({x['type'] for x in items})}
            row['cli_runs'].append({'role':run.name,'exit_code':meta.get('exit_code'),'timeout':meta.get('timeout',False),'elapsed_seconds':meta['elapsed_seconds'],'prompt_sha256':meta['prompt_sha256'],'task_sha256':meta['task_sha256'],'events_sha256':sha(run/'events.jsonl'),'final_sha256':sha(run/'final.txt') if (run/'final.txt').exists() else None,'completed_item_counts':counts,'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed']})
        if (case/'explicit-dispatch.json').exists():
            row['native_dispatch']=json.loads((case/'explicit-dispatch.json').read_text())
            for f in (case/'prompts').glob('*-explicit.txt'):row['native_dispatch']['prompt_sha256']=sha(f)
        for f in sorted((p/'reports').glob('*.md')):row['reports'][f.name]={'sha256':sha(f),'words':len(f.read_text().split())}
        for f in sorted((p/'evidence').rglob('*.json')):row['receipts'][str(f.relative_to(p/'evidence'))]=sha(f)
        audit=p/'evidence/test-invocations.jsonl'
        if audit.exists():
            row['test_invocations_sha256']=sha(audit)
            for line in audit.read_text().splitlines():
                event=json.loads(line);argv=event['argv'];normalized=[Path(argv[0]).name,*argv[1:]]
                full='discover' in argv and '-k' not in argv and '-p' not in argv
                row['test_invocations'].append({'actor':event['actor'],'command':normalized,'full_suite_pattern':full,'utc':event['utc']})
        result['cases'].append(row)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(args.output)

if __name__=='__main__':main()
