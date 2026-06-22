# `test_pipeline.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal regression test for the Gallica post-OCR pipeline.

This script verifies that a few core normalization operations
still behave as expected after modifications to the pipeline.

The goal is not exhaustive testing, but quick regression control.
"""

import subprocess
import tempfile
from pathlib import Path


TEST_TEXT = '''
M . Dupont a dit : "bonjour" .
Le 1 er janvier 1890.
'''


EXPECTED_PATTERNS = [
    "1er janvier",
    "« bonjour »",
]


PIPELINE_SCRIPTS = [
    "02apost.py",
    "05_espaces.py",
    "06_ordinaux.py",
    "13_guillemets.py",
]


SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"


def run_pipeline(input_text):
    """
    Run a minimal subset of the normalization pipeline.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        input_file = tmpdir / "input.txt"
        output_file = tmpdir / "output.txt"

        input_file.write_text(input_text, encoding="utf-8")

        current_input = input_file

        for i, script in enumerate(PIPELINE_SCRIPTS):
            current_output = tmpdir / f"step_{i}.txt"

            command = [
                "python",
                str(SCRIPT_DIR / script),
                str(current_input),
                str(current_output),
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"[FAIL] Error while running {script}")
                print(result.stderr)
                return None

            current_input = current_output

        final_text = current_input.read_text(encoding="utf-8")
        output_file.write_text(final_text, encoding="utf-8")

        return final_text


def main():
    print("Running minimal regression test...\n")

    result = run_pipeline(TEST_TEXT)

    if result is None:
        return

    success = True

    for pattern in EXPECTED_PATTERNS:
        if pattern not in result:
            print(f"[FAIL] Missing expected pattern: {pattern}")
            success = False
        else:
            print(f"[OK] Found: {pattern}")

    print("\n--- Output ---\n")
    print(result)

    if success:
        print("\n[OK] Minimal regression test passed.")
    else:
        print("\n[FAIL] Regression test failed.")


if __name__ == "__main__":
    main()
```

---

# Où placer ce fichier

À la racine du dépôt :

```text
README.md
LICENSE
requirements.txt
test_pipeline.py
scripts/
```

---

# Utilisation

Depuis la racine du dépôt :

```bash
python test_pipeline.py
```

---

# Ce que fait ce test

Le script :

- crée un mini corpus synthétique ;
- exécute une partie du pipeline ;
- vérifie quelques transformations attendues ;
- affiche un diagnostic simple.

Il sert principalement de :

- test de régression minimal ;
- vérification rapide après modification des scripts ;
- démonstration reproductible du pipeline.

