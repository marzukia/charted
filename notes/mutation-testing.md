# Mutation Testing Guide

## Overview

Mutation testing helps identify weak tests by introducing small bugs (mutants) into the codebase and checking if the test suite catches them. A high mutation score indicates strong test coverage.

## Tools

- **mutmut**: Python mutation testing tool
- Configured in `.mutmut-config`

## Running Mutation Testing

### Initial Setup

```bash
# Install dependencies
uv sync --extra dev

# Run initial mutation testing to establish baseline
./scripts/run-mutation-testing.sh
```

### Quarterly Schedule

Mutation testing should be run quarterly:

1. **Run full mutation test suite**:
   ```bash
   ./scripts/run-mutation-testing.sh
   ```

2. **Review results**:
   ```bash
   mutmut results
   mutmut show  # View individual mutants
   ```

3. **Improve tests** for surviving mutants:
   - Add new test cases
   - Strengthen assertions
   - Cover edge cases

### CI Integration

Add to `.github/workflows/ci.yml` for quarterly runs:

```yaml
mutation-testing:
  runs-on: ubuntu-latest
  schedule:
    - cron: '0 0 1 * *'  # First day of every month
  steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        pip install uv
        uv sync --extra dev
    - name: Run mutation testing
      run: ./scripts/run-mutation-testing.sh
```

## Understanding Results

### Mutation Score

- **90%+**: Excellent - tests catch most bugs
- **80-90%**: Good - solid test coverage
- **70-80%**: Acceptable - some gaps exist
- **<70%**: Needs improvement - weak tests

### Mutant Status

- **Killed**: Test caught the mutation ✓
- **Survived**: No test detected the bug ✗
- **Timeout**: Mutation caused infinite loop/slowdown
- **Skipped**: Mutant not applicable

## Common Mutations

| Original | Mutated | Example |
|----------|---------|---------|
| `>` | `<=` | `if x > 5:` → `if x <= 5:` |
| `==` | `!=` | `if x == y:` → `if x != y:` |
| `+` | `-` | `x + y` → `x - y` |
| `and` | `or` | `a and b` → `a or b` |
| Return value | `None` | `return x` → `return None` |

## Best Practices

1. **Run after major test additions**: Verify new tests kill mutants
2. **Focus on surviving mutants**: Add tests for uncovered logic
3. **Don't chase 100%**: Diminishing returns above 90%
4. **Review timeout mutants**: May indicate performance issues
5. **Exclude generated code**: Don't mutate auto-generated files

## Troubleshooting

### Slow Mutation Testing

```bash
# Run with fewer workers
mutmut run --workers=2

# Exclude slow modules
# Add to .mutmut-config:
paths_to_mutate = charted/charts/ charted/utils/
```

### False Positives

Some mutants may "survive" legitimately:
- Defensive code that handles edge cases
- Logging/debug statements
- Version constants

Mark as ignored in `.mutmut-ignore`:
```python
# mutmut: no mutation
SOME_CONSTANT = "value"
```

## Related Resources

- [mutmut Documentation](https://github.com/boxed/mutmut)
- [Mutation Testing Principles](https://mutationtesting.org/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
