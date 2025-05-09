# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of Charted seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email at [INSERT SECURITY EMAIL] with the following information:

1. Description of the vulnerability
2. Steps to reproduce the issue
3. Potential impact
4. Suggested fix (if any)

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

After the initial reply to your report, we will send you a more detailed acknowledgment and begin working on a fix. We will keep you informed of the progress toward a fix and full announcement, and may ask for additional information or guidance.

### Disclosure Policy

When we release a security fix, we will:

1. Publish a security advisory on GitHub
2. Update this document with the fix version
3. Announce the fix in our changelog
4. Give credit to the reporter (if desired)

### Security Best Practices

When using Charted, please be aware of the following:

- Charted generates SVG files. Always validate SVG output before deploying to production.
- When loading CSV data, ensure the source is trusted to avoid injection attacks.
- Keep your dependencies up to date using `uv update`.
