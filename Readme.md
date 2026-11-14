# Guru99 Bank — Manual Functional Testing Project

Manual functional testing of the Guru99 Bank demo banking web application, based on the project's Software Requirements Specification (SRS v2, "Complete Edition"). The project covers the full manual QA cycle: test planning, scenario and test-case design, execution, requirements traceability, defect reporting and a final test summary report. The test cases were also imported into **TestRail**, executed in a Test Run, and reported there.

**Result:** 353 test cases executed — 169 passed, 137 failed, 47 blocked. 41 defects logged (5 Critical, 10 High, 18 Medium, 8 Low). Release not recommended.

## Project at a glance

| Item | Details |
|---|---|
| Application under test | Guru99 Bank demo site — https://demo.guru99.com |
| Requirements source | SRS v2 (Complete Edition) — `SRS_Complete_Guru99_Banking.docx` |
| Testing type | Manual functional testing (black-box) |
| Scope | Functional testing and external interfaces |
| Out of scope | Automation testing, performance / stress testing |
| User roles in scope | Manager and Customer |
| Environment | Google Chrome, Guru99 Bank demo site |
| Test management tool | TestRail |
| Schedule | Sep 2026 – Nov 2026 |
| Tester | Amjad Alrays |

## Deliverables

All core deliverables are sheets of a single Excel workbook: `Guru99_Bank_Test_Plan_Updated.xlsx`

| Sheet | Content |
|---|---|
| Test Plan | Objective, scope, approach, entry/exit criteria, severity/priority definitions, defect life cycle, risks |
| Test Scenarios | High-level scenarios per module, mapped to requirements and test cases |
| Test Cases | 353 test cases (ID, Title, Description, Pre-Condition, Test steps, Test data, Priority, Expected Result, Actual result, Status, Designer, Executer) |
| RTM | Requirements Traceability Matrix — 131 SRS requirements mapped to test cases, results and linked defects |
| Bug Report | 41 defects with steps, expected/actual result, severity, priority, status and linked test cases |
| Failed-Blocked Tests | Every failed or blocked test case with its linked defect |
| Test Summary Report | Results by module and priority, requirement coverage, defect summary, exit criteria, conclusion |
| Test Data Setup | Test data used by the test cases and how to prepare it |

TestRail artifacts are in the `testrail/` folder (see [Test management in TestRail](#test-management-in-testrail)).

## Modules covered (14)

Login · New Customer · Edit Customer · Delete Customer · New Account · Edit Account · Delete Account · Deposit · Withdrawal · Fund Transfer · Balance Enquiry · Mini Statement · Customized Statement · Change Password

## Test approach

- Requirement-based testing — every test case traces back to an SRS requirement
- Equivalence partitioning and boundary value analysis for field lengths and numeric limits
- Positive and negative testing, including blank, invalid and duplicate input
- Error guessing, including security checks (SQL injection input, direct URL access, session handling after logout)
- Test case status values: Pass, Fail, Blocked, Not Applicable

## Results

### Overall

| Total | Passed | Failed | Blocked | Executed (Pass + Fail) | Pass rate (of executed) | Pass rate (of total) |
|---|---|---|---|---|---|---|
| 353 | 169 | 137 | 47 | 306 (86.7%) | 55.2% | 47.9% |

### By module

| Module | Total | Pass | Fail | Blocked |
|---|---|---|---|---|
| Login | 18 | 8 | 10 | 0 |
| New Customer | 52 | 39 | 12 | 1 |
| Edit Customer | 40 | 12 | 28 | 0 |
| Delete Customer | 14 | 12 | 2 | 0 |
| New Account | 29 | 23 | 4 | 2 |
| Edit Account | 15 | 1 | 1 | 13 |
| Delete Account | 13 | 4 | 4 | 5 |
| Deposit | 27 | 8 | 3 | 16 |
| Withdrawal | 29 | 13 | 16 | 0 |
| Fund Transfer | 31 | 13 | 18 | 0 |
| Balance Enquiry | 15 | 6 | 4 | 5 |
| Mini Statement | 20 | 6 | 9 | 5 |
| Customized Statement | 27 | 4 | 23 | 0 |
| Change Password | 23 | 20 | 3 | 0 |
| **Total** | **353** | **169** | **137** | **47** |

### Defects

| Severity | Count |
|---|---|
| Critical | 5 |
| High | 10 |
| Medium | 18 |
| Low | 8 |
| **Total** | **41** |

All 41 defects are in status Open — they were reported against a public demo site, so no fix/retest cycle took place.

### Requirements coverage

131 SRS requirements in the RTM: 78 Pass, 40 Fail, 9 Blocked, 4 not covered by a test case (96.9% covered).

## Key findings

- **Security:** login can be bypassed with SQL injection input; protected pages open without authentication; accounts are not locked after 3 failed attempts; the session survives Logout; credentials are not case-sensitive.
- **Core banking flows:** Deposit, Balance Enquiry and Fund Transfer end on an error page, a blank page or without any message, which blocked the dependent balance, statement and validation tests.
- **Validation:** Edit Customer, Customized Statement and Change Password do not enforce the SRS rules; New Customer accepts customers under 18 and invalid mobile/password lengths.
- **Field lengths:** several input fields are shorter than the lengths defined in the SRS.
- **What works:** basic blank and non-numeric input validation passes in most modules.

**Conclusion:** release is not recommended — 5 Critical and 10 High defects are open and 47 tests could not be completed because of them.

## Test management in TestRail

After the manual execution, the test cases were loaded into TestRail to manage them like in a real QA team.

| Step | What was done |
|---|---|
| 1. Import | The 353 test cases were exported from Excel to CSV and imported into a TestRail project with field mapping (Section, Title, Preconditions, Steps, Test Data, Expected Result, Priority, References). A custom `Test Data` field was added. |
| 2. Structure | 14 sections, one per module. The SRS requirement ID is stored in the `References` field for traceability. |
| 3. Execution | One Test Run (`Guru99 - Execution Run 1`) containing all 353 cases. |
| 4. Results upload | Execution results (status, actual result, linked defect IDs) were uploaded in bulk through the TestRail REST API with a Python script. |
| 5. Reporting | The *Runs (Summary)* and *Coverage for References* reports were generated and exported to PDF. |

Files: `testrail/Guru99_TestRail_Import.csv` · `testrail/upload_results_to_testrail.py` · `testrail/reports/`

### Run the upload script

```bash
pip install requests pandas openpyxl

# Dry run: builds the results locally and sends nothing
python testrail/upload_results_to_testrail.py --excel Guru99_Bank_Test_Plan_Updated.xlsx --dry-run

# Real upload (the API key is requested through a hidden prompt and is never stored in the code)
python testrail/upload_results_to_testrail.py --excel Guru99_Bank_Test_Plan_Updated.xlsx \
  --url https://YOUR-INSTANCE.testrail.io --email you@example.com --run-id 1
```

## Limitations

- Results come from a shared public demo site that is not the application described in the SRS, so some differences from the SRS are reported as defects.
- No test case covers a login as Customer, the 15-minute session timeout, or the Customer-role rules FT12, MS5 and CS9, so the Customer role was not exercised.
- 4 of 131 requirements have no test case.
- In TestRail, 87 detailed test cases (mostly boundary-value cases) are linked to a general requirement and carry no `References` value, so the TestRail coverage report lists them separately. The full requirement coverage is documented in the RTM sheet.
- TestRail's progress and forecast sections reflect the time the results were uploaded and are not a measure of the real execution time.
- Performance, stress and automation testing are out of scope.

## AI usage

AI tools were used to speed up test-case drafting and to automate the TestRail import and results upload. Every test case was executed manually and every actual result was reviewed and recorded by the tester.

## Repository structure

```
.
├── README.md
├── Guru99_Bank_Test_Plan_Updated.xlsx
├── SRS_Complete_Guru99_Banking.docx
└── testrail/
    ├── Guru99_TestRail_Import.csv
    ├── upload_results_to_testrail.py
    └── reports/
        ├── Test_Execution_Summary.pdf
        └── Requirements_Coverage.pdf
```

## Tools

Microsoft Excel · TestRail · Python (requests, pandas) · Google Chrome · AI tools · Git / GitHub

## Author

**Amjad Alrays** — QA Engineer / Software Test Engineer
[GitHub](https://github.com/amjad639) · [LinkedIn](https://linkedin.com/in/amjad-alrays)
