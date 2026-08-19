# GOX Visual Command Center

Goal: give the strategist one visual screen showing what the system is doing without reading code or logs.

## Top row gauges
- VERIFIED REVENUE: earned vs received
- ACTIVE TASKS: count and highest-value task
- BLOCKERS: unresolved count
- USER ACTION: number of unavoidable human gates
- VPS HEALTH: worker/controller/Hermes/OpenClaw state

## Main flow board
Columns:
1. FOUND
2. VERIFIED
3. EXECUTING
4. QA
5. SUBMITTED
6. PAID
7. BLOCKED

Each task card shows:
- source
- task name
- expected pay
- estimated minutes
- score/priority
- assigned agent
- current stage
- last action time
- evidence link/reference

## Agent panel
Show each functional role with one of:
- GREEN = actively working / healthy
- YELLOW = waiting on another internal step
- RED = blocked/error
- BLUE = waiting on the strategist for a mandatory human gate

Roles:
- Opportunity Scout
- Verifier
- Operator
- QA
- Blocker Resolver
- Human Gate Router
- Revenue Controller
- Auditor
- Learning Agent
- Hermes Agent runtime
- OpenClaw communications runtime (optional)

## Blocker panel
Every blocker must show:
- what is blocked
- why
- automatic fixes attempted
- specialist team currently assigned
- whether other lanes are continuing
- smallest exact human action if unavoidable
- direct URL when applicable

## Human-action inbox
Use large one-tap cards. Each card contains:
- ACTION REQUIRED
- service/site
- direct URL
- exactly one instruction
- what success looks like
- screenshot requested after completion

No coding language should be shown to the strategist unless specifically requested.

## Revenue lane
Separate these values visually:
- potential value
- submitted value
- verified earned revenue
- cash actually received

Never merge potential value with earned revenue.

## Health strip
- gox-worker
- gox-control
- Hermes Agent
- OpenClaw
- queue depth
- failed jobs
- heartbeat age

## Primary UX rule
If everything is healthy and no user action is required, the strategist should be able to understand system state in under 5 seconds.
