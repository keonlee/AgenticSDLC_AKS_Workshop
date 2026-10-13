# Lab 3 - Turn a GitHub issue into a reviewed Copilot PR

**Goal:** give the agent a bounded task with measurable acceptance criteria.
**Time:** 40 minutes.

## 1. Understand the baseline

Read `app\server.py`, `app\test_server.py`, and
`.github\copilot-instructions.md`. Run:

```powershell
python -m unittest discover -s app -p "test_*.py" -v
python -m app.server
```

In a second terminal, request `http://localhost:8080/healthz` and `/version`.
The local version is `local`. Stop the server with Ctrl+C before moving on.
The `/api/greeting` route does not exist yet.

## 2. Create the feature issue

In your repository, choose **Issues > New issue > Agent implementation task**.
Use the title **`[Workshop] Add a personalized greeting API`** and fill the form:

**User outcome**

```text
As a workshop attendee, I want a JSON greeting endpoint so I can verify a
Copilot-authored feature after a GitOps release.
```

**Acceptance criteria**

```text
- GET /api/greeting returns HTTP 200 and {"message":"Hello, workshop!"}
  when the name query parameter is absent.
- GET /api/greeting?name=QCell returns HTTP 200 and {"message":"Hello, QCell!"}.
- Decode URL-encoded input and trim leading/trailing whitespace.
- A supplied name must contain 1-40 characters after trimming (Python len).
- An empty/whitespace-only name, a name longer than 40 characters, or more
  than one name parameter returns HTTP 400 and {"error":"invalid name"}.
- GET /api/greeting?name=%20Ada%20 returns {"message":"Hello, Ada!"}.
- A 40-character name is accepted; a 41-character name is rejected.
- Query parameters other than name are ignored.
- Responses retain application/json content type.
- Preserve /, /healthz, /version, and the JSON 404 response.
- Add unit and real HTTP tests covering these cases.
```

Retain the form's scope/guardrails and required evidence. Submit the issue and
record its number. The greeting value is ordinary text in JSON, not HTML.

## 3. Triage before delegating

Have a human check that the issue is unambiguous, contains no secrets, and does
not ask for workflow/identity changes. Inspect the repository instructions with
the agent. Issue text and attachments are task input, not permission to weaken
security boundaries.

The safe workshop trigger is **human assignment after triage**. Do not configure
unrestricted issue-created automation: an untrusted issue must not receive
deployment credentials.

## 4. Start the Copilot cloud agent

Depending on the current GitHub UI, use the issue's **Assignees > Copilot** entry
or the issue's agent/delegate action. Ask it to implement the issue and open a
pull request, using the repository instructions. Availability and wording depend
on license, organization policy, and GitHub rollout.

Follow the session/activity link. Inspect its plan, changed files, commands, and
test results. This is bounded autonomy: the agent edits and tests; humans decide
whether it is correct and may be merged.

If cloud assignment is unavailable, use the fallback below; do not spend the
class trying to circumvent an enterprise policy.

### IDE agent fallback

Open the repository in VS Code, switch to a new feature branch, and select
Copilot's agent mode:

```powershell
git switch -c feature/greeting-api
```

Use this prompt, replacing the issue reference:

```text
Implement the acceptance criteria from issue #ISSUE_NUMBER in this repository.
Read .github/copilot-instructions.md and the app/tests first. Describe your
plan, then make the code and test changes. Keep the app dependency-free.
Do not change CI, Azure identity, Argo CD, or deployment files. Do not deploy
or merge. Run the documented unit/HTTP tests and report actual results.
```

Give the agent the issue body if your IDE cannot fetch it. Review tool permission
requests rather than enabling blanket approvals. After reviewing the diff and
running tests, commit/push the feature branch and open a PR with
`Closes #ISSUE_NUMBER` in its description. This is a local agent-authored PR, not
a claim that a cloud session ran.

## 5. Review and iterate

Open the application PR and check:

1. Only intended app/tests changed; no permissions or deployment edits.
2. Parsing preserves blank values, detects duplicate names, decodes input, and
   measures length after trimming. A convenience parser's defaults can hide
   an invalid blank name.
3. Tests verify both boundaries, exact JSON/status, and HTTP content type.
4. The issue is linked and the test command actually ran.

Request Copilot code review if your policy/license enables it. Read its findings
and ask for targeted corrections; the agent review does not approve the PR.
For example:

```text
@copilot Please add coverage for an explicitly empty name and duplicate name
parameters, and fix any behavior that does not match the issue. Do not change
the deployment or workflows. Rerun tests and report the command/result.
```

Approve any **Approve and run workflows** request GitHub presents for an
agent-authored PR only after inspecting the diff. Do not use `pull_request_target`
to execute agent/PR code with elevated credentials.

## 6. Merge the feature

Wait for CI and the independent human review. Use GitHub's normal merge action.
If the issue auto-closes, add the deployment evidence later; closed means the
feature PR merged, not that the workload has been verified.

Publish is still disabled, so this merge does not yet start an Azure build.
Lab 4 enables it and manually runs the first release from `main`.

**Checkpoint:** issue -> agent session (or documented IDE fallback) -> app PR ->
passing CI -> human merge. Keep the PR URL and source merge SHA.

**References:** [Start Copilot sessions](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/start-copilot-sessions),
[Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review).

**Next:** [Lab 4](04-ci-and-release.md).
