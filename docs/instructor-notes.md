# Instructor notes

## Before class

Arrange the GHEC/Azure administrators and a reviewer for every learner/team.
Confirm cloud-agent entitlement and policy, App creation/installation, deploy
keys, approved Actions/runners, environment reviewers, regional quota, and ACR
Tasks. If any are unavailable, communicate the required adaptation before class.

Rehearse the full path in a disposable repository/subscription. Choose and
approve an exact supported Argo CD release, install its matching CLI, check
kubectl/AKS version skew, and use enterprise-approved action pins if required.
Budget for two four-vCPU nodes per team plus ACR/task and Actions costs; use
shared instructor-provisioned resources only with explicit namespace/access
isolation and a different cleanup plan.

Cloud policies and agent UI change. The guide's permissions model is the
contract; an old screenshot or obsolete UI label is not.

## Teach the boundaries

| Boundary | Learner should explain |
| --- | --- |
| Intent to implementation | Acceptance criteria constrain the agent; issue text is untrusted input |
| Implementation to merge | Tests plus human review, not agent confidence |
| Merge to artifact | OIDC restricted to `dev` and a registry; no cluster credentials |
| Artifact to desired state | Release PR promotes a digest; App token triggers normal CI |
| Desired state to workload | Argo CD pulls reviewed Git and reconciles it |
| Workload to completion | HTTP evidence links issue, source SHA, digest, Git revision, and actual result |

Avoid selling "fully autonomous production deployment." Humans approve code,
publication, and desired-state promotion. The agent proposes changes and handles
bounded implementation/testing work.

## Facilitation checkpoints

1. At Lab 0, verify CI and gates, and stop unconfigured publish runs.
2. At Lab 1, verify learners are in approved subscriptions and API CIDRs.
3. At Lab 2, emphasize why the Application is deferred until a real digest exists.
4. At Lab 3, ask the learner to find blank/duplicate input edge cases in tests.
5. At Lab 4, ask why `GITHUB_TOKEN`-authored release PRs can lack CI and why the
   App is not a ruleset bypass.
6. At Lab 5, ask why source build SHA and Argo Git revision differ, then require
   a second valid release before rollback.
7. At Lab 6, verify cleanup completed; resource deletion being requested is not
   proof that charges stopped.

## Completion rubric

| Criterion | Evidence |
| --- | --- |
| Intent captured | Issue with exact acceptance criteria and guardrails |
| Agent contribution bounded | Session/IDE evidence, intended code/test diff |
| Quality and governance | Passing checks and independent approvals |
| Secretless build | Environment-scoped federation, registry-only Azure access |
| Immutable promotion | Release PR contains ACR digest and source/build link |
| Actual deployment | Synced/Healthy plus deployed digest and HTTP responses |
| Recovery | Reviewed revert between two valid retained images |
| Hygiene | Cleanup verification and removed temporary access |

## Optional discussion, not additional baseline steps

Discuss staging/production overlays with build-once promotion, a separate GitOps
repository and narrowly scoped App, signed artifact admission, observability,
policy-as-code, and cost controls. Decide whether event-based agent automation
should exist only after defining authorized triggers and input trust boundaries.
