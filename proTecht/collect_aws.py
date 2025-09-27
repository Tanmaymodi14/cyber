#!/usr/bin/env python3
import sys
import os
import json
import argparse

# Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aws_collect import collect_all, build_mixed_evidence
from database import ProTechtDatabase


def main():
    p = argparse.ArgumentParser(description='Collect live AWS data and load into proTecht DB')
    p.add_argument('--profile', help='AWS profile name')
    p.add_argument('--regions', help='Comma-separated regions (default us-east-1)')
    p.add_argument('--dry-run', action='store_true', help='Do not write to DB')
    p.add_argument('--json-out', help='Write collected JSON to file')
    p.add_argument('--mixed-evidence-out', help='Write mixed controls evidence JSON to file')
    args = p.parse_args()

    regions = [r.strip() for r in args.regions.split(',')] if args.regions else ['us-east-1']

    print('⏳ Collecting AWS data...')
    data = collect_all(profile=args.profile, regions=regions)
    print('✅ Collection complete')

    if args.json_out:
        with open(args.json_out, 'w') as f:
            json.dump(data, f, default=str, indent=2)
        print(f'📝 Wrote raw data to {args.json_out}')

    if args.mixed_evidence_out:
        evidence = build_mixed_evidence(data)
        with open(args.mixed_evidence_out, 'w') as f:
            json.dump(evidence, f, default=str, indent=2)
        print(f'📝 Wrote mixed evidence to {args.mixed_evidence_out}')

    if not args.dry_run:
        db = ProTechtDatabase()
        db.load_aws_data(data)
        print('🗄️  Loaded AWS data into database')


if __name__ == '__main__':
    main()
