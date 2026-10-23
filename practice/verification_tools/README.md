# Two tools, two Treasury questions

This optional Chapter 9 exercise runs Hypothesis against the actual current
`repo/src/treasury/routing.py`, then runs Bandit against that source and its
direct adapter. It also creates two explicitly seeded controls in a new output
directory. It does not change the learner's candidate or the protected oracle.

## Reproduce the observed route

From the companion root, create an isolated environment outside the companion:

```bash
python3 -m venv ../verification_env
../verification_env/bin/python -m pip install -r practice/verification_tools/requirements.txt
../verification_env/bin/python practice/verification_tools/run.py --output ../verification_tools_run_01
```

The pinned route was executed on Python 3.12.14, Linux. Other runtimes are
unobserved. The ordinary lab has no dependency on these optional tools. Inspect
the packages before installing them in a work environment.

## Interpret the result

The owner expectation is that finite positive cent-valued strings below
EUR 5,000 use the standard queue, while equality and larger values require
review. Nonpositive and selected malformed/nonfinite strings are rejected.
Hypothesis explores those declared families and explicit boundary examples.
It is not allowed to derive the expected threshold from the function it tests.

Changing `<` to `<=` in a disposable copy is the boundary negative control.
The property rejects `5000.00`. That is a demonstrated defect under a selected
case, not an empirical mutation score. The original source remains untouched.

The second risk is interpreting an amount as executable Python. A disposable
control replaces decimal parsing with `eval`. Bandit reports B307. This control
is only scanned and is never imported or executed. The actual router and direct
adapter have no selected Bandit findings. A clean syntax scan does not establish
safe permissions, correct authorization, dependency safety or the absence of
other vulnerabilities. Bandit does not understand the Treasury business rule.

## Original offline exercise and retained extension

The original CP09 used Python standard-library checks. The later retained
extension actually ran Hypothesis 6.170.5 and Bandit 1.8.6 on Linux with
Python 3.12.14. Table 9.4 distinguishes these scopes. Pytest, mutmut, CodeQL,
pip-audit and hosted GitHub Actions were not run in either scope represented
by that table.

| Record | What it identifies |
| --- | --- |
| [OBSERVATIONS.json](observed/OBSERVATIONS.json) | Versions, runtime, property outcomes, seeded boundary failure, exact scan invocations and router SHA-256 |
| [actual_router_and_adapter.json](observed/actual_router_and_adapter.json) | Bandit metrics and no selected findings for the router and direct adapter |
| [unsafe_parse_control.json](observed/unsafe_parse_control.json) | B307 for the deliberately seeded eval control, scanned without execution |

The router source is `repo/src/treasury/routing.py`. Its recorded digest is
`14d186a327a418dddb405144bfefb5810ed27e626b981424c9ad3b66742e8b32`.
The direct adapter is `repo/src/treasury/architecture/direct.py`. The retained
invocation and report identify that path, but the original observation does
not record a separate adapter digest. Do not infer an exact historical byte
binding from the current package's inventory. This editorial revision preserves
the original receipts and reports their actual scope; it is not a new tool run.
Rerun the checks after changing either source and retain the new result.


Primary documentation, checked 2026-10-21:

- https://hypothesis.readthedocs.io/en/latest/quickstart.html
- https://bandit.readthedocs.io/en/latest/start.html
- https://bandit.readthedocs.io/en/latest/plugins/b307_eval.html
