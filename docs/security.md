# Security review

## Threat model

- Prompt injection in `SKILL.md` or references.
- Token leakage through logs or committed configuration.
- Arbitrary command execution through media filenames or user input.
- Network exfiltration through configurable endpoints.
- Untrusted binary or image payloads.
- Unauthorized third-party Reel acquisition.

## Controls

- All nine skill directories pass the local Skill Security Auditor with zero findings.
- Media commands use `subprocess.run` with argument arrays and never `shell=True`.
- The Reel pipeline accepts local files and an explicit permission basis; no downloader is included.
- Meta tokens are read from environment variables, URL-log redaction is tested, and Graph hosts are allowlisted to `graph.instagram.com` or `graph.facebook.com`.
- The OpenAI image adapter decodes the documented base64 response with strict validation and rejects bytes without a supported image signature before writing.
- `.env`, private data, media, generated outputs, and common secrets are excluded from Git.
- Network adapters are opt-in and document authentication and terms.

## Scanner review

A repository-root static scan flags expected plugin dot-directories, the allowlisted Meta HTTP client, and documented base64 image decoding. These are reviewed architectural capabilities, not hidden behavior. Scanning each distributable `skills/*` directory independently returns PASS. Root scanner findings should still be reviewed whenever network or binary handling changes.

