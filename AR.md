# Adversarial Review: Migrate from Poetry to uv

## 📋 Changes Reviewed

### 1. `.github/workflows/ci.yml`

```diff
- pip install uv
+ uv pip install '.[dev]'
+ uv run flake8 charted
+ uv run tox
```

**🚨 CRITICAL ISSUES:**

1. **No `uv` cache/restore step** - CI will be slow without caching `~/.cache/uv` or using `--frozen`
2. **No Python version pinning for uv** - Using whatever pip gives you
3. **`uv pip install` won't respect pyproject.toml Poetry format** - This is a MIGRATION, not a replacement. The pyproject.toml still has Poetry fields!
4. **`uv run tox`** - This runs tox inside a uv-managed environment, but tox.ini might still reference poetry
5. **No verification that dependencies actually install** - `. [dev]` might not exist

### 2. `README.md`

```diff
- poetry run python charted/fonts/creator.py
+ uv run python charted/fonts/creator.py
```

**❌ LOW RISK** - Just documentation, but check if `charted/fonts/creator.py` exists vs `charted/commands/create_font_definition.py`

### 3. `.gitignore`

```diff
+COMPLAINTS.md
+DONE.md
+FINDINGS.md
+PLANS.md
+TODO.md
```

**❓ QUESTIONABLE:** These look like development artifacts. Should they be ignored globally in `.gitignore` or is this project-specific?

### 4. `poetry.lock` deletion

**✅ CORRECT** - This should go when migrating

## 🔍 Missing Critical Files

**The pyproject.toml changes are NOT in the diff!** This is the most important file. If pyproject.toml still has Poetry fields, the migration is INCOMPLETE and will FAIL.

## 🚨 Blocking Issues Found

1. **pyproject.toml unchanged?** - Need to verify it's been converted to PEP 621 format
2. **No lockfile strategy** - uv uses `uv.lock`, not poetry.lock. What's the strategy?
3. **tox.ini migration?** - Tox likely still has Poetry commands inside
4. **No pyproject.toml diff shown** - Critical gap in the PR

## 💡 Recommendations

1. **ADD pyproject.toml changes to PR** - Show the migration from Poetry config to PEP 621
2. **Update tox.ini** - Remove poetry references
3. **Add uv cache to CI** - `actions/cache@v3` for `~/.cache/uv`
4. **Verify `. [dev]` extras** exist in pyproject.toml
5. **Consider keeping .gitignore changes separate** - It's unrelated to the migration

## ⚠️ Risk Assessment

- **High Risk**: CI will likely fail due to incomplete pyproject.toml migration
- **Medium Risk**: tox may fail if tox.ini still has poetry commands
- **Low Risk**: README change is straightforward

**Would NOT approve this PR in current state without seeing pyproject.toml changes.**
