"""Recheck saved excerpts using HTTP only; never starts research or model calls."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from comparison import DIMENSIONS, fetch_text, markdown, parse_fields, safe_url, validate_result


def reverify(result, timeout=10):
    for competitor in result['competitors']:
        # Reuse all existing eligibility, normalization and exact-match rules.
        candidates = {}
        for dimension in DIMENSIONS:
            field = competitor['fields'][dimension]
            urls = field['source_urls']
            candidates[dimension] = {
                'quote': field['quote'],
                'url': urls[0] if len(urls) == 1 else '',
            }
        allowed = [u for u in competitor['source_urls'] if safe_url(u)]
        checked = parse_fields(json.dumps({'fields': candidates}), allowed,
                               lambda url: fetch_text(url, timeout))
        for dimension, checked_field in checked.items():
            field = competitor['fields'][dimension]
            for key in ('kind', 'pending', 'fetch_status'):
                field[key] = checked_field[key]
    return validate_result(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path(__file__).with_name('comparison.json'))
    parser.add_argument('--output-dir', type=Path,
                        default=Path(__file__).with_name('reverified'))
    parser.add_argument('--timeout', type=float, default=10)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    result = reverify(json.loads(args.input.read_text(encoding='utf-8')), args.timeout)
    rendered = markdown(result)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'comparison.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.output_dir / 'comparison.md').write_text(rendered, encoding='utf-8')
    for competitor in result['competitors']:
        for dimension, field in competitor['fields'].items():
            print(f'{competitor["name"]} / {dimension}: {field["fetch_status"]}')
    print(f'HTTP recheck saved to {args.output_dir}; fetch failures remain pending.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
