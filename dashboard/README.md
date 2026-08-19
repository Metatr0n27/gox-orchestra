# GOX Visual Control Room

Purpose: give the strategist a visual, non-terminal view of the entire GOX execution system.

The dashboard should surface:

- Revenue: verified earned, verified received, pending payout, and time-to-cash.
- Agent activity: Scout, Verifier, Operator, QA, Blocker Resolver, Human Gate Router, Revenue Controller, Auditor, Learning Agent.
- Runtime health: Hermes Agent, optional OpenClaw, GOX Control Plane, GOX Worker.
- Task pipeline: NEW -> VERIFIED -> IN PROGRESS -> QA -> SUBMITTED -> PAID.
- Blockers: exact blocker, owner, age, what was tried, and smallest required action.
- User actions: a dedicated red panel containing only unavoidable human steps.
- Failures: recent failed tasks and retry count.
- Evidence: links or IDs proving submission, payout, or completion.

Traffic-light semantics:

- GREEN = verified healthy/completed/paid.
- ORANGE = in progress or waiting on an external system.
- RED = blocked, failed, or user action required.
- GRAY = idle/not configured.

The primary view should be readable on a phone and require no shell knowledge. The operator should be able to understand the system in under 10 seconds.
