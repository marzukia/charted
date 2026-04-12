# TODO

## Tasks from FINDINGS.md Analysis

### Immediate Actions (High Priority)

1. **Extract Common Transformation Logic**
   - Extract the common SVG transformation chain to a `base_transform` property in the `Chart` base class
   - This will eliminate duplication across Column, Line, and Scatter charts

2. **Standardize Offset Handling**
   - Create a unified method for calculating position offsets
   - Ensure consistent application across all chart types
   - Address current inconsistency where `y_offsets` is handled differently across chart types

### Long-term Improvements (Medium Priority)

3. **Refactor Axis Implementation**
   - Consider consolidating X and Y axis logic
   - Use composition over inheritance where appropriate
   - Address duplicated patterns in grid lines and axis labels

4. **Documentation Improvements**
   - Add docstrings explaining the expected behavior of each abstract method
   - Create visual documentation of the class hierarchy
   - Document expected behaviors for abstract methods

## Tasks Checklist

- [x] Extract common transformation logic to Chart base class as base_transform property
- [ ] Standardize offset handling across all chart types
- [ ] Refactor axis implementation to consolidate X and Y axis logic
- [ ] Add docstrings for abstract methods and improve documentation
