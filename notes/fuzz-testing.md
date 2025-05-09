# Fuzz Testing Guide

## Overview

Fuzz testing (fuzzing) automatically provides invalid, unexpected, or random data to program inputs to discover bugs, crashes, and security vulnerabilities. This guide documents the fuzz testing setup for charted.

## Tools

- **atheris**: Google's Python coverage-guided fuzzer
- Scripts located in `scripts/` directory

## Fuzz Test Targets

### CSV Parser Fuzzer

**File**: `scripts/fuzz_csv_parser.py`

**Target**: CSV parsing logic in `charted/cli/create.py::_parse_csv()`

**What it tests**:
- Invalid CSV formats
- Encoding issues
- Malformed rows
- Empty fields
- Special characters
- Very large inputs

### JSON Parser Fuzzer

**File**: `scripts/fuzz_json_parser.py`

**Target**: JSON parsing in `charted/cli/create.py::load_data()`

**What it tests**:
- Invalid JSON syntax
- Encoding issues
- Nested structures
- Very large objects
- Special Unicode characters

## Running Fuzz Tests

### Quick Test (5 minutes)

```bash
# Run with timeout
timeout 300 python scripts/fuzz_csv_parser.py
timeout 300 python scripts/fuzz_json_parser.py
```

### Extended Test (1 hour)

```bash
# Run for 1 hour each
timeout 3600 python scripts/fuzz_csv_parser.py
timeout 3600 python scripts/fuzz_json_parser.py
```

### Full Test Session

```bash
# Run both fuzzers with the helper script
./scripts/run-fuzzing.sh
```

## Interpreting Results

### No Crashes

If fuzzing runs without crashes, it means:
- ✅ Parser handles edge cases well
- ✅ No obvious security vulnerabilities found
- ✅ Continue testing with longer sessions

### Crashes Found

If a crash occurs:
1. **Save the input**: atheris saves crashing inputs to `corpus/`
2. **Analyze the crash**:
   ```bash
   python -c "
   data = open('corpus/crash_X', 'rb').read()
   print(repr(data))
   "
   ```
3. **Fix the bug** in the parser
4. **Add regression test** with the crashing input

### Coverage

Check coverage statistics:
```bash
# atheris prints coverage during fuzzing
# Look for "Interesting:" messages indicating new code paths found
```

## Best Practices

### When to Run

- **Before major releases**: Run 1+ hour of fuzzing
- **After parser changes**: Quick 5-minute test
- **Quarterly**: Extended session (1+ hours)

### Corpus Management

```bash
# Save seed corpus for reproducibility
./scripts/fuzz_csv_parser.py -dict=csv.dict -merge=corpus/

# Use saved corpus for continued testing
./scripts/fuzz_csv_parser.py corpus/
```

### CI Integration

Add to `.github/workflows/ci.yml`:

```yaml
fuzz-testing:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install atheris
      run: pip install atheris
    - name: Run CSV fuzzer (5 min)
      run: timeout 300 python scripts/fuzz_csv_parser.py
    - name: Run JSON fuzzer (5 min)
      run: timeout 300 python scripts/fuzz_json_parser.py
```

## Common Fuzz Findings

### Typical Bugs Discovered

| Bug Type | Example | Fix |
|----------|---------|-----|
| Division by zero | Empty CSV with headers | Add validation |
| Index out of bounds | Malformed rows | Bounds checking |
| Memory exhaustion | Very large inputs | Size limits |
| Encoding errors | Invalid UTF-8 | Error handling |
| Infinite loops | Recursive structures | Recursion limits |

### Security Concerns

Fuzz testing helps find:
- **Buffer overflows** (not applicable to Python)
- **Denial of service** (memory/CPU exhaustion)
- **Injection vulnerabilities** (if parsing user input)
- **Information disclosure** (crash dumps with data)

## Troubleshooting

### Fuzzer Won't Start

```bash
# Check Python version (atheris requires 3.7+)
python --version

# Reinstall atheris
pip uninstall atheris
pip install atheris
```

### No Interesting Inputs Found

```bash
# Provide seed corpus with valid examples
echo "a,b,c\n1,2,3" > seed.csv
python scripts/fuzz_csv_parser.py seed.csv
```

### Too Many False Positives

Some exceptions are expected:
- `json.JSONDecodeError` - invalid JSON
- `csv.Error` - invalid CSV

These are caught and ignored. Only uncaught exceptions indicate real bugs.

## Related Resources

- [atheris Documentation](https://github.com/google/atheris)
- [Python Fuzzing Best Practices](https://google.github.io/oss-fuzz/getting-started/new-project-guide/python-lang/)
- [OWASP Fuzzing](https://owasp.org/www-community/Fuzzing)

## Next Steps

1. **Run initial fuzz session** to establish baseline
2. **Fix any crashes** discovered
3. **Add seed corpus** with realistic data
4. **Integrate into CI** for continuous testing
5. **Schedule quarterly** extended sessions
