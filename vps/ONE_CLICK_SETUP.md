# GOX VPS — One-Time Setup, Then One Click

The VPS stack can be deployed from GitHub Actions without opening the VPS terminal after the one-time SSH credentials are stored.

## One-time GitHub repository secrets

Repository: `Metatr0n27/gox-orchestra`

Open **Settings → Secrets and variables → Actions → New repository secret** and create:

- `GOX_VPS_HOST` — VPS public IP or hostname.
- `GOX_VPS_USER` — normally `root`, or a sudo-capable user.
- `GOX_VPS_SSH_KEY` — the complete private SSH key authorized on the VPS. Never commit this key to the repository.
- `GOX_VPS_PORT` — optional. Omit when SSH uses port 22.

## One-click deployment

Open **Actions → GOX One-Click VPS Deploy → Run workflow → Run workflow**.

The workflow connects by SSH, downloads the current bootstrap, installs/updates GOX, enables the persistent worker and controller, runs health/routing tests, executes the VPS preflight audit, and fails visibly if verification does not pass.

If deployment fails, the workflow automatically opens a GitHub blocker issue so the failure is tracked.

## Verified success

A deployment is successful only when:

- `gox-worker` is active.
- `gox-control` is active.
- `/var/lib/gox/heartbeat.json` exists.
- the bootstrap health task appears in `done.jsonl`.
- the bootstrap routing task appears in `control/active.jsonl`.
- `vps/preflight.sh` exits successfully.

This deploys the deterministic GOX runtime. External revenue services still require their own legitimate API/account credentials and platform-authorized access. Human-only identity, CAPTCHA, financial authorization, or personal-attestation steps remain human gates and must not be bypassed.
