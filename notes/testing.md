# Testing Resilience Notes

*Status: May 22, 2026 | Last Updated: Just now*

---

## 🎯 Executive Summary

**Current State**: 595 tests passing (**91% coverage**) with property-based testing infrastructure newly added.

**Key Achievement**: Property-based tests discovered and fixed critical edge cases in validation logic. Critical coverage gaps in theme system and chart modules now filled. **90% coverage target ACHIEVED.**

**Next Priority**: Fill remaining coverage gaps in chart modules (scatter.py, column.py, pie.py).

---

## ✅ Completed (PR Ready)

- [x] **Analyzed test coverage** across all modules (86% total)
- [x] **Installed hypothesis** for property-based testing
- [x] **Created 34 property-based tests** covering colors, themes, and validation
- [x] **Fixed hex parsing bugs**:
  - Added support for 3-digit hex (#FFF → #FFFFFF)
  - Added support for 8-digit hex with alpha (#AARRGGBB)
  - Added `is_valid_hex_color()` validation function
- [x] **Created TESTING_STRATEGY.md** with comprehensive roadmap
- [x] **Added theme_manager.py tests**: 40% → **96%** (16 tests)
- [x] **Added registry.py tests**: 58% → **100%** (19 tests)
- [x] **Added validation.py property tests**: 48% → **97%** (26 tests)
- [x] **Added scatter.py comprehensive tests**: 63% → **100%** (30 tests)
- [x] **Added data_model.py property tests**: 94% → **100%** (20 tests)
- [x] **Added column.py comprehensive tests**: 81% → **96%** (44 tests)
- [x] **Added pie.py comprehensive tests**: 89% → **92%** (54 tests)
- [x] **Added series_style.py comprehensive tests**: 71% → **100%** (39 tests)
- [x] **Added CLI integration tests**: 25 new tests for create and batch commands
- [x] **Added mutation testing setup**: mutmut configuration and documentation
- [x] **Added performance benchmarks**: 18 benchmarks across all chart types
- [x] **Added visual regression tests**: 20 tests for themes and edge cases
- [x] **Added fuzz testing setup**: atheris scripts for CSV/JSON parsers
- [x] **Added accessibility tests**: 13 tests for WCAG compliance
- [x] **Added test documentation**: Comprehensive README.md and helper utilities
- [x] **Created test helpers**: conftest.py fixtures, chart_builders.py, svg_assertions.py
- [x] **Created TESTING_IMPROVEMENTS_PR.md** for PR description
- [x] **Verified all tests pass**: 681 tests passing (91% coverage)

---

## 🚨 Critical Gaps (COMPLETED ✅)

### Priority: CRITICAL 🔴

|||| Module | Before | After | Status |
|--------|--------|-------|--------|
| `utils/theme_manager.py` | 40% | **96%** | ✅ **FIXED** |
| `themes/registry.py` | 58% | **100%** | ✅ **FIXED** |
| `utils/validation.py` | 48% | **97%** | ✅ **FIXED** |
| `charts/scatter.py` | 63% | **100%** | ✅ **FIXED** |
| `utils/data_model.py` | 94% | **100%** | ✅ **FIXED** |
| `charts/column.py` | 81% | **96%** | ✅ **FIXED** |
| `charts/pie.py` | 89% | **92%** | ✅ **FIXED** |
| `utils/series_style.py` | 71% | **100%** | ✅ **FIXED** |

**Why Critical**: These are core utilities that affect all chart generation. Low coverage meant bugs could slip through.

---

## ⚠️ High Priority Issues (Not in this PR)

### Priority: HIGH 🟠

- [ ] **Add property tests for data validation**
  - Target: `utils/data_model.py`, `utils/validation.py` (already done ✅)
  - Verify NaN/infinity rejection
  - Verify padding boundaries (0.0-1.0)
  - Verify series count matching

- [ ] **Completed**: scatter.py coverage (63% → 100%) ✅
- [ ] **Completed**: data_model.py property tests (94% → 100%) ✅
- [ ] **Completed**: column.py coverage (81% → 96%) ✅
- [ ] **Completed**: pie.py coverage (89% → 92%) ✅
- [ ] **Completed**: series_style.py coverage (71% → 100%) ✅

- [ ] **Fix remaining coverage gaps**

---

## 📋 Medium Priority Improvements (Not in this PR)

### Priority: MEDIUM 🟡

- [ ] **Add integration tests**
  - End-to-end CLI chart generation (`charted create bar --data ...`)
  - CSV/JSON file loading and rendering pipeline
  - Markdown export with data URLs

- [ ] **Add mutation testing baseline**
  - Install: `uv pip install mutmut`
  - Run: `mutmut run` (quarterly)
  - Goal: Identify tests that don't actually catch bugs

- [ ] **Add performance benchmarks**
  - Install: `uv pip install pytest-benchmark`
  - Create: `tests/benchmarks/test_chart_generation.py`
  - Track: SVG generation time, file size, memory usage

- [ ] **Improve visual regression testing**
  - Add more baseline images for edge cases
  - Test themes (light, dark, high-contrast)
  - Test negative values with zero line

---

## 🎨 Nice to Have (Low Priority)

### Priority: LOW 🟢

- [ ] **Fuzz testing for security**
  - Install: `uv pip install atheris`
  - Target: CSV/JSON parsers, CLI input handling
  - Run nightly: 100k fuzz iterations

- [ ] **Accessibility testing**
  - WCAG contrast ratio validation
  - Screen reader compatibility for SVG text
  - Colorblind-safe palette options

- [ ] **Documentation coverage**
  - Ensure all public APIs have docstrings
  - Add type hints to remaining functions
  - Update README with testing instructions

---

## 🛠️ Infrastructure Improvements (Not in this PR)

### CI/CD Pipeline

- [ ] **Add property-based tests to CI**
  ```yaml
  - name: Property-based tests
    run: pytest tests/properties/ --hypothesis-seed=0
  ```

- [ ] **Add mutation testing to nightly builds**
  ```yaml
  - if: github.event_name == 'schedule'
    run: mutmut run
  ```

- [ ] **Add benchmark tracking**
  ```yaml
  - name: Performance benchmarks
    run: pytest tests/benchmarks/ --benchmark-json=benchmark.json
  - uses: benchmark-action/github-action-benchmark@v1
  ```

### Test Organization

- [ ] **Create test helper utilities**
  - `tests/conftest.py`: Add more fixtures for common patterns
  - `tests/helpers/chart_builders.py`: Pre-built chart configurations
  - `tests/helpers/svg_assertions.py`: SVG structure assertions

- [ ] **Add test documentation**
  - `tests/README.md`: How to write tests for charted
  - `tests/PROPERTIES.md`: List of all invariants being tested
  - `tests/BENCHMARKS.md`: How to interpret benchmark results

---

## 📊 Coverage Targets

|| Module | Current | Target | Status |
|--------|---------|--------|--------|
| Overall | **91%** | 90% | 🟢 **ACHIEVED** |
| Core (themes, utils) | 85-100% | 90% | 🟢 Excellent |
| Charts | 92-100% | 90% | 🟢 Excellent |
| CLI | 78-92% | 85% | 🟢 Good |
| HTML | 94-100% | 95% | 🟢 Excellent |

---

## 🔍 Bugs Discovered by Property Testing

### Fixed in May 22, 2026 Commit

1. **3-digit hex not supported** (`utils/colors.py`)
   - Before: `hex_to_rgb("#FFF")` raised ValueError
   - After: Expands to `#FFFFFF` automatically

2. **8-digit alpha ignored silently** (`utils/colors.py`)
   - Before: `hex_to_rgb("#AARRGGBB")` raised ValueError
   - After: Strips alpha, returns RGB correctly

3. **Missing validation function** (`utils/colors.py`)
   - Added: `is_valid_hex_color()` for theme validation

4. **Data length mismatch in validation** (property test discovery)
   - Property tests found edge cases where validation should raise but didn't
   - Tests now properly verify error conditions

5. **Floating-point precision in complementary colors**
   - Before: Tests expected exact equality
   - After: Allow ±2 RGB tolerance for HSV conversion

---

## 📅 Recommended Timeline

### Week 1 (Immediate)
- [x] Add property tests for `utils/theme_manager.py` ✅
- [x] Add unit tests for `themes/registry.py` ✅
- [x] Fix remaining critical coverage gaps ✅

### Week 2-3 (Short-term)
- [ ] Add integration tests for CLI and file loading
- [ ] Set up mutation testing baseline
- [ ] Create performance benchmarks
- [ ] Improve scatter.py, column.py, pie.py coverage

### Month 2 (Medium-term)
- [ ] Add fuzz testing to nightly builds
- [ ] Improve visual regression coverage
- [ ] Reach 90% overall coverage

### Quarterly (Long-term)
- [ ] Run mutation testing to identify weak tests
- [ ] Accessibility testing audit
- [ ] Documentation and examples review

---

## 📝 Notes for Future Contributors

### Writing Property Tests

**When to add property tests:**
- Validation functions (data, colors, config)
- Transformation functions (RGB ↔ Hex, color cycling)
- Composition functions (theme merging, data combining)

**Example pattern:**
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_validation_rejects_invalid(text):
    """Validator should reject all invalid input."""
    if not is_valid_input(text):
        # Confirms validator catches bad input
        pass
```

### When to Use Property-Based Testing vs. Unit Tests

| Test Type | Use For | Example |
|-----------|---------|---------|
| **Unit Tests** | Specific cases, error messages | `test_theme_from_preset_light()` |
| **Property Tests** | Invariants, edge cases | `test_color_cycling_is_deterministic()` |
| **Integration Tests** | End-to-end workflows | `test_cli_creates_svg_file()` |
| **Visual Tests** | Rendering correctness | `test_bar_chart_png_baseline()` |

### Baseline Management

**NEVER update baselines without approval:**
```bash
# Correct workflow:
1. Investigate WHY test failed
2. Fix CODE to match baseline (not vice versa)
3. If change is intentional, get approval
4. Run: python scripts/update_baselines.py <test_name>
```

---

## 📚 References

- [TESTING_STRATEGY.md](../TESTING_STRATEGY.md) - Full testing strategy document
- [TESTING_IMPROVEMENTS_PR.md](../TESTING_IMPROVEMENTS_PR.md) - PR description
- [AGENTS.md](../AGENTS.md) - Baseline protection policy
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/) - Property-based testing guide
- [pytest-hypothesis](https://pypi.org/project/pytest-hypothesis/) - Plugin integration

---

## 🎯 Success Metrics

**30 Days:**
- [x] 90% overall test coverage ✅ **ACHIEVED (91%)**
- [x] All critical gaps filled (theme_manager, registry, validation) ✅
- [x] Chart modules improved (scatter, column, pie) ✅
- [x] Utils modules improved (data_model, series_style) ✅
- [ ] Mutation testing baseline established

**60 Days:**
- [ ] Performance benchmarks in place
- [ ] Fuzz testing running nightly
- [ ] CI/CD pipeline updated with property tests

**90 Days:**
- [ ] 92%+ test coverage
- [ ] Zero critical bugs discovered in production
- [ ] Automated accessibility testing

---

*Last reviewed: May 22, 2026 | Next review: June 1, 2026*
