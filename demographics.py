from typing import Any, Dict, List

from category_mapping import is_mm, is_om, is_pwd, map_category

CATEGORIES = ['General', 'EWS', 'OBC', 'SC', 'ST']
ROW_KEYS = ('Total', 'PWD', 'MM', 'OM')
GENDERS = ('M', 'F', 'TG')


def normalize_gender(raw: Any) -> str:
    if not raw:
        return 'M'  # Default to Male if not specified
    value = str(raw).strip().lower()
    if value.startswith('m'):
        return 'M'
    if value.startswith('f'):
        return 'F'
    if 'trans' in value or 'tg' in value:
        return 'TG'
    return 'M'  # Default to Male for unrecognized values


def compute_demographics_rows(students: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = {key: {cat: {'M': 0, 'F': 0, 'TG': 0} for cat in CATEGORIES} for key in ROW_KEYS}

    def inc(target_row: str, category: str, gender: str) -> None:
        if category not in CATEGORIES:
            category = 'General'
        rows[target_row][category][gender] += 1

    for s in students:
        raw_category = (s.get('category') or s.get('caste') or '')
        category = map_category(raw_category)
        gender = normalize_gender(s.get('gender'))
        caste_value = s.get('caste') or ''
        religion_value = s.get('religion') or ''

        inc('Total', category, gender)

        if any(is_pwd(value) for value in (raw_category, caste_value, religion_value)):
            inc('PWD', category, gender)
        if any(is_mm(value) for value in (raw_category, caste_value, religion_value)):
            inc('MM', category, gender)
        if any(is_om(value) for value in (raw_category, caste_value, religion_value)):
            inc('OM', category, gender)

    row_totals = {}
    for row_key, table in rows.items():
        m = sum(table[c]['M'] for c in CATEGORIES)
        f = sum(table[c]['F'] for c in CATEGORIES)
        tg = sum(table[c]['TG'] for c in CATEGORIES)
        row_totals[row_key] = {'M': m, 'F': f, 'TG': tg}
        rows[row_key]['TOTAL'] = {'M': m, 'F': f, 'TG': tg}

    specials = {
        'PWD': sum(rows['PWD'][c]['TG'] for c in CATEGORIES),
        'MM': sum(rows['MM'][c]['TG'] for c in CATEGORIES),
        'OM': sum(rows['OM'][c]['TG'] for c in CATEGORIES),
    }
    for row_key in row_totals:
        row_totals[row_key].update({'PWD': specials['PWD'], 'MM': specials['MM'], 'OM': specials['OM']})

    for row_key, table in rows.items():
        male_sum = sum(table[c]['M'] for c in CATEGORIES)
        female_sum = sum(table[c]['F'] for c in CATEGORIES)
        tg_sum = sum(table[c]['TG'] for c in CATEGORIES)
        assert row_totals[row_key]['M'] == male_sum, f"male total mismatch for {row_key}: {row_totals[row_key]['M']} != {male_sum}"
        assert row_totals[row_key]['F'] == female_sum, f"female total mismatch for {row_key}: {row_totals[row_key]['F']} != {female_sum}"
        assert row_totals[row_key]['TG'] == tg_sum, f"tg total mismatch for {row_key}: {row_totals[row_key]['TG']} != {tg_sum}"

    return {'rows': rows, 'row_totals': row_totals}


def validate_demographics(appeared: Dict[str, Any], passed: Dict[str, Any], passed_60: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    for row_key in ROW_KEYS:
        for category in CATEGORIES:
            appeared_total = appeared['rows'].get(row_key, {}).get(category, {}).get('TG', 0)
            passed_total = passed['rows'].get(row_key, {}).get(category, {}).get('TG', 0)
            passed_60_total = passed_60['rows'].get(row_key, {}).get(category, {}).get('TG', 0)

            if passed_total > appeared_total:
                errors.append(
                    f"Passed > Appeared for row={row_key} category={category} (passed={passed_total} appeared={appeared_total})"
                )
            if passed_60_total > passed_total:
                errors.append(
                    f"Passed>=60 > Passed for row={row_key} category={category} (>=60={passed_60_total} passed={passed_total})"
                )

        male_sum = sum(appeared['rows'].get(row_key, {}).get(category, {}).get('M', 0) for category in CATEGORIES)
        female_sum = sum(appeared['rows'].get(row_key, {}).get(category, {}).get('F', 0) for category in CATEGORIES)
        tg_sum = sum(appeared['rows'].get(row_key, {}).get(category, {}).get('TG', 0) for category in CATEGORIES)

        row_totals = appeared.get('row_totals', {}).get(row_key, {})
        if row_totals.get('M', 0) != male_sum:
            errors.append(f"Total male mismatch for row={row_key} (expected={male_sum} got={row_totals.get('M')})")
        if row_totals.get('F', 0) != female_sum:
            errors.append(f"Total female mismatch for row={row_key} (expected={female_sum} got={row_totals.get('F')})")
        if row_totals.get('TG', 0) != tg_sum:
            errors.append(f"Total TG mismatch for row={row_key} (expected={tg_sum} got={row_totals.get('TG')})")

    specials = {
        'PWD': sum(appeared['rows'].get('PWD', {}).get(category, {}).get('TG', 0) for category in CATEGORIES),
        'MM': sum(appeared['rows'].get('MM', {}).get(category, {}).get('TG', 0) for category in CATEGORIES),
        'OM': sum(appeared['rows'].get('OM', {}).get(category, {}).get('TG', 0) for category in CATEGORIES),
    }

    return {'valid': len(errors) == 0, 'errors': errors, 'specials': specials}
