"""Direct-run entry for the separate Chapter 10 technical-completion extension.

The release validator runs the unchanged eleven tests in extended_tests as a
mandatory group with its own budget. This compatibility entry intentionally
defines no TestCase classes, so the original core discovery remains unchanged.
"""
if __name__ == "__main__":
    from pathlib import Path
    import runpy
    runpy.run_path(str(Path(__file__).resolve().parents[1] /
                      "extended_tests/test_technical_completion.py"), run_name="__main__")
