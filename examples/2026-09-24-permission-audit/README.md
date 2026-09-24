# Audit unnecessary agent permissions

Source: [GitHub local sandboxing announcement](https://github.blog/changelog/2026-09-23-local-sandboxing-in-the-github-copilot-app/), September 23, checked September 24, 2026. Public preview, off by default. Project settings apply to new sessions; `/sandbox on` enables an active local session. Cloud and remote-host sessions are outside this feature.

Run `bash run.sh`. Standard library, offline CPU.

Five synthetic task templates are repeated ten times. The baseline grants every task all six abstract capabilities. The intervention grants exactly each task's assumed requirements. The measured headline is unused baseline grant instances divided by total baseline grant instances. The scoped audit checks that the constructed grant sets match the assumptions.

This measures over-allocation in a synthetic fixture, not security improvement, exploitation probability, Copilot behavior or operating-system enforcement. Labels are not product configuration keys. Repetition does not create independent observations. Requirements must be audited against real tasks before applying a policy. Nothing in the script changes permissions on the user's machine.
