# Geneva Loop Engine

A stop-and-go operating architecture inspired by the Geneva mechanism: one controlled movement advances the system exactly one stage, then the system locks, validates, records the result, and only then advances again.

## Core cycle

```text
CAPTURE -> CLASSIFY -> PLAN -> APPROVE -> EXECUTE -> VERIFY -> RECORD -> REPEAT
             ^          |         |          |          |
             |          +--STOP---+----------+----------+
             +-------------------REWORK-----------------
```

Each item is a **work packet**. A packet may represent an email, business problem, payment, customer request, document, order, or automated task.

## Stop-and-go rules

1. **One state transition at a time.** No packet may skip a stage.
2. **Lock before movement.** A packet must satisfy the current stage's exit criteria before advancing.
3. **Idempotent execution.** Re-running the same stage must not create duplicate emails, payments, orders, or records.
4. **Human gates for risk.** Money movement, legal communications, destructive actions, and external publication stop at `APPROVE` unless an explicit policy permits automatic release.
5. **Evidence after every movement.** Every transition records timestamp, actor, input hash, output, and decision.
6. **Failure returns to a known tooth.** Recoverable failures go to `REWORK`; unrecoverable failures go to `HALTED`.
7. **Continuous production without uncontrolled autonomy.** The loop can keep processing queued packets, but every packet remains constrained by policy, limits, and approval gates.

## State definitions

| State | Purpose | Exit condition |
|---|---|---|
| `CAPTURE` | Receive and normalize input | Required fields exist |
| `CLASSIFY` | Determine type, risk, owner, urgency | Classification confidence meets threshold |
| `PLAN` | Produce steps, tools, cost, dependencies | Plan passes policy checks |
| `APPROVE` | Human or policy authorization | Valid approval token exists |
| `EXECUTE` | Perform one bounded action | Action returns a traceable result |
| `VERIFY` | Check result against acceptance criteria | Verification passes |
| `RECORD` | Persist evidence, metrics, and next trigger | Audit record written |
| `REWORK` | Correct a failed plan or execution | New plan is ready |
| `HALTED` | Safe stop requiring intervention | Manual release or cancellation |
| `COMPLETE` | Packet has reached its intended result | Terminal state |

## Architecture

```text
Inputs
  email / forms / APIs / schedules / ledgers
       |
       v
Queue -> State Engine -> Policy Gate -> Worker Adapter
              |               |              |
              v               v              v
          Audit Log       Approval Store   External System
              |                              |
              +---------- Verifier <---------+
                             |
                             v
                       next state / rework
```

## Recommended use patterns

### Email replies

`CAPTURE message -> CLASSIFY intent/urgency -> PLAN response -> APPROVE if sensitive -> EXECUTE draft/send -> VERIFY delivery/thread -> RECORD follow-up date`

### Business solutions

`CAPTURE problem -> CLASSIFY domain/value/risk -> PLAN options -> APPROVE selected option -> EXECUTE smallest test -> VERIFY KPI -> RECORD learning -> REPEAT`

### Money cycles

`CAPTURE obligation/opportunity -> CLASSIFY source/destination/risk -> PLAN transfer or allocation -> APPROVE with limits -> EXECUTE once -> VERIFY settlement -> RECORD ledger entry`

Money movement should never be fully autonomous without transaction limits, allow-listed destinations, reconciliation, fraud checks, and a manual emergency stop.

## Files

- `engine.py` — deterministic state-machine runner.
- `workflow.yaml` — policy and stage configuration.
- `.github/workflows/geneva-loop.yml` — scheduled and manual GitHub Actions runner.

## Local run

```bash
python3 geneva_loop/engine.py --config geneva_loop/workflow.yaml --queue geneva_loop/queue.jsonl
```

The starter runner uses local JSONL files as a transparent audit trail. Production adapters can later connect Gmail, CRM systems, payment providers, databases, or message queues without changing the state model.
