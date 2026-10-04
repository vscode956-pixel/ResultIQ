# Product Requirements Document (PRD)

# Result Engine — Multi-College Result Analysis SaaS
**Document Version:** 1.0
**Product Status:** Product definition / architecture stage
**Target:** B2B SaaS for colleges and academic institutions
**V1 University Support:** Bangalore University
**Primary Institution for Beta:** Soundarya Institute of Management & Science (SIMS)
**Primary Use Case:** Automating semester result analysis and official report generation

---

## 1. Executive Summary
**Result Engine** is a B2B SaaS platform that automates the process of converting university result/marks-ledger data into structured academic analysis and official college result-analysis reports.

The current system was originally designed around **Bangalore University marks-ledger PDFs + student master Excel files**. The supplied BU ledger demonstrates that the source contains college, program, semester, exam month, subject metadata, student USNs/names, CIA + SEE marks, total marks, credits, grade points, results, SGPA/CGPA and other academic information.     ExamResultLedgerA4 (1)

The product will evolve from a single-college utility into a **multi-tenant institutional SaaS platform**.

### Core transformation

```
CURRENT SYSTEM

PDF + Excel
     ↓
Parser
     ↓
Analysis
     ↓
DOCX/PDF Report

TARGET PRODUCT

College Organization
       ↓
User Login
       ↓
Create Result Analysis
       ↓
Upload University Ledger + Student Master
       ↓
Validate
       ↓
Parse
       ↓
Match Students
       ↓
Analyze
       ↓
Review
       ↓
Approve
       ↓
Generate Official Reports
       ↓
Store Result History
```

The most important product principle remains:

> **Accuracy is more important than visual polish.**
The existing project explicitly defines success as every statistic matching the official manual analysis, the generated report matching the approved template, processing supported semesters without code changes, and allowing a new user to generate a report in under five minutes.    plan

---

# 2. Problem Statement
Colleges currently spend significant manual effort converting university result data into institutional result-analysis reports.

Typical workflow:

```
University Result PDF
        +
College Student Master Excel
        ↓
Manual Data Extraction
        ↓
Student Matching
        ↓
Manual Calculations
        ↓
Subject-wise Analysis
        ↓
Class/Result Analysis
        ↓
Gender/Category Analysis
        ↓
Topper Identification
        ↓
Centum Identification
        ↓
Report Preparation
        ↓
Manual Verification
        ↓
Word/PDF Report
```

This creates several problems:

### 2.1 Manual calculation errors
A single incorrect count can make an official report unreliable.

### 2.2 Repetitive work
The same analysis must be repeated every semester.

### 2.3 PDF complexity
University ledgers are structured for human reading rather than direct database ingestion.

For example, the BU ledger contains different subject types and maximum marks, including 100-mark theory subjects and 50-mark practical/lab subjects.     ExamResultLedgerA4 (1)

### 2.4 Student matching
The ledger and college master may contain different information structures.

The system therefore needs reliable matching using identifiers such as USN.

### 2.5 Report formatting
Academic departments often require a specific official report structure.

### 2.6 Lack of historical system
A traditional script produces a report but does not provide:

- previous result history
- organization management
- user management
- auditability
- report retrieval
- role-based access
- usage tracking

---

# 3. Product Vision

### Vision

> **Become the academic result-analysis infrastructure used by colleges to transform university result data into accurate, reviewable and institution-ready academic intelligence.**
The product should eventually support:

- multiple colleges
- multiple users per college
- multiple programs
- multiple semesters
- multiple academic years
- multiple result analyses
- report history
- organization branding
- role-based access
- subscription plans
- university-specific adapters

---

# 4. Product Positioning
Result Engine is **not simply a PDF parser**.

It is:

> **A result-analysis workflow platform for academic institutions.**
The PDF parser is only one component.

### Product layers

```
┌─────────────────────────────────────────────┐
│              SaaS PLATFORM                  │
│                                             │
│ Auth │ Organizations │ Users │ Roles        │
│ Plans │ Usage │ Dashboard │ History         │
│ Reports │ Settings │ Security               │
├─────────────────────────────────────────────┤
│          RESULT ANALYSIS ENGINE             │
│                                             │
│ Validation                                  │
│ PDF Parsing                                 │
│ Excel Parsing                               │
│ Student Matching                            │
│ Analysis                                    │
│ Review                                      │
│ Report Generation                            │
├─────────────────────────────────────────────┤
│        UNIVERSITY ADAPTER LAYER             │
│                                             │
│ Bangalore University V1                     │
│ Future: Other Universities                  │
└─────────────────────────────────────────────┘
```

---

# 5. Goals

## 5.1 Primary Goals

1. Automate semester result analysis.
2. Reduce manual calculation work.
3. Produce highly accurate academic statistics.
4. Generate official DOCX/PDF reports.
5. Support multiple colleges.
6. Provide organization-specific branding.
7. Provide secure user authentication.
8. Provide role-based access.
9. Maintain result-analysis history.
10. Make the architecture extensible to other universities.

---

# 6. Non-Goals for V1
The following should **not** become distractions during the first production release:

- AI-generated academic predictions
- student performance prediction
- attendance management
- fee management
- LMS
- timetable management
- examination scheduling
- ERP replacement
- mobile application
- complicated analytics/BI platform
- public student portal
The product should first become excellent at:

> **PDF + Excel → Accurate Result Analysis → Verified Report**

---

# 7. Target Customers

## Primary Customer
Colleges and academic institutions that conduct result analysis after university examinations.

### Example

```
Soundarya Institute of Management & Science
        ↓
BCA Department
        ↓
Semester II
        ↓
Bangalore University
```

The current real-world ledger is from Soundarya Institute of Management & Science for Bachelor of Computer Applications, Semester II, June/July 2025.     ExamResultLedgerA4 (1)

---

# 8. Target Users

## 8.1 Super Admin
Platform owner.

Can manage:

- organizations
- users
- plans
- access requests
- platform configuration
- system health
- organization status
- usage

---

## 8.2 Organization Admin
College-level administrator.

Can:

- manage organization profile
- manage users
- create result analyses
- view reports
- configure branding
- view history

---

## 8.3 Examination Coordinator
Responsible for result processing.

Can:

- create analysis
- upload files
- validate data
- review analysis
- approve analysis
- generate reports
- download reports

---

## 8.4 Faculty
Can:

- view assigned/available results
- inspect analysis
- view subject statistics
- view student performance
- download authorized reports

---

## 8.5 Viewer
Read-only access.

Can:

- view approved analyses
- view reports
- download authorized reports
Cannot:

- upload
- modify
- approve
- delete

---

# 9. Account Creation Strategy

## V1: Controlled Access
Do **not** launch with unrestricted public signup.

Recommended workflow:

```
College wants Result Engine
          ↓
Request Access
          ↓
Super Admin reviews request
          ↓
Organization created
          ↓
Organization Admin created
          ↓
Activation email/link
          ↓
Admin sets password
          ↓
Admin logs in
```

This prevents uncontrolled account creation and makes the initial SaaS easier to manage.

---

# 10. Multi-Tenant Architecture
Every college is an **Organization/Tenant**.

Example:

```
Result Engine
│
├── SIMS
│   ├── Admin
│   ├── Exam Coordinator
│   └── Faculty
│
├── College B
│   ├── Admin
│   └── Faculty
│
└── College C
    └── Admin
```

### Critical rule
One organization must never be able to access another organization's:

- users
- students
- result analyses
- reports
- files
- configuration
Every major database entity should therefore contain:

```
organization_id
```

where applicable.

---

# 11. Organization Profile
Each organization should have configurable:

```
Organization
├── id
├── name
├── short_name
├── logo
├── university
├── address
├── city
├── state
├── country
├── contact_email
├── contact_phone
├── website
├── active
├── created_at
└── updated_at
```

### Why?
The current application contains college-specific branding such as SIMS.

That must be removed from hardcoded frontend logic.

Instead:

```
Backend
   ↓
Organization Configuration
   ↓
Frontend
   ↓
Header
Sidebar
Dashboard
Reports
DOCX
PDF
```

---

# 12. University Architecture
V1 supports:

> **Bangalore University**
But the system should not hardcode BU logic throughout the application.

Use an adapter architecture:

```
UniversityAdapter
       │
       ├── BangaloreUniversityAdapter
       │
       ├── FutureUniversityAdapter
       │
       └── FutureUniversityAdapter
```

Example:

```
University
    ↓
Parser
    ↓
Normalized Result Data
    ↓
Common Analysis Engine
```

This means the analysis engine does not care whether the input came from BU or another university.

---

# 13. Core Input
V1 requires two main files:

### 1. University Marks Ledger PDF
Example BU ledger structure includes:

- University
- College
- Program
- Semester
- Exam month
- Subject code
- Subject name
- Course type
- CIA
- SEE
- Total
- Minimum marks
- Maximum marks
    ExamResultLedgerA4 (1)

### 2. Student Master Excel
Contains institutional/student metadata such as:

```
USN
Student Name
Gender
Category
Caste
```

Additional columns may be supported later.

---

# 14. Result Metadata
Before processing, user enters/selects:

```
Program
Semester
Academic Year
Exam Month
Result Date
Section(s)
Faculty Name(s)
```

Existing project requirements already identify these as report metadata.    plan

---

# 15. Result Analysis Lifecycle
The central workflow should be:

```
DRAFT
  ↓
UPLOADING
  ↓
VALIDATING
  ↓
PARSING
  ↓
MATCHING
  ↓
ANALYZING
  ↓
REVIEW_REQUIRED
  ↓
APPROVED
  ↓
REPORT_GENERATED
```

Possible failure:

```
VALIDATION_FAILED
PARSING_FAILED
MATCHING_FAILED
ANALYSIS_FAILED
REPORT_FAILED
```

---

# 16. Step 1 — Create Result
User selects:

```
Program: BCA
Semester: II
Academic Year: 2024-25
Exam Month: June/July 2025
Result Date: ...
```

System creates:

```
ResultAnalysis
status = DRAFT
```

---

# 17. Step 2 — Upload Files
Upload:

```
Marks Ledger PDF
Student Master XLSX
```

UI should clearly show:

```
✓ PDF uploaded
✓ Excel uploaded
```

File requirements should be displayed before upload.

---

# 18. Step 3 — File Validation

## PDF Validation
Check:

- extension
- MIME type
- file size
- readability
- page count
- expected university
- expected college if configured
- program
- semester
- subject structure
- required fields
The existing specification already requires correct PDF format, size and readability validation.    plan

---

## Excel Validation
Check:

- valid XLSX
- required columns
- duplicate USNs
- blank USNs
- missing gender
- missing category
- malformed records
Existing requirements explicitly include required columns, duplicate USN detection, and gender/category validation.    plan

---

# 19. Step 4 — PDF Parsing
The parser converts the university ledger into normalized structured data.

Example:

```
{
  "usn": "U03KU24S0054",
  "student_name": "Harshitha R",
  "result": "PASS",
  "sgpa": 7.15,
  "cgpa": 7.07,
  "subjects": []
}
```

The ledger demonstrates student-level fields such as USN, student name, SGPA, CGPA, result and subject marks.     ExamResultLedgerA4 (1)

---

# 20. Subject Data Model
Normalized subject:

```
Subject
├── code
├── name
├── course_type
├── cia_marks
├── see_marks
├── grace_marks
├── total_marks
├── maximum_marks
├── minimum_marks
├── credits
├── grade_point
├── credit_points
├── letter_grade
├── result
├── absent
└── centum
```

The BU ledger explicitly contains CIA + SEE, grace, maximum/total marks, credits, grade points, credit points, letter grade and result fields.     ExamResultLedgerA4 (1)

---

# 21. Step 5 — Excel Parsing
Excel is converted into:

```
StudentMaster[]
```

Example:

```
{
  "usn": "U03KU24S0054",
  "gender": "Female",
  "category": "..."
}
```

---

# 22. Step 6 — Student Matching
Primary key:

```
USN
```

Process:

```
PDF Students
      +
Excel Students
      ↓
USN Matching
      ↓
Matched
Unmatched PDF
Unmatched Excel
```

### Matching result
Example:

```
Students in PDF: 65
Students in Excel: 67

Matched: 64
PDF unmatched: 1
Excel unmatched: 3
```

The UI should never hide mismatches.

---

# 23. Matching Rules

### Exact match

```
normalized_pdf_usn == normalized_excel_usn
```

Normalization may include:

- trim whitespace
- uppercase
- remove accidental spaces

### Never silently fuzzy-match USNs.
If an identifier is ambiguous:

```
REVIEW REQUIRED
```

This is critical because a wrong student match can corrupt demographic and result analysis.

---

# 24. Step 7 — Analysis Engine
The analysis engine must remain independent from:

- PDF parser
- Excel parser
- UI
- report generator
Architecture:

```
Normalized Students
        ↓
 ┌──────┼────────┬────────┬────────┐
 ↓      ↓        ↓        ↓        ↓
Summary Topper Subject  Demographic Centum
        Analysis Analysis Analysis
```

The existing design explicitly separates these analysis services and prevents the report generator from directly handling PDF parsing.    plan

---

# 25. Overall Summary
The system should calculate:

- Appeared
- Passed
- Failed
- Distinction
- First Class
- Second Class
- Pass Class
- Pass Percentage
Current project specification defines these categories as core report outputs.    plan

### Important
The classification rules currently present in the implementation are **not yet confirmed as official Bangalore University rules**.

Therefore:

> These rules must be verified against the college's approved manual result-analysis report before being treated as production truth.

---

# 26. Result Classification
Current implementation logic uses approximately:

```
85%+  → Distinction
60%+  → First Class
50%+  → Second Class
40%+  → Pass Class
<40%  → Fail
```

Explicit:

```
FAIL
FAILED
RETEST
```

should override percentage-based classification.

### Product requirement
Do not permanently hardcode these thresholds.

Instead:

```
ResultRuleSet
```

should eventually contain:

```
pass_percentage
distinction_percentage
first_class_percentage
second_class_percentage
```

This allows university/program-specific rules later.

---

# 27. Subject Analysis
For every subject:

```
Subject Code
Subject Name
Appeared
Passed
Failed
Absent
Pass %
Topper Marks
Centum Count
```

The original project identifies passed, failed, absent, centum, pass percentage and topper marks as required subject statistics.    plan

---

# 28. Subject Pass Percentage
Current implementation uses:

```
Passed / (Passed + Failed) × 100
```

with absent/missing marks excluded from the denominator.

### Important
This is another rule that must be verified against the approved institutional report before being declared the official calculation rule.

---

# 29. Top Performers
The system should identify:

```
Rank
Student Name
USN
Total Marks
Percentage
```

Example:

```
1. Student A — 565/700 — 80.71%
2. Student B — 560/700 — 80.00%
3. Student C — 552/700 — 78.86%
```

The current engine sorts by total marks and allows tied students to share the same rank.

---

# 30. Subject Toppers
For each subject:

```
Subject
Topper
USN
Marks
Maximum Marks
Percentage
```

Example BU data demonstrates student subject totals and maximum marks directly in the ledger.     ExamResultLedgerA4 (1)

---

# 31. Centum Analysis
Detect:

```
Obtained Marks == Maximum Marks
```

Output:

```
Subject
Student
USN
Marks
```

Example:

A student record in the ledger contains 50/50 in multiple lab subjects, demonstrating why centum detection needs to work for both 100-mark and 50-mark subjects.     ExamResultLedgerA4 (1)

---

# 32. Demographic Analysis
Using the student master:

### Gender

```
Male
Female
Other/Unknown
```

For each:

```
Appeared
Passed
Failed
Pass %
```

### Category

```
Category
Appeared
Passed
Failed
Pass %
```

Potential future:

```
60%+
Distinction
First Class
```

The original project already identifies category-wise and gender-wise analysis as part of demographics.

---

# 33. Student-Level Result
Every student should have:

```
USN
Name
Gender
Category
Subjects
Total Marks
Maximum Marks
Percentage
Result
Division/Class
SGPA
CGPA
```

The existing student model already defines USN, name, gender, category, caste, subjects, total marks, percentage, result and division.    plan

---

# 34. Review Screen
This is one of the most important additions to the SaaS version.

Before report generation:

```
                 RESULT REVIEW

Students detected      67
Students matched       65
Unmatched               2
Subjects                9
Passed                 51
Failed                 14
Warnings                3

[ View Students ]

[ View Subject Analysis ]

[ View Warnings ]

[ Approve Analysis ]
```

---

# 35. Warnings
Examples:

```
⚠ 2 students could not be matched.

⚠ 1 student has missing category.

⚠ 3 students contain absent subjects.

⚠ PDF contains an unexpected subject code.

⚠ Student count differs between PDF and Excel.
```

Warnings should not necessarily block processing.

Critical errors should.

---

# 36. Approval
Only authorized roles should approve.

Workflow:

```
Analysis generated
      ↓
Review
      ↓
Coordinator verifies
      ↓
Approve
      ↓
Report generation enabled
```

This creates an important control point.

---

# 37. Report Generation
Output formats:

### DOCX
Official editable report.

### PDF
Official final/shareable report.

Existing requirements explicitly define DOCX and PDF generation and require verification against the approved report template.    plan

---

# 38. Report Generator Architecture
Report generator receives:

```
AnalysisResult
```

containing:

```
summary
toppers
subjects
demographics
centum
metadata
```

It should not know anything about:

- PDF extraction
- Excel parsing
- HTTP
- authentication
This separation already exists in the original architecture and should be preserved.    plan

---

# 39. Report Branding
Reports should dynamically use organization settings.

```
Organization Logo
Organization Name
University
Address
Program
Semester
Academic Year
Exam Month
```

Instead of:

```
RESULT ENGINE SIMS
```

hardcoded everywhere.

---

# 40. Report History
Each completed analysis becomes a permanent record.

Example:

```
2025-26
BCA
Semester II
June/July
Approved
PDF
DOCX
```

Users can open:

```
Result History
    ↓
Result Details
    ↓
Analysis
    ↓
Download Report
```

---

# 41. Dashboard
Organization dashboard:

```
┌───────────────────────────────────────────────┐
│ Good Morning, Exam Coordinator               │
├───────────────────────────────────────────────┤
│                                               │
│ Total Analyses        12                      │
│ Reports Generated     10                      │
│ Students Analysed   1,248                    │
│                                               │
├───────────────────────────────────────────────┤
│ Recent Results                                │
│                                               │
│ BCA Sem II       Approved                     │
│ BCA Sem I        Approved                     │
│ BBA Sem IV       Processing                   │
└───────────────────────────────────────────────┘
```

---

# 42. Organization Dashboard Modules
Recommended navigation:

```
Dashboard

Results
├── All Results
├── Create Analysis
└── Drafts

Reports
├── Generated Reports
└── Templates

Students
└── Student Records

Programs
└── Programs

Users
└── Organization Users

Settings
├── Organization
├── Branding
└── Preferences
```

---

# 43. Super Admin Dashboard
Platform-level dashboard:

```
Organizations
Users
Active Analyses
Reports Generated
System Health
Plans
Usage
Access Requests
```

Example:

```
Organizations             12
Active Organizations       9
Users                     48
Analyses                 137
Reports                  121
```

---

# 44. Super Admin — Organizations
Super Admin can:

- create organization
- deactivate organization
- edit organization
- view organization
- assign plan
- view usage
- manage primary admin
Organization status:

```
ACTIVE
SUSPENDED
TRIAL
EXPIRED
ARCHIVED
```

---

# 45. Super Admin — Access Requests
Request form:

```
Name
Official Email
Phone
College
Designation
Department
University
Reason
```

Admin actions:

```
Approve
Reject
Request More Information
```

---

# 46. User Management
Organization Admin:

```
Invite User
Deactivate User
Change Role
Reset Access
```

Roles:

```
ORG_ADMIN
EXAM_COORDINATOR
FACULTY
VIEWER
```

Platform:

```
SUPER_ADMIN
```

---

# 47. Authentication
Required:

- secure password hashing
- login
- logout
- session/token handling
- password reset
- account activation
- role-based authorization
- organization isolation
Never store plain-text passwords.

---

# 48. Authorization Model
Example:

FeatureSuper AdminOrg AdminCoordinatorFacultyViewerManage organizations✓————Manage users✓✓———Create analysis✓✓✓optional—Upload files✓✓✓optional—Review✓✓✓optional—Approve✓✓✓——Reports✓✓✓✓✓Organization settings✓✓———

---

# 49. Database
Recommended:

> **PostgreSQL**
Database stores structured information.

### Core tables

```
organizations
users
roles
organization_users
plans
subscriptions
usage_records

programs
students
student_master_records

result_analyses
result_students
result_subjects
result_statistics

reports
report_templates

access_requests

audit_logs
```

---

# 50. Organization Schema

```
organizations
----------------
id
name
short_name
logo_url
university_id
address
city
state
country
email
phone
website
status
created_at
updated_at
```

---

# 51. User Schema

```
users
----------------
id
name
email
password_hash
status
last_login_at
created_at
updated_at
```

Organization membership:

```
organization_users
----------------
id
organization_id
user_id
role
status
created_at
```

This supports one user potentially belonging to multiple organizations later.

---

# 52. Result Analysis Schema

```
result_analyses
----------------
id
organization_id
program_id
semester
academic_year
exam_month
result_date
university
status
student_count
passed_count
failed_count
created_by
approved_by
approved_at
created_at
updated_at
```

---

# 53. Report Schema

```
reports
----------------
id
organization_id
result_analysis_id
report_type
file_name
file_path
file_size
version
generated_by
generated_at
```

Types:

```
DOCX
PDF
```

---

# 54. File Storage Strategy
Do **not** use PostgreSQL as a PDF file store.

### Temporary input

```
PDF
Excel
   ↓
Temporary storage
   ↓
Processing
   ↓
Delete
```

### Persistent output

```
Generated PDF
Generated DOCX
       ↓
Object/File Storage
```

Database stores only metadata/reference.

---

# 55. Raw Data Retention
V1 recommended:

### Uploaded PDF
Temporary.

### Uploaded Excel
Temporary.

### Parsed structured analysis
Persistent.

### Generated reports
Persistent.

This provides useful history without unnecessarily storing sensitive source files.

---

# 56. Plans
Plans belong to the **organization**, not individual users.

Example:

```
Evaluation
Standard
Institution
Enterprise
```

The system should not hardcode:

```
if (plan === "standard") ...
```

throughout the frontend.

Instead:

```
Plan
 ↓
Entitlements
 ↓
Usage Service
 ↓
Feature Access
```

---

# 57. Example Entitlements
Possible configuration:

```
max_analyses
max_students_per_analysis
report_formats
history_retention
users_allowed
programs_allowed
support_level
```

Exact commercial limits should be finalized after beta usage data.

---

# 58. Evaluation Plan
Recommended:

> One-time organization-level evaluation rather than unlimited recurring free trials.
For example:

```
Evaluation
2 analyses
```

not:

```
2 analyses per user per month
```

This reduces trial abuse.

---

# 59. Usage Tracking
Track:

```
organization_id
analysis_id
user_id
event_type
students_processed
timestamp
```

Example events:

```
ANALYSIS_CREATED
ANALYSIS_COMPLETED
REPORT_GENERATED
PDF_GENERATED
DOCX_GENERATED
```

---

# 60. Audit Logging
For institutional software, important actions should be recorded.

Example:

```
User
Action
Organization
Resource
Timestamp
IP/device metadata if appropriate
```

Examples:

```
Admin approved result analysis
Coordinator generated PDF
Admin changed organization branding
User downloaded report
```

---

# 61. API Architecture
Current API:

```
POST /api/v1/upload
POST /api/v1/report/docx
POST /api/v1/report/pdf
GET  /health
```

These should evolve into a versioned SaaS API.

---

# 62. Proposed API Structure

```
/api/v1/auth
/api/v1/organizations
/api/v1/users
/api/v1/programs
/api/v1/results
/api/v1/analyses
/api/v1/reports
/api/v1/dashboard
/api/v1/plans
/api/v1/usage
/api/v1/admin
```

---

# 63. Result APIs

### Create

```
POST /api/v1/results
```

### Upload

```
POST /api/v1/results/{id}/files
```

### Validate

```
POST /api/v1/results/{id}/validate
```

### Analyze

```
POST /api/v1/results/{id}/analyze
```

### Review

```
GET /api/v1/results/{id}/review
```

### Approve

```
POST /api/v1/results/{id}/approve
```

### Generate report

```
POST /api/v1/results/{id}/reports
```

---

# 64. Frontend Architecture
Recommended:

```
React
TypeScript
Vite
TailwindCSS
shadcn/ui
React Hook Form
Zod
Axios
```

Existing project architecture already uses a React/Vite-style frontend with dedicated components, services, hooks and pages.    plan

---

# 65. Backend Architecture
Recommended:

```
FastAPI
Python 3.12
Pydantic
PostgreSQL
SQLAlchemy
Alembic
pdfplumber
Pandas
openpyxl
python-docx
```

Existing system already uses FastAPI/Python, PDF parsing, Pandas/openpyxl and python-docx as the foundation.

---

# 66. Backend Module Structure

```
backend/
│
├── app/
│   ├── api/
│   │   ├── auth/
│   │   ├── organizations/
│   │   ├── users/
│   │   ├── results/
│   │   ├── reports/
│   │   └── admin/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── permissions.py
│   │
│   ├── db/
│   │   ├── models/
│   │   ├── session.py
│   │   └── migrations/
│   │
│   ├── services/
│   │   ├── result/
│   │   ├── parser/
│   │   ├── analysis/
│   │   ├── reports/
│   │   └── storage/
│   │
│   ├── universities/
│   │   └── bangalore_university/
│   │
│   └── main.py
```

---

# 67. University Adapter
Example:

```
class UniversityAdapter:
    def validate_pdf(self):
        pass

    def extract_metadata(self):
        pass

    def extract_students(self):
        pass

    def extract_subjects(self):
        pass
```

Then:

```
BangaloreUniversityAdapter
```

implements BU-specific parsing.

---

# 68. Analysis Engine

```
analysis/
├── summary.py
├── toppers.py
├── subjects.py
├── demographics.py
├── centum.py
├── classification.py
└── engine.py
```

The analysis engine receives normalized data:

```
NormalizedStudent[]
```

not raw PDF text.

---

# 69. Report Engine

```
reports/
├── docx/
├── pdf/
├── templates/
├── renderer.py
└── service.py
```

Report engine receives:

```
AnalysisResult
```

---

# 70. UI — Login
Professional SaaS login:

```
┌──────────────────────────────┐
│       RESULT ENGINE          │
│                              │
│   Sign in to your account    │
│                              │
│   Email                      │
│   [____________________]     │
│                              │
│   Password                   │
│   [____________________]     │
│                              │
│   [ Sign In ]                │
│                              │
│   Forgot Password?           │
│                              │
│   Need access? Request →     │
└──────────────────────────────┘
```

---

# 71. UI — Dashboard
The dashboard should not immediately throw the user into a giant upload form.

Instead:

```
Dashboard
   ↓
Recent analyses
   ↓
Create New Analysis
```

This makes it feel like a SaaS product rather than a script wrapper.

---

# 72. UI — Create Analysis
Wizard:

```
1. Details
2. Upload
3. Validation
4. Matching
5. Analysis
6. Review
7. Approve
8. Report
```

Progress indicator:

```
✓ Details
✓ Upload
✓ Validation
● Analysis
○ Review
○ Report
```

---

# 73. UI — Validation
Example:

```
Validation Complete

✓ PDF readable
✓ Bangalore University detected
✓ Program detected: BCA
✓ Semester detected: II
✓ 67 pages detected
✓ Excel valid
✓ No duplicate USNs

Warnings: 2
```

---

# 74. UI — Matching

```
Student Matching

PDF Students       67
Excel Students     67

Matched            65
Unmatched PDF       2
Unmatched Excel     2

[ Review Matches ]
```

---

# 75. UI — Analysis Review
Sections:

```
Overview
Students
Subjects
Toppers
Demographics
Centum
Warnings
```

---

# 76. UI — Reports

```
Generated Reports

BCA Sem II
June/July 2025

PDF     Download
DOCX    Download
```

---

# 77. Error Handling
Never show:

```
Internal Server Error
```

to the user when a meaningful error is available.

Instead:

```
PDF format not supported.
```

```
Excel missing Gender column.
```

```
Duplicate USN found: U03KU24S0126
```

```
Unable to match 3 students.
```

These examples are directly aligned with the existing project specification.    plan

---

# 78. Error Categories

```
FILE_ERROR
VALIDATION_ERROR
PARSER_ERROR
MATCHING_ERROR
ANALYSIS_ERROR
REPORT_ERROR
AUTH_ERROR
PERMISSION_ERROR
STORAGE_ERROR
SYSTEM_ERROR
```

Each should have:

```
code
message
details
user_action
```

---

# 79. Security Requirements
Minimum:

- password hashing
- secure authentication
- authorization middleware
- tenant isolation
- input validation
- file type validation
- file size limits
- temporary file cleanup
- secure report downloads
- database constraints
- audit logging
- environment secrets
- HTTPS in production

---

# 80. Tenant Isolation
Every request must establish:

```
authenticated_user
        ↓
organization_id
        ↓
resource.organization_id
        ↓
authorize
```

Never trust:

```
organization_id
```

sent directly from the frontend.

---

# 81. File Security
Uploaded files should be treated as untrusted.

Validate:

```
Extension
MIME
Size
Readable structure
Expected format
```

Do not execute uploaded files.

Use random temporary filenames.

Delete temporary inputs after successful processing.

---

# 82. Performance Requirements
Target:

### Normal analysis

```
≤ 5 minutes
```

from upload to generated report for a typical supported college result.

The existing success criteria explicitly targets report generation in under five minutes.    plan

### UI
Normal API operations:

```
< 2 seconds
```

where practical.

Long-running processing should show progress rather than appearing frozen.

---

# 83. Scalability
V1 can use synchronous/background processing depending on actual processing time.

If workloads increase:

```
FastAPI
   ↓
Job Queue
   ↓
Worker
   ↓
PDF Parser
   ↓
Analysis
   ↓
Report Generator
```

Potential future:

```
Redis
Celery/RQ
```

But this should not be added prematurely.

---

# 84. Deployment
Initial architecture:

```
Frontend
   ↓
Netlify / equivalent

Backend
   ↓
Render / equivalent

Database
   ↓
Managed PostgreSQL

File Storage
   ↓
Object Storage
```

The original deployment plan uses Netlify for frontend and Render for backend.    plan

---

# 85. Development Infrastructure
Early development/beta can use low-cost/free infrastructure.

However:

> Free infrastructure should be treated as an early-stage strategy, not the permanent production architecture.
The PDF parser and report generator are computationally heavier than a basic CRUD SaaS.

---

# 86. Observability
System should log:

```
Request
User
Organization
Analysis ID
Processing stage
Duration
Error
File size
Student count
Report generation time
```

Example:

```
Analysis: RA-2026-0012
Stage: PDF_PARSE
Duration: 8.42s
Students: 67
Status: SUCCESS
```

---

# 87. Testing Strategy
This is arguably the most important engineering requirement.

## Unit Tests
Test:

- USN normalization
- matching
- classification
- pass percentage
- topper ranking
- centum
- demographic calculations

---

# 88. Parser Tests
Use known BU ledger samples.

Verify:

```
Student count
USNs
Names
Subjects
Marks
Results
SGPA
CGPA
```

The supplied BU ledger contains 67 pages and multiple student records with different pass/fail/absent scenarios, making it useful as a real-world parser test source.     ExamResultLedgerA4 (1)

---

# 89. Golden Dataset
Create a manually verified dataset:

```
golden_students.json
golden_subjects.json
golden_analysis.json
```

Expected:

```
students = X
passed = X
failed = X
distinction = X
first_class = X
...
```

Then:

```
Actual == Expected
```

must pass.

---

# 90. End-to-End Test
The most important test:

```
67-page BU PDF
       +
Student Master Excel
       ↓
System
       ↓
Analysis
       ↓
Official report
```

Then compare every important output with the manually verified report.

The existing project explicitly recommends reaching a point where the full PDF + Excel flow produces correct students, correct statistics and the correct official report before adding SaaS complexity.    Pasted markdown(20261003-085003)

---

# 91. Acceptance Criteria
A result analysis is successful only when:

```
PDF valid
AND
Excel valid
AND
Students matched
AND
No critical warnings
AND
Analysis completed
AND
Review approved
AND
Report generated
```

---

# 92. Product-Level Success Criteria
V1 is successful when:

### Accuracy
Every approved statistic matches the verified manual result analysis.

### Usability
A trained college user can complete an analysis without developer assistance.

### Speed
Typical report generated within five minutes.

### Reliability
Repeated processing of the same inputs produces the same results.

### Multi-tenancy
College A cannot access College B.

### Reporting
DOCX and PDF reports are correctly generated.

### Extensibility
Adding a new university does not require rewriting the SaaS layer.

---

# 93. Auditability
Every report should be traceable:

```
Report
 ↓
Result Analysis
 ↓
Input metadata
 ↓
User who created it
 ↓
User who approved it
 ↓
Calculation version
```

Recommended:

```
analysis_engine_version
parser_version
rule_set_version
```

This becomes extremely important if the product is later used commercially.

---

# 94. Calculation Versioning
Do not simply store:

```
percentage = 62.5
```

Store the context/rule version as well.

Example:

```
analysis_engine_version = 1.2.0
rule_set_version = BU-2025-v1
```

If calculation rules change later, old reports remain reproducible.

---

# 95. Report Versioning
If a report is regenerated:

```
Report v1
Report v2
```

Do not silently overwrite an approved report.

Example:

```
BCA Sem II Result Analysis
v1 — Generated
v2 — Regenerated after correction
```

---

# 96. Correction Workflow
If an error is discovered:

```
Approved
   ↓
Correction requested
   ↓
Create new analysis version
   ↓
Reprocess
   ↓
Review
   ↓
Approve
```

Avoid editing historical statistics directly.

---

# 97. Data Model Relationship

```
Organization
     │
     ├── Users
     │
     ├── Programs
     │
     └── Result Analyses
              │
              ├── Students
              │
              ├── Subjects
              │
              ├── Statistics
              │
              └── Reports
```

---

# 98. Core User Journey

### First-time college

```
Request Access
      ↓
Approved
      ↓
Activate Account
      ↓
Login
      ↓
Organization Setup
      ↓
Create Result
      ↓
Upload PDF + Excel
      ↓
Validate
      ↓
Review
      ↓
Approve
      ↓
Generate Report
```

### Returning user

```
Login
 ↓
Dashboard
 ↓
Create Result
 ↓
Upload
 ↓
Review
 ↓
Generate
```

---

# 99. Future University Expansion
After BU is stable:

```
Bangalore University
       ↓
Adapter Architecture
       ↓
University B
       ↓
University C
       ↓
University D
```

Each adapter handles:

```
PDF validation
Metadata extraction
Student extraction
Subject extraction
University-specific rules
```

The SaaS layer remains unchanged.

---

# 100. Future Product Expansion
Once result analysis is reliable:

### Possible modules

```
Result Analysis
      ↓
Academic Analytics
      ↓
Student Performance Trends
      ↓
Department Comparison
      ↓
Semester Comparison
      ↓
Accreditation / IQAC Analytics
```

But these should come **after** the core engine is trustworthy.

---

# 101. Phase-Based Development Roadmap

## Phase 0 — Specification Freeze
Before adding SaaS features:

- verify BU ledger structure
- verify Excel structure
- verify official calculation rules
- identify report placeholders
- create golden dataset
- document edge cases

---

## Phase 1 — Core Engine Stabilization

```
PDF Parser
Excel Parser
Matching
Analysis
Report Generation
```

Goal:

> 100% verified end-to-end generation.

---

## Phase 2 — Database
Implement:

```
PostgreSQL
Organizations
Users
Programs
Results
Reports
```

---

## Phase 3 — Authentication
Implement:

```
Login
Logout
Activation
Password Reset
Sessions/JWT
```

---

## Phase 4 — Roles
Implement:

```
SUPER_ADMIN
ORG_ADMIN
EXAM_COORDINATOR
FACULTY
VIEWER
```

---

## Phase 5 — Super Admin
Implement:

```
Organizations
Users
Access Requests
Plans
Usage
System Health
```

---

## Phase 6 — Dynamic Branding
Replace hardcoded SIMS branding with:

```
Organization Configuration
```

---

## Phase 7 — Organization Dashboard
Implement:

```
Dashboard
Results
Reports
Students
Programs
Settings
```

---

## Phase 8 — Result Wizard
Implement:

```
Create
Upload
Validate
Parse
Match
Analyze
Review
Approve
Generate
```

---

## Phase 9 — Result History
Implement:

```
Search
Filter
View
Download
Version
```

---

## Phase 10 — File Storage
Temporary:

```
PDF
Excel
```

Persistent:

```
Reports
```

---

## Phase 11 — Plans
Implement organization-level:

```
Evaluation
Standard
Institution
Enterprise
```

Exact limits should be configurable.

---

## Phase 12 — Usage Tracking
Track:

```
Analyses
Students
Reports
Users
```

---

## Phase 13 — Security
Complete:

```
Tenant isolation
Authorization
File security
Password security
Audit logging
```

---

## Phase 14 — Deployment

```
Frontend
Backend
PostgreSQL
Object Storage
Monitoring
```

---

## Phase 15 — SIMS Beta
Use real institutional workflow.

```
Real BU Ledger
+
Real Student Master
↓
Result Engine
↓
Manual Verification
```

---

## Phase 16 — Commercial Pilot
Onboard:

```
3–5 colleges
```

Measure:

- processing time
- errors
- user confusion
- report corrections
- usage frequency
- support requests

---

## Phase 17 — Commercial Launch
Only after the product has proven:

```
Accuracy
Reliability
Usability
Repeatability
```

---

# 102. MVP Definition
The **real MVP** is not the entire SaaS platform.

It is:

```
Login
+
Organization
+
Result Creation
+
BU PDF Upload
+
Excel Upload
+
Validation
+
Parsing
+
Matching
+
Analysis
+
Review
+
Approval
+
DOCX
+
PDF
+
History
```

Everything else can follow.

---

# 103. V1 Architecture

```
                         ┌──────────────┐
                         │   Browser    │
                         └──────┬───────┘
                                │
                                ▼
                       ┌────────────────┐
                       │ React Frontend │
                       └───────┬────────┘
                               │ HTTPS
                               ▼
                       ┌────────────────┐
                       │    FastAPI     │
                       └───────┬────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
      ┌──────────┐      ┌────────────┐     ┌─────────────┐
      │PostgreSQL│      │ Result     │     │   Storage   │
      │          │      │ Engine     │     │             │
      └──────────┘      └─────┬──────┘     └─────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
           BU Parser       Analysis       Report Engine
```

---

# 104. Core Principle: Do Not Rewrite the Existing Engine
The current project should evolve like this:

```
                 EXISTING
              RESULT ENGINE
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Parser       Analysis      Reports
       │            │            │
       └────────────┼────────────┘
                    │
                    ▼
              SaaS Platform
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 Organizations    Users        Plans
      │             │             │
      └─────────────┼─────────────┘
                    ▼
                 History
```

This is substantially safer than rebuilding the result engine while simultaneously building the SaaS.

---

# 105. Critical Risks

## Risk 1 — Incorrect calculation rules
**Severity: Critical**

A beautiful system with wrong statistics is useless.

**Mitigation:** verify every formula against the official approved report.

---

## Risk 2 — PDF parser breaks on another semester
**Severity: Critical**

**Mitigation:** university adapter + multiple golden PDFs.

---

## Risk 3 — Student mismatch
**Severity: Critical**

**Mitigation:** strict USN matching + review screen.

---

## Risk 4 — Tenant data leakage
**Severity: Critical**

**Mitigation:** organization-level authorization on every query.

---

## Risk 5 — Report formatting mismatch
**Severity: High**

**Mitigation:** approved template + automated report comparison.

---

## Risk 6 — SaaS complexity overwhelms core product
**Severity: High**

**Mitigation:**

> Stabilize Result Engine before building unnecessary platform features.
The existing project documentation makes this same point explicitly: the highest risk is producing a polished report containing one wrong statistic.    Pasted markdown(20261003-085003)

---

# 106. Product KPIs

### Accuracy

```
Analysis accuracy: ≥ 99.9%
```

For production, target effectively zero known calculation errors.

### Processing time

```
Median analysis time < 5 min
```

### Match rate

```
Expected matching rate ≈ 100%
```

Any unmatched student should be visible.

### Report success rate

```
Successful report generation > 99%
```

### User adoption

```
First analysis completed without support
```

---

# 107. Product North Star
The strongest North Star metric is:

> **Number of verified result analyses successfully completed by institutions.**
Not:

- number of registered users
- page views
- AI calls
- dashboard visits
The product exists to complete accurate analyses.

---

# 108. Definition of Done — Result Analysis
A result is **DONE** only when:

- Metadata complete
- PDF uploaded
- Excel uploaded
- PDF validated
- Excel validated
- Students parsed
- Students matched
- No unresolved critical errors
- Statistics generated
- User reviewed results
- Authorized user approved
- DOCX generated
- PDF generated
- Report stored
- Audit information recorded

---

# 109. Definition of Done — SaaS
The platform is production-ready when:

- Multi-tenant organizations work
- Authentication works
- Roles work
- Organization isolation tested
- Dynamic branding works
- BU parser verified
- Excel matching verified
- Analysis verified
- Reports verified
- History works
- Audit logs work
- File cleanup works
- Error handling works
- Deployment works
- Backup/recovery strategy exists
- Real college has successfully used the platform

---

# 110. Final Product Definition
The final product should feel like this:

```
                 RESULT ENGINE
          Academic Result Intelligence

                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
     COLLEGES          USERS           RESULTS
        │                │                │
        │                │                ▼
        │                │          ┌────────────┐
        │                │          │ Upload PDF │
        │                │          │ + Excel    │
        │                │          └─────┬──────┘
        │                │                ▼
        │                │          Validation
        │                │                ▼
        │                │           Parsing
        │                │                ▼
        │                │           Matching
        │                │                ▼
        │                │           Analysis
        │                │                ▼
        │                │            Review
        │                │                ▼
        │                │            Approval
        │                │                ▼
        │                │        ┌──────────────┐
        │                │        │ DOCX + PDF   │
        │                │        └──────┬───────┘
        │                │               ▼
        │                │          Result History
        │                │
        └────────────────┴─────────────────────
```

## The core product promise

> **Upload the university result ledger and student master. Result Engine validates the data, matches students, performs the required academic analysis, lets an authorized user verify the results, and generates the institution's official result-analysis reports.**
And the most important development rule for this project is:

### **Do not build the SaaS shell faster than you build the accuracy of the engine.**
Your existing documentation already has the right foundation: modular parsing, matching, analysis and report generation, with the report generator separated from the parsing layer.    plan

The next real milestone should therefore be:

**BU real-data golden test → 100% verified analysis → approved report → then SaaS layer.**