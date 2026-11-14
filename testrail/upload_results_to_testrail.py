"""
Upload Guru99 test execution results (from the Excel workbook) to a TestRail Test Run.

Usage (run on YOUR computer, not here):
    pip install requests pandas openpyxl

    # 1) Dry run: builds the results locally, sends nothing, writes results_preview.csv
    python upload_results_to_testrail.py --excel Guru99_Bank_Test_Plan_Updated.xlsx --dry-run

    # 2) Real upload
    python upload_results_to_testrail.py --excel Guru99_Bank_Test_Plan_Updated.xlsx \
        --url https://YOURNAME.testrail.io --email you@mail.com --run-id 1

The API key is read from the TESTRAIL_API_KEY environment variable, or asked
for with a hidden prompt. Never paste it into this file.
"""
import argparse
import getpass
import os
import re
import sys

import pandas as pd

# TestRail default status IDs
STATUS = {"pass": 1, "blocked": 2, "fail": 5}
BATCH = 100


def expand_ids(text):
    """'TC_LG_009 - TC_LG_010\n(2 failed)' / 'TC_A_001; TC_B_002' -> list of TC IDs."""
    ids = []
    text = str(text)
    # ranges first: TC_XX_001 - TC_XX_005
    for p, a, b in re.findall(r"(TC_[A-Z]+_)(\d+)\s*-\s*TC_[A-Z]+_(\d+)", text):
        ids += [f"{p}{i:03d}" for i in range(int(a), int(b) + 1)]
    text = re.sub(r"(TC_[A-Z]+_)(\d+)\s*-\s*TC_[A-Z]+_(\d+)", " ", text)
    ids += re.findall(r"TC_[A-Z]+_\d+", text)
    return ids


def build_results(excel):
    tc = pd.read_excel(excel, sheet_name="Test Cases")
    tc = tc[tc["ID"].notna()].copy()

    bugs = pd.read_excel(excel, sheet_name="Bug Report")
    tc_to_bugs = {}
    for _, row in bugs.iterrows():
        for t in expand_ids(row["Test case ID"]):
            tc_to_bugs.setdefault(t, []).append(str(row["ID"]).strip())

    results = {}
    for _, row in tc.iterrows():
        status = str(row["Status"]).strip().lower()
        if status not in STATUS:
            print(f"Skipping {row['ID']}: unknown status {row['Status']!r}")
            continue
        tc_id = str(row["ID"]).strip()
        actual = "" if pd.isna(row["Actual result"]) else str(row["Actual result"]).strip()
        res = {
            "status_id": STATUS[status],
            "comment": f"Actual result: {actual}",
        }
        if status in ("fail", "blocked") and tc_id in tc_to_bugs:
            res["defects"] = ", ".join(dict.fromkeys(tc_to_bugs[tc_id]))
        results[tc_id] = res
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True)
    ap.add_argument("--url", help="e.g. https://yourname.testrail.io")
    ap.add_argument("--email")
    ap.add_argument("--run-id", type=int)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    results = build_results(args.excel)
    counts = pd.Series([r["status_id"] for r in results.values()]).map(
        {1: "Passed", 2: "Blocked", 5: "Failed"}).value_counts()
    print(f"Built {len(results)} results:\n{counts.to_string()}")

    if args.dry_run:
        pd.DataFrame(
            [{"TC": k, "status_id": v["status_id"], "defects": v.get("defects", ""),
              "comment": v["comment"]} for k, v in results.items()]
        ).to_csv("results_preview.csv", index=False, encoding="utf-8")
        print("Dry run only. Check results_preview.csv. Nothing was sent.")
        return

    if not (args.url and args.email and args.run_id):
        sys.exit("--url, --email and --run-id are required (unless --dry-run).")

    import requests

    key = os.getenv("TESTRAIL_API_KEY") or getpass.getpass("TestRail API key (hidden): ")
    base = args.url.rstrip("/") + "/index.php?/api/v2/"
    s = requests.Session()
    s.auth = (args.email, key)
    s.headers["Content-Type"] = "application/json"

    # 1) fetch tests of the run (handles paginated and plain-list responses)
    tests, offset = [], 0
    while True:
        r = s.get(base + f"get_tests/{args.run_id}&offset={offset}")
        if r.status_code != 200:
            sys.exit(f"get_tests failed: {r.status_code} {r.text[:300]}")
        data = r.json()
        batch = data["tests"] if isinstance(data, dict) else data
        tests += batch
        if isinstance(data, dict) and data.get("_links", {}).get("next"):
            offset += data.get("limit", len(batch)) or len(batch)
        else:
            break
    print(f"Run {args.run_id} contains {len(tests)} tests.")

    # 2) match by 'TC_XX_NNN' at the start of the case title
    payload, missing = [], []
    by_tc = {}
    for t in tests:
        m = re.match(r"(TC_[A-Z]+_\d+)", t["title"])
        if m:
            by_tc[m.group(1)] = t["case_id"]
    for tc_id, res in results.items():
        if tc_id in by_tc:
            payload.append({"case_id": by_tc[tc_id], **res})
        else:
            missing.append(tc_id)
    if missing:
        print(f"WARNING: {len(missing)} test cases not found in the run: {missing[:10]}...")

    # 3) send in batches
    sent = 0
    for i in range(0, len(payload), BATCH):
        chunk = payload[i:i + BATCH]
        r = s.post(base + f"add_results_for_cases/{args.run_id}", json={"results": chunk})
        if r.status_code != 200:
            sys.exit(f"Upload failed at batch {i // BATCH + 1}: {r.status_code} {r.text[:300]}")
        sent += len(chunk)
        print(f"Uploaded {sent}/{len(payload)}")
    print("Done.")


if __name__ == "__main__":
    main()
