import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from pypdf import PdfReader


@dataclass
class Subject:
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    cia: Optional[int] = None
    see: Optional[int] = None
    grace: Optional[int] = None
    max_marks: Optional[int] = None
    total_marks: Optional[int] = None
    credits: Optional[int] = None
    grade_point: Optional[float] = None
    credit_points: Optional[float] = None
    letter_grade: Optional[str] = None
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "cia": self.cia,
            "see": self.see,
            "grace": self.grace,
            "max_marks": self.max_marks,
            "total_marks": self.total_marks,
            "credits": self.credits,
            "grade_point": self.grade_point,
            "credit_points": self.credit_points,
            "letter_grade": self.letter_grade,
            "result": self.result,
        }


@dataclass
class Totals:
    cia_total: Optional[int] = None
    see_total: Optional[int] = None
    max_marks: Optional[int] = None
    total_marks: Optional[int] = None
    credits: Optional[int] = None
    credit_points: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cia_total": self.cia_total,
            "see_total": self.see_total,
            "max_marks": self.max_marks,
            "total_marks": self.total_marks,
            "credits": self.credits,
            "credit_points": self.credit_points,
        }


@dataclass
class Student:
    usn: Optional[str] = None
    student_name: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    sgpa: Optional[float] = None
    cgpa: Optional[float] = None
    overall_result: Optional[str] = None
    term_grade: Optional[str] = None
    marks_card_no: Optional[str] = None
    subjects: List[Subject] = field(default_factory=list)
    totals: Totals = field(default_factory=Totals)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student": {
                "usn": self.usn,
                "student_name": self.student_name,
                "father_name": self.father_name,
                "mother_name": self.mother_name,
                "sgpa": self.sgpa,
                "cgpa": self.cgpa,
                "overall_result": self.overall_result,
                "term_grade": self.term_grade,
                "marks_card_no": self.marks_card_no,
            },
            "subjects": [subject.to_dict() for subject in self.subjects],
            "totals": self.totals.to_dict(),
            "warnings": self.warnings,
        }


@dataclass
class PdfMetadata:
    program: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    exam_month: Optional[str] = None
    result_date: Optional[str] = None


@dataclass
class PdfParseResult:
    metadata: PdfMetadata = field(default_factory=PdfMetadata)
    students: List[Student] = field(default_factory=list)
    subject_master: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "program": self.metadata.program,
                "semester": self.metadata.semester,
                "academic_year": self.metadata.academic_year,
                "exam_month": self.metadata.exam_month,
                "result_date": self.metadata.result_date,
            },
            "students": [student.to_dict() for student in self.students],
            "subject_master": self.subject_master,
            "statistics": self.statistics,
            "warnings": self.warnings,
            "errors": self.errors,
        }


METADATA_PATTERNS = {
    "program": re.compile(r"Program\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "semester": re.compile(r"Semester\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "academic_year": re.compile(r"Academic Year\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "exam_month": re.compile(r"Exam Month\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "result_date": re.compile(r"(?:Result Date|Print Date)\s*[:\-]?\s*(.+)", re.IGNORECASE),
}

STUDENT_BLOCK_START = re.compile(r"^USN\s*[:\-]?\s*(U[0-9A-Za-z]{9,})", re.IGNORECASE)
FIELD_PATTERNS = {
    "student_name": re.compile(r"Student Name\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "father_name": re.compile(r"Father Name\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "mother_name": re.compile(r"Mother Name\s*[:\-]?\s*(.+)", re.IGNORECASE),
    "sgpa": re.compile(r"SGPA\s*[:\-]?\s*([0-9]+\.?[0-9]*)", re.IGNORECASE),
    "cgpa": re.compile(r"CGPA\s*[:\-]?\s*([0-9]+\.?[0-9]*)", re.IGNORECASE),
    "overall_result": re.compile(r"Result\s*[:\-]?\s*([A-Za-z\-]+)", re.IGNORECASE),
    "term_grade": re.compile(r"Term Grade\s*[:\-]?\s*([A-Za-z0-9\+\-]+)", re.IGNORECASE),
    "marks_card_no": re.compile(r"Marks card\s*No\s*[:\-]?\s*(\S+)", re.IGNORECASE),
}

SUBJECT_CODE_RE = re.compile(r"^(?=.*\d)[A-Z0-9/\- ]{5,40}$")
SUBJECT_CONTINUATION_RE = re.compile(r"^[A-Z0-9/\-]{1,40}$")
SUBJECT_SPLIT_RE = re.compile(r"\s{2,}")
TOTALS_START_RE = re.compile(r"^Total\b", re.IGNORECASE)


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages: List[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages.append(page_text)
    return "\n".join(pages)


def normalize_lines(text: str) -> List[str]:
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized: List[str] = []
    i = 0

    def is_field_start(line: str) -> bool:
        normalized_line = line.lower()
        return any(normalized_line.startswith(label.lower()) for label in [
            "usn",
            "student name",
            "father name",
            "mother name",
            "sgpa",
            "cgpa",
            "result",
            "term grade",
            "marks card",
            "total",
        ])

    while i < len(raw_lines):
        line = raw_lines[i]

        if line.lower() == "marks card" and i + 2 < len(raw_lines) and raw_lines[i + 1].lower().startswith("no"):
            normalized.append(f"Marks card No: {raw_lines[i + 2]}")
            i += 3
            continue

        if line.endswith(":") and i + 1 < len(raw_lines):
            next_line = raw_lines[i + 1]
            if not is_field_start(next_line) and not SUBJECT_CODE_RE.match(next_line) and not TOTALS_START_RE.match(next_line):
                normalized.append(f"{line} {next_line}")
                i += 2
                continue

        if SUBJECT_CODE_RE.match(line) and i + 1 < len(raw_lines):
            continuation = raw_lines[i + 1]
            if SUBJECT_CONTINUATION_RE.match(continuation) and any(ch.isdigit() for ch in continuation):
                if line.endswith("-"):
                    normalized.append(f"{line}{continuation}")
                else:
                    normalized.append(f"{line} {continuation}")
                i += 2
                continue

        if ":" in line and not line.endswith(":") and i + 1 < len(raw_lines):
            next_line = raw_lines[i + 1]
            if (
                not is_field_start(next_line)
                and next_line.isupper()
                and len(next_line.split()) <= 4
                and not SUBJECT_CODE_RE.match(next_line)
            ):
                normalized.append(f"{line} {next_line}")
                i += 2
                continue

        normalized.append(line)
        i += 1

    return normalized


def parse_metadata(text: str) -> PdfMetadata:
    metadata = PdfMetadata()
    normalized_text = "\n".join(normalize_lines(text))
    for key, pattern in METADATA_PATTERNS.items():
        match = pattern.search(normalized_text)
        if match:
            setattr(metadata, key, normalize_field_value(match.group(1)))
    return metadata


def split_student_blocks(text: str) -> List[str]:
    lines = normalize_lines(text)
    blocks: List[List[str]] = []
    current: List[str] = []

    for line in lines:
        if STUDENT_BLOCK_START.match(line):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)

    if current:
        blocks.append(current)
    return ["\n".join(block) for block in blocks]


def parse_subject_group(group_lines: List[str], warnings: List[str]) -> Subject:
    subject = Subject()
    if not group_lines:
        return subject

    subject.subject_code = group_lines[0].strip()
    idx = 1
    name_parts: List[str] = []

    while idx < len(group_lines) and not re.match(r"^[0-9]+\s*\+\s*[-0-9]*$", group_lines[idx].strip()):
        name_parts.append(group_lines[idx].strip())
        idx += 1

    subject.subject_name = " ".join(name_parts).strip() if name_parts else None

    marks_part = group_lines[idx].strip() if idx < len(group_lines) else ""
    marks_part = marks_part.replace("–", "-").replace("—", "-").replace("−", "-")
    idx += 1
    plus_match = re.match(r"^([0-9]+)\s*\+\s*([-0-9]*)$", marks_part)
    if plus_match:
        subject.cia = int(plus_match.group(1))
        see_raw = plus_match.group(2).strip()
        if see_raw == "":
            subject.see = None
        elif see_raw.isdigit():
            subject.see = int(see_raw)
        else:
            warnings.append(f"Unable to parse SEE from '{see_raw}' for subject {subject.subject_code}")
    else:
        if marks_part.strip() == "":
            subject.cia = None
            subject.see = None
        else:
            warnings.append(f"Unable to parse CIA+SEE from '{marks_part}' for subject {subject.subject_code}")

    if idx < len(group_lines) and group_lines[idx].strip().isdigit():
        subject.grace = int(group_lines[idx].strip())
        idx += 1

    if idx < len(group_lines) and group_lines[idx].strip().isdigit():
        subject.max_marks = int(group_lines[idx].strip())
        idx += 1

    if idx < len(group_lines) and group_lines[idx].strip().isdigit():
        subject.total_marks = int(group_lines[idx].strip())
        idx += 1

    if idx < len(group_lines) and group_lines[idx].strip().isdigit():
        subject.credits = int(group_lines[idx].strip())
        idx += 1

    if idx < len(group_lines) and re.match(r"^[0-9]+\.?[0-9]*$", group_lines[idx].strip()):
        subject.grade_point = float(group_lines[idx].strip())
        idx += 1

    if idx < len(group_lines) and re.match(r"^[0-9]+\.?[0-9]*$", group_lines[idx].strip()):
        subject.credit_points = float(group_lines[idx].strip())
        idx += 1

    if idx < len(group_lines):
        token = group_lines[idx].strip()
        if token.upper() in {"PASS", "FAIL", "FAILED", "RETEST"}:
            subject.result = token
            idx += 1
        else:
            subject.letter_grade = token
            idx += 1

    if idx < len(group_lines):
        token = group_lines[idx].strip()
        if token.upper() in {"PASS", "FAIL", "FAILED", "RETEST"}:
            subject.result = token
        elif subject.result is None and subject.letter_grade is None:
            subject.letter_grade = token

    return subject


def normalize_field_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned in {"", ":", "-", "NA", "N/A", "None"}:
        return None
    return cleaned


def is_likely_header_value(value: Optional[str]) -> bool:
    if not value:
        return False
    return bool(re.search(r"\b(UNIVERSITY|COLLEGE|EXAM|RESULT|SEMESTER|PROGRAM|YEAR|DATE|MARKS)\b", value, re.IGNORECASE))


def validate_student(student: Student, warnings: List[str]) -> None:
    if not student.usn:
        warnings.append("Missing USN")
    if not student.student_name:
        warnings.append(f"Missing student name for USN {student.usn or '<unknown>'}")
    if not student.subjects:
        warnings.append(f"No subjects parsed for USN {student.usn or '<unknown>'}")
    if student.totals.total_marks is None:
        warnings.append(f"Total marks missing for USN {student.usn or '<unknown>'}")
    if student.totals.credits is None:
        warnings.append(f"Total credits missing for USN {student.usn or '<unknown>'}")
    if not student.overall_result:
        warnings.append(f"Overall result missing for USN {student.usn or '<unknown>'}")


def extract_subjects(block_lines: List[str], warnings: List[str]) -> List[Subject]:
    subjects: List[Subject] = []
    current: List[str] = []

    for line in block_lines:
        if TOTALS_START_RE.match(line) or line.lower().startswith("marks card"):
            break

        if SUBJECT_CODE_RE.match(line):
            if current:
                parsed_subject = parse_subject_group(current, warnings)
                if parsed_subject.cia is not None or parsed_subject.see is not None:
                    subjects.append(parsed_subject)
            current = [line]
            continue

        if current:
            current.append(line)

    if current:
        parsed_subject = parse_subject_group(current, warnings)
        if parsed_subject.cia is not None or parsed_subject.see is not None:
            subjects.append(parsed_subject)

    return subjects


def extract_totals(block_lines: List[str]) -> Totals:
    totals = Totals()
    lines = block_lines
    for index, line in enumerate(lines):
        if TOTALS_START_RE.match(line):
            total_lines = lines[index + 1 : index + 7]
            if total_lines:
                plus_line = total_lines[0] if len(total_lines) > 0 else ""
                total_line_values = [val.strip() for val in plus_line.split("+")]
                if len(total_line_values) == 2 and all(val.isdigit() for val in total_line_values):
                    totals.cia_total = int(total_line_values[0])
                    totals.see_total = int(total_line_values[1])
                if len(total_lines) > 2 and total_lines[2].isdigit():
                    totals.max_marks = int(total_lines[2])
                if len(total_lines) > 3 and total_lines[3].isdigit():
                    totals.total_marks = int(total_lines[3])
                if len(total_lines) > 4 and total_lines[4].isdigit():
                    totals.credits = int(total_lines[4])
                elif len(total_lines) > 3 and total_lines[3].isdigit() and totals.credits is None:
                    totals.credits = int(total_lines[3])
                if len(total_lines) > 5 and re.match(r"^[0-9]+\.?[0-9]*$", total_lines[5]):
                    totals.credit_points = float(total_lines[5])
            break
    return totals


def parse_student_block(block: str, warnings: List[str]) -> Student:
    student = Student()
    student_warnings: List[str] = []
    lines = normalize_lines(block)

    for line in lines:
        for key, pattern in FIELD_PATTERNS.items():
            match = pattern.search(line)
            if match:
                value = normalize_field_value(match.group(1))
                if key in {"sgpa", "cgpa"}:
                    if value is None:
                        setattr(student, key, None)
                    else:
                        try:
                            setattr(student, key, float(value))
                        except ValueError:
                            student_warnings.append(f"Unable to parse {key}: {value}")
                else:
                    setattr(student, key, value)

    usn_match = STUDENT_BLOCK_START.search("\n".join(lines))
    if usn_match:
        student.usn = usn_match.group(1).strip()

    for key, pattern in FIELD_PATTERNS.items():
        if key == 'student_name':
            continue
        for line in lines:
            match = pattern.search(line)
            if match:
                value = normalize_field_value(match.group(1))
                if key in {'sgpa', 'cgpa'}:
                    if value is None:
                        setattr(student, key, None)
                    else:
                        try:
                            setattr(student, key, float(value))
                        except ValueError:
                            student_warnings.append(f"Unable to parse {key}: {value}")
                else:
                    setattr(student, key, value)

    candidate_names = []
    for line in lines:
        match = FIELD_PATTERNS['student_name'].search(line)
        if match:
            candidate_names.append(normalize_field_value(match.group(1)))

    valid_names = [name for name in candidate_names if name and not is_likely_header_value(name)]
    if valid_names:
        student.student_name = valid_names[0]
    else:
        for name in candidate_names:
            if name and not is_likely_header_value(name):
                student.student_name = name
                break

    if not student.student_name:
        # fallback: look for the first line after USN that is not a header or field label
        for idx, line in enumerate(lines):
            if STUDENT_BLOCK_START.match(line):
                for candidate in lines[idx + 1: idx + 8]:
                    if not candidate:
                        continue
                    if is_likely_header_value(candidate):
                        continue
                    if any(pattern.search(candidate) for pattern in FIELD_PATTERNS.values()):
                        continue
                    student.student_name = normalize_field_value(candidate)
                    break
                break

    subject_section_start = 0
    for idx, line in enumerate(lines):
        if SUBJECT_CODE_RE.match(line):
            subject_section_start = idx
            break

    student.subjects = extract_subjects(lines[subject_section_start:], student_warnings)
    student.totals = extract_totals(lines[subject_section_start:])

    if student.marks_card_no is None:
        card_match = re.search(r"Marks card\s*No\s*[:\-]?\s*(\S+)", "\n".join(lines), re.IGNORECASE)
        if card_match:
            student.marks_card_no = normalize_field_value(card_match.group(1))

    if student.mother_name is not None and student.mother_name == ":":
        student.mother_name = None

    validate_student(student, student_warnings)
    student.warnings = student_warnings
    warnings.extend(student_warnings)
    return student


def build_subject_master(students: List[Student]) -> List[Dict[str, Any]]:
    subject_map: Dict[str, Dict[str, Any]] = {}
    for student in students:
        for subject in student.subjects:
            if not subject.subject_code:
                continue
            code = subject.subject_code
            existing = subject_map.get(code)
            entry = {
                "code": code,
                "name": subject.subject_name,
                "max_marks": subject.max_marks,
                "credits": subject.credits,
            }
            if existing:
                if existing.get("name") != entry["name"] and entry["name"]:
                    existing["name"] = existing["name"] or entry["name"]
                if existing.get("max_marks") is None:
                    existing["max_marks"] = entry["max_marks"]
                if existing.get("credits") is None:
                    existing["credits"] = entry["credits"]
            else:
                subject_map[code] = entry
    return list(subject_map.values())


def normalize_program_name(program: Optional[str]) -> Optional[str]:
    if not program:
        return None

    cleaned = program.strip()
    if not cleaned:
        return None

    normalized = cleaned.lower()
    program_map = {
        'bachelor of computer applications': 'BCA',
        'bachelor of business administration': 'BBA',
        'bachelor of commerce': 'BCom',
        'bachelor of science': 'BSc',
        'bachelor of arts': 'BA',
        'bachelor of engineering': 'BE',
        'bachelor of technology': 'BTech',
    }
    if normalized in program_map:
        return program_map[normalized]

    acronym_match = re.fullmatch(r'[A-Z]{2,5}', cleaned)
    if acronym_match:
        return cleaned

    words = re.findall(r"\b[A-Za-z]+\b", cleaned)
    if words and words[0].lower() == 'bachelor':
        stopwords = {'of', 'and', 'the', 'in', 'for', 'with', 'science', 'commerce', 'technology', 'engineering', 'applications', 'administration', 'arts'}
        core_words = [word for word in words[1:] if word.lower() not in stopwords]
        if core_words:
            acronym = ''.join(word[0] for word in core_words if word)
            if 2 <= len(acronym) <= 4:
                return acronym.upper()

    return cleaned


def normalize_metadata(metadata: PdfMetadata) -> PdfMetadata:
    normalized = PdfMetadata(
        program=normalize_program_name(metadata.program),
        semester=(f"{metadata.semester.strip()} Semester" if metadata.semester and "semester" not in metadata.semester.lower() else metadata.semester),
        academic_year=metadata.academic_year,
        exam_month=(metadata.exam_month.title() if metadata.exam_month else None),
        result_date=metadata.result_date,
    )
    return normalized


def parse_pdf(pdf_path: str) -> PdfParseResult:
    result = PdfParseResult()
    raw_text = extract_text_from_pdf(pdf_path)
    metadata = parse_metadata(raw_text)
    result.metadata = normalize_metadata(metadata)

    blocks = split_student_blocks(raw_text)
    if not blocks:
        result.errors.append("No student blocks found")
        return result

    for block in blocks:
        student = parse_student_block(block, result.warnings)
        if student.usn:
            result.students.append(student)
        else:
            result.warnings.append("Skipped block with no USN")

    result.subject_master = build_subject_master(result.students)
    result.statistics = {
        "students_parsed": len(result.students),
        "subjects_detected": sum(len(student.subjects) for student in result.students),
        "unique_subjects": len(result.subject_master),
        "errors": len(result.errors),
        "warnings": len(result.warnings),
    }

    return result


def print_pdf_result(pdf_path: str, parsed: PdfParseResult) -> None:
    print("=" * 37)
    print("PDF METADATA")
    print("=" * 37)
    print()
    print(f"Program         : {parsed.metadata.program or ''}")
    print(f"Semester        : {parsed.metadata.semester or ''}")
    print(f"Academic Year   : {parsed.metadata.academic_year or ''}")
    print(f"Exam Month      : {parsed.metadata.exam_month or ''}")
    print(f"Result Date     : {parsed.metadata.result_date or ''}")
    print()

    for index, student in enumerate(parsed.students, start=1):
        print("=" * 40)
        print(f"STUDENT {index}")
        print("=" * 40)
        print()
        print(f"USN            : {student.usn or ''}")
        print()
        print(f"Student Name   : {student.student_name or ''}")
        print()
        print(f"Father Name    : {student.father_name or ''}")
        print()
        print(f"Mother Name    : {student.mother_name or ''}")
        print()
        print(f"SGPA           : {student.sgpa or ''}")
        print()
        print(f"CGPA           : {student.cgpa or ''}")
        print()
        print(f"Overall Result : {student.overall_result or ''}")
        print()
        print(f"Term Grade     : {student.term_grade or ''}")
        print()
        print(f"Marks Card No  : {student.marks_card_no or ''}")
        print()
        print(f"Subjects Found : {len(student.subjects)}")
        print()

        for subject_index, subject in enumerate(student.subjects, start=1):
            print("-" * 42)
            print(f"Subject {subject_index}")
            print()
            print(f"Code      : {subject.subject_code or ''}")
            print()
            print(f"Name      : {subject.subject_name or ''}")
            print()
            print(f"CIA       : {subject.cia_marks if subject.cia_marks is not None else ''}")
            print()
            print(f"SEE       : {subject.see_marks if subject.see_marks is not None else ''}")
            print()
            print(f"Grace     : {subject.grace if subject.grace is not None else ''}")
            print()
            print(f"Obtained  : {subject.obtained_marks if subject.obtained_marks is not None else ''}")
            print()
            print(f"Maximum   : {subject.maximum_marks if subject.maximum_marks is not None else ''}")
            print()
            print(f"Credits   : {subject.credits if subject.credits is not None else ''}")
            print()
            print(f"Grade Pt  : {subject.grade_point if subject.grade_point is not None else ''}")
            print()
            print(f"Credit Pt : {subject.credit_points if subject.credit_points is not None else ''}")
            print()
            print(f"Letter    : {subject.letter_grade or ''}")
            print()
            print(f"Result    : {subject.result or ''}")
            print()

        print("-" * 39)
        print()
        print("TOTALS")
        print()
        print(f"CIA Total        : {parsed.students[index-1].totals.cia_total or ''}")
        print(f"SEE Total        : {parsed.students[index-1].totals.see_total or ''}")
        print(f"Maximum Marks    : {parsed.students[index-1].totals.maximum_marks or ''}")
        print(f"Obtained Marks   : {parsed.students[index-1].totals.obtained_marks or ''}")
        print(f"Credits          : {parsed.students[index-1].totals.credits or ''}")
        print(f"Credit Points    : {parsed.students[index-1].totals.credit_points or ''}")
        print()

    print("=" * 34)
    print()
    print("PDF SUMMARY")
    print("=" * 34)
    print()
    all_subject_codes = {sub.subject_code for student in parsed.students for sub in student.subjects if sub.subject_code}
    print(f"Students Parsed : {len(parsed.students)}")
    print(f"Subjects Found  : {sum(len(student.subjects) for student in parsed.students)}")
    print(f"Unique Subjects : {len(all_subject_codes)}")
    print(f"Errors          : {len(parsed.errors)}")
    print()

    if parsed.warnings:
        print("Warnings:")
        for warning in parsed.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    import sys

    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "ledger.pdf"
    if not Path(pdf_file).exists():
        print(f"File not found: {pdf_file}")
        sys.exit(1)

    parsed = parse_pdf(pdf_file)
    print_pdf_result(pdf_file, parsed)
