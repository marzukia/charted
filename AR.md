# Adversarial Review: Migrate from Poetry to uv

## 📋 Changes Reviewed

### 1. `.github/workflows/ci.yml`

**Changes:**
- Added uv cache step (`actions/cache@v4` for `~/.cache/uv`)
- Uses `uv pip install '.[dev]'` 
- Runs `uv run flake8 charted` and `uv run tox`

**✅ IMPROVEMENTS vs previous:**
- Cache step now present (fixes #1 from previous AR)
- Caches `~/.cache/uv` keyed by pyproject.toml hash

**⚠️ REMAINING ISSUES:**

1. **No uv version pinning** - Line `pip install uv` uses latest, could break on uv major version bump
   - **Fix:** Add `uv==0.x.y` or `--version` constraint
   - **Risk:** Medium - uv is generally backward compatible but not guaranteed

2. **`uv pip install '.[dev]'` is unoptimized** - Re-downloads deps on each CI run
   - **Fix:** Use `uv pip sync` with lockfile or `uv sync` directly
   - **Risk:** Low-Medium - CI is slower but functional

3. **No `--frozen` flag** - Dependencies might resolve differently
   - **Fix:** Add `--frozen` to prevent version drift
   - **Risk:** Low - pyproject.toml has pinned versions

4. **Flake8 runs before tox** - Could fail if tox env needed
   - **Fix:** Order is probably fine but document rationale
   - **Risk:** None - flake8 doesn't need tox env

### 2. `pyproject.toml`

**Current State:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "charted"
version = "0.1.8a"
# ... PEP 621 format

[project.optional-dependencies]
dev = ["pytest>=8.2.1", "ipython>=8.24.0", "flake8>=7.0.0", "black>=24.4.2", "tox>=4.15.1"]
docs = ["sphinx>=7.3.7"]
```

**✅ MIGRATION COMPLETE:**
- No Poetry fields present (no `tool.poetry`)
- Uses hatchling build backend (PEP 517 compliant)
- PEP 621 `[project]` format
- Dev dependencies in `[project.optional-dependencies]`

**⚠️ MINOR ISSUES:**

1. **No uv.lock file present** - uv can generate lockfiles for reproducible installs
   - **Fix:** Run `uv lock` to generate `uv.lock`
   - **Risk:** Low - CI still works without it, but local dev less reproducible

2. **Version constraints use `>=` only** - Could pull in breaking changes
   - **Fix:** Pin upper bounds: `pytest>=8.2.1,<9.0.0`
   - **Risk:** Low-Medium - depends on how strict semver is

### 3. `tox.ini`

**Current State:**
```ini
[testenv]
deps = pytest coverage
commands =
    uv pip install .
    coverage run -m pytest
    coverage xml
```

**✅ MIGRATION COMPLETE:**
- No poetry references
- Uses `uv pip install .` (line 13, 26)
- Clean tox config

**⚠️ ISSUES:**

1. **`uv pip install .` in tox is redundant** - tox already creates venv, should use tox's deps
   - **Fix:** Remove `uv pip install .` line, add pytest/coverage to `[testenv]` deps
   - **Risk:** Medium - current approach works but inefficient

2. **No sphinx in tox docs env** - sphinx-build in commands but not in deps
   - **Wait, actually sphinx IS in deps (line 20-22)**
   - **Risk:** None - this is correct

3. **`uv pip install .` doesn't install dev deps** - Tests need pytest
   - **Fix:** Use `uv pip install -e ".[dev]"` or add to `[testenv]` deps
   - **Risk:** HIGH - Tests might fail if pytest not available!

### 4. `README.md`

**Current State:**
```sh
uv run python charted/commands/create_font_definition.py Helvetica
```

**✅ CORRECT:**
- Updated from `poetry run` to `uv run`
- Path corrected from `fonts/creator.py` to `commands/create_font_definition.py`
- **Verified file exists:** `charted/commands/create_font_definition.py` ✓

### 5. `.gitignore`

**Changes:**
```
COMPLAINTS.md
DONE.md
FINDINGS.md
PLANS.md
TODO.md
```

**⚠️ CONSIDERATION:**
- These are dev artifacts - ignoring them is reasonable
- **Suggestion:** Add `uv.lock` if you want it ignored (or don't, if you want it committed)
- **Risk:** None - personal preference

### 6. `poetry.lock`

**Status:** ✅ **DELETED** ✓

**Correct!** Poetry lockfile removed as part of migration.

---

## 🎯 Overall Assessment

### ✅ What's Working

1. **pyproject.toml fully migrated** - No Poetry remnants, uses hatchling
2. **CI has caching** - uv cache configured
3. **tox.ini migrated** - No poetry commands
4. **README updated** - Correct path and uv syntax
5. **poetry.lock removed** - Clean break from Poetry

### ⚠️ Issues to Address (in priority order)

| Priority | Issue | Risk | Fix |
|----------|-------|------|-----|
| **HIGH** | tox tests may fail without pytest | Tests fail | Add pytest to tox deps or use `uv pip install -e ".[dev]"` |
| **MEDIUM** | No uv version pinning | CI break on uv update | Add `pip install uv==0.x.y` |
| **MEDIUM** | No lockfile for reproducibility | Dev environment drift | Run `uv lock`, commit uv.lock |
| **LOW** | Version constraints too loose | Breaking changes sneak in | Add upper bounds to deps |
| **LOW** | Redundant `uv pip install .` in tox | Slower tox runs | Remove, use tox deps |

### 📊 Risk Matrix

| Component | Status | Risk Level |
|-----------|--------|------------|
| pyproject.toml | ✅ Migrated | None |
| CI workflow | ⚠️ Partial | Low (cache added, missing pin) |
| tox.ini | ⚠️ May fail tests | **HIGH** - pytest may not be installed |
| README | ✅ Correct | None |
| gitignore | ✅ Reasonable | None |

### 🚦 Recommendation

**DO NOT MERGE YET** - Fix the tox test configuration first:

1. **Immediate fix needed:** Ensure tox tests can run (pytest must be available)
2. **Before merge:** Add uv version pin, consider `uv lock`
3. **Nice to have:** Optimize tox deps, tighten version constraints

**Minimum viable PR:**
```diff
# tox.ini [testenv]
- deps = pytest coverage  # OR
+ deps = 
+     pytest
+     coverage
+ commands =
+     coverage run -m pytest  # Remove uv pip install .
+     coverage xml
```

OR verify that `uv pip install .` pulls in test dependencies (it doesn't by default - needs `. [dev]`).

---

**Final verdict:** 🟡 **CONDITIONAL APPROVAL** - Fix tox pytest availability before merging.
