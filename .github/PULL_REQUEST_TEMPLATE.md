name: Pull Request
description: Submit a pull request
title: "[PR]: "
labels: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for contributing to Charted! Please fill out this template to help us review your PR efficiently.
  - type: textarea
    id: description
    attributes:
      label: Description
      description: Describe your changes
      placeholder: What does this PR do? Why is it needed?
    validations:
      required: true
  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      description: Please confirm the following
      options:
        - label: I have read the [Contributing Guide](CONTRIBUTING.md)
          required: true
        - label: I have added tests that prove my fix is effective or that my feature works
          required: false
        - label: New and existing unit tests pass locally with my changes
          required: true
        - label: I have updated the documentation accordingly
          required: false
        - label: I have added a changelog entry
          required: false
  - type: textarea
    id: testing
    attributes:
      label: Testing
      description: How did you test your changes?
      placeholder: Describe your testing approach and any manual testing performed.
  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots / Examples
      description: If applicable, add screenshots or example outputs.
      placeholder: For UI changes or visual outputs, include examples here.
  - type: dropdown
    id: type
    attributes:
      label: PR Type
      description: What type of change is this?
      multiple: true
      options:
        - Bug fix (non-breaking change that fixes an issue)
        - New feature (non-breaking change that adds functionality)
        - Breaking change (fix or feature that would cause existing functionality to change)
        - Documentation update
        - Code refactoring
        - Performance improvement
        - Build/CI related changes
        - Test related changes
  - type: textarea
    id: additional-context
    attributes:
      label: Additional context
      description: Add any other context about the PR here.
