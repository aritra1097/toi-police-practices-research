"""Structural checks for community submissions; no truth or causality validation."""
from pathlib import Path
import argparse
import csv
import datetime as dt
import json
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent

def validate(path, schema):
    errors, seen, count = [], set(), 0
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, [])
        if header != schema['columns']:
            return ['CSV header/order differs from community/schema.json'], 0
        for number, cells in enumerate(reader, 2):
            if len(cells) != len(header):
                errors.append(f'Record {number}: expected {len(header)} fields, got {len(cells)}')
                continue
            count += 1
            row = dict(zip(header, cells))
            case_id = row['case_id'].strip()
            label = case_id or f'record {number}'
            if case_id in seen:
                errors.append(f'{label}: duplicate case_id')
            seen.add(case_id)
            for key in schema['required_fields']:
                if not row[key].strip():
                    errors.append(f'{label}: missing {key}')
            if row['record_status'] not in schema['record_statuses']:
                errors.append(f'{label}: invalid record_status')
            if row['record_status'] in {'ai_reviewed', 'human_reviewed'} and not row['reviewed_by'].strip():
                errors.append(f'{label}: reviewed record needs reviewed_by')
            if row['record_status'] == 'human_reviewed' and not row['contribution_url'].strip():
                errors.append(f'{label}: human_reviewed needs a review issue/PR URL')
            if not row['event_date_ist'].strip() and not (row['date_basis'].strip() or row['uncertainties'].strip()):
                errors.append(f'{label}: missing incident date needs a date_basis or uncertainties explanation')
            try:
                dt.date.fromisoformat(row['record_updated_date'])
            except ValueError:
                errors.append(f'{label}: record_updated_date must be YYYY-MM-DD')
            if row['bjp_led_state_government'] not in {'', 'True', 'False', 'unknown'}:
                errors.append(f'{label}: bjp_led_state_government must be True, False, unknown, or blank')
            assignment = any(row[key].strip().lower() not in {'', 'unknown', 'not_applicable'} for key in ['chief_minister', 'cm_party_at_incident', 'government_at_incident', 'bjp_led_state_government'])
            for key in ['source_urls', 'government_sources', 'authority_sources', 'contribution_url']:
                tokens = [value.strip() for value in row[key].split(';') if value.strip()]
                required_link = key == 'source_urls' or (key == 'government_sources' and assignment) or (key == 'contribution_url' and row['record_status'] == 'human_reviewed')
                if required_link and not tokens:
                    errors.append(f'{label}: {key} requires at least one source URL')
                for value in tokens:
                    url = urlsplit(value)
                    if url.scheme not in {'http', 'https'} or not url.netloc:
                        errors.append(f'{label}: invalid URL in {key}')
    if not count:
        errors.append('CSV contains no case records')
    return errors, count

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', nargs='?', type=Path, default=ROOT/'cases.csv')
    args = parser.parse_args()
    schema = json.loads((ROOT/'schema.json').read_text())
    try:
        errors, count = validate(args.csv, schema)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        raise SystemExit(f'CSV validation failed: {exc}')
    if errors:
        raise SystemExit('CSV validation failed:\n' + '\n'.join(errors))
    print(f'Valid CSV structure: {count} records. Source truth and coding still require review.')

if __name__ == '__main__':
    main()
