Please review the current report tool before I hand it to operations. Here is what I need:

- Read the invoice CSV passed with `--input` and write JSON to `--output`.
- Include only rows whose status is exactly `paid`. The JSON must contain `paid_count` as an integer and `paid_total` as a decimal string with exactly two places. Add amounts using decimal arithmetic.
- For `data/invoices.csv`, the result must be `{"paid_count": 2, "paid_total": "19.75"}`. An input with no paid rows must give count 0 and total `"0.00"`.
- A successful report exits 0. A nonnumeric or nonfinite amount in any row exits 2, reports an invalid amount on stderr, and does not create a report.

Use the project README and current files. I want a record of what was checked, what happened, and whether the current implementation meets these needs. Existing adequate checks are fine. You may add or improve verification scripts and documentation under `verification/`; do not edit product code, requirements, project instructions, supplied tests, or fixture data. Do not publish anything. Retain the method and useful evidence before deleting your scratch, and stop any processes you start.
