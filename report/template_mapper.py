from __future__ import annotations

from typing import Any, Dict, List


class TemplateMapper:
    """Map normalized report data to placeholder-friendly structures for rendering."""

    def map(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        metadata = report_data.get('metadata', {}) or {}
        summary = report_data.get('summary', {}) or {}
        overall_summary = report_data.get('overall_summary', {}) or {}
        demographics = report_data.get('demographics') or {}
        subjects = report_data.get('subjects') or []
        toppers = report_data.get('toppers') or []
        centum = report_data.get('centum_achievers') or []

        return {
            'metadata': {
                'program': self._text(metadata.get('program')),
                'semester': self._text(metadata.get('semester')),
                'academic_year': self._text(metadata.get('academic_year')),
                'exam': self._text(metadata.get('exam')),
                'result_date': self._text(metadata.get('result_date')),
            },
            'overall_summary': overall_summary,
            'summary': {
                'appeared': self._text(summary.get('appeared')),
                'passed': self._text(summary.get('passed')),
                'failed': self._text(summary.get('failed')),
                'distinction': self._text(summary.get('distinction')),
                'first_class': self._text(summary.get('first_class')),
                'second_class': self._text(summary.get('second_class')),
                'pass_class': self._text(summary.get('pass_class')),
                'pass_percentage': self._text(summary.get('pass_percentage')),
            },
            'demographics': demographics,
            'subjects': self._normalize_rows(subjects),
            'toppers': self._normalize_rows(toppers),
            'centum_achievers': self._normalize_rows(centum),
        }

    def _normalize_rows(self, values: List[Any]) -> List[Dict[str, Any]]:
        if not isinstance(values, list):
            return []
        normalized: List[Dict[str, Any]] = []
        for item in values:
            if isinstance(item, dict):
                normalized.append({str(k): self._text(v) for k, v in item.items()})
        return normalized

    def _text(self, value: Any) -> Any:
        if value is None:
            return 'N/A'
        return value
