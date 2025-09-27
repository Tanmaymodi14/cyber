#!/usr/bin/env python3
import sys
import os
import json
from argparse import ArgumentParser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from technical_engine import evaluate_ac_controls  # type: ignore
from database import ProTechtDatabase  # type: ignore


def main():
    parser = ArgumentParser(description='Headless technical AC controls evaluation (no Flask/UI)')
    parser.add_argument('--json', '-j', action='store_true', help='Output JSON')
    parser.add_argument('--from-file', '-f', help='Path to AWS evidence JSON file instead of DB')
    args = parser.parse_args()

    if args.from_file:
        try:
            with open(args.from_file, 'r') as fh:
                aws_data = json.load(fh)
        except Exception as e:
            print(f"❌ Failed to load evidence file: {e}")
            sys.exit(1)
    else:
        db = ProTechtDatabase()
        aws_data = db.load_aws_data_from_db()

    results = evaluate_ac_controls(aws_data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n=== Technical AC Controls Evaluation ===")
        for cid in sorted(results.keys()):
            r = results[cid]
            print(f"- {cid}: {r['status']} (conf: {r['confidence']:.2f})")
            if r.get('reasons'):
                print("  reasons:")
                for reason in r['reasons']:
                    print(f"    - {reason}")
            if r.get('missing_evidence'):
                print("  missing:")
                for m in r['missing_evidence']:
                    print(f"    - {m}")


if __name__ == '__main__':
    main()



