# Security policy

## API keys

The repository must never contain an active NVIDIA API key. The application supports two user-controlled methods:

1. Entering the key in the AI EQ panel.
2. Supplying `NVIDIA_API_KEY` through the environment.

On Windows, a user may choose to save the key with Data Protection API (DPAPI). The stored configuration contains an encrypted blob rather than the plain-text key. DPAPI protection is tied to the current Windows user context and is not intended as a portable secret format.

## Reporting a vulnerability

Do not post API keys, personal data, exploit details, or sensitive logs in a public issue. Contact the Connectia-LABS repository owners through a private channel and include:

- Affected version.
- Clear reproduction steps.
- Expected and actual behavior.
- Potential impact.
- A minimal proof of concept when appropriate.

## Supported version

Security fixes target the latest release on the default branch.

## Secret response procedure

When a credential is committed or shared publicly:

1. Revoke it at the provider immediately.
2. Generate a replacement.
3. Remove the value from current files.
4. Review repository history and logs.
5. Assume the exposed credential has been copied.

Removing a key from the latest commit does not make the old key safe; revocation is mandatory.

## External network access

The application may connect to:

- NVIDIA API endpoints for optional AI EQ.
- Radio-Browser servers for station discovery and repair.
- Radio station stream URLs.
- Station logo URLs.
- The configured FFmpeg download source during first-time setup.

Users should review their network, privacy, and organizational policies before enabling these features.
