# Security Policy

## Supported versions

Security fixes are applied to the current minor release line. Older versions
do not receive backported fixes; upgrade to the latest 1.1.x release.

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| < 1.1.0 | :x:                |

## Reporting a vulnerability

Please do not open a public GitHub issue for a security vulnerability.

Report it privately through GitHub's private vulnerability reporting:

1. Go to the repository's Security tab.
2. Click "Report a vulnerability".
3. Fill in what you found, how to reproduce it, and the impact.

This opens a private security advisory visible only to the maintainers. If you
can suggest a fix, include it, but it is not required.

We will review the report, confirm the issue, and work on a fix. Once a fix
ships, we publish a security advisory on GitHub and credit the reporter unless
they ask us not to.

## Notes for users

Charted produces SVG output. If you render that SVG in a browser, treat the
input data the same way you would treat any other untrusted input, since
attacker-controlled labels or values can end up in the markup. Validate or
sanitize CSV and other data sources before charting them.
