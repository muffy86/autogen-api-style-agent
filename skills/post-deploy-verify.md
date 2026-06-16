# Skill: post-deploy-verify
*Confirm a deployment is healthy before walking away.*

## Purpose
Use this skill immediately after a production deploy, a rollback, or a configuration change in production. The goal is to prove the system is healthy with evidence from health checks, critical flows, logs, configuration, and baseline metrics instead of trusting pipeline green lights alone. This skill closes the loop between “deployed” and “actually working.”

## When to invoke
- Immediately after any production deployment.
- Immediately after a rollback completes.
- After changing production config or secrets.
- When on-call needs evidence that a deploy is stable before standing down.

## Inputs
- Deploy URL or service hostname.
- Previous deploy SHA or tag for baseline comparison.
- Health endpoint path.
- List of three critical user flows.
- Links to logs and metrics dashboards.

## Steps
1. Hit the health endpoint.
   - Expect HTTP `200` and the current commit SHA in the payload.
   - Fail fast if the endpoint is unavailable or returns the wrong build metadata.
   - Use:
     ```bash
     curl -fsS https://<host>/health
     ```

2. Exercise three canonical user flows.
   - List each flow by name and expected result before testing it.
   - Use API requests, browser automation, or CLI tooling that matches real user behavior.
   - Use:
     ```bash
     curl -fsS -X POST https://<host>/auth/login
     curl -fsS https://<host>/api/items
     curl -fsS -X POST https://<host>/api/items
     ```

3. Tail production logs for five to ten minutes.
   - Scan for new error signatures, `5xx` spikes, and unhandled exceptions.
   - Prefer the platform CLI or workflow log export over screenshots alone.
   - Use:
     ```bash
     gh run view <run-id> --log
     docker compose logs --tail=200
     ```

4. Verify environment configuration.
   - Use a safe debug or config endpoint that exposes non-secret keys only.
   - Confirm required flags, region settings, and backing service endpoints are loaded.
   - Use:
     ```bash
     curl -fsS https://<host>/config
     ```

5. Compare baseline metrics.
   - Check error rate and p95 latency against the previous deploy window.
   - Capture screenshots or exported panels that show the before-and-after comparison.

6. Confirm no regression against the previous deploy.
   - Re-run the same three flows and compare outputs, status codes, and timings to the prior baseline.
   - If behavior changed intentionally, confirm the change matches the release notes.

7. Record results in the deploy thread.
   - Post the commit SHA, health result, flow results, error-rate delta, latency delta, and screenshots.
   - Make the status explicit: healthy and standing down, or unhealthy and escalating.
   - Use:
     ```text
     Deploy SHA: <sha>
     Health: 200
     Flow 1: pass
     Flow 2: pass
     Flow 3: pass
     Error rate delta: <value>
     p95 latency delta: <value>
     ```

## Success criteria
- [ ] `/health` returns `200` with the expected commit SHA.
- [ ] All three critical flows return the expected responses.
- [ ] No new error signatures appear in logs during the observation window.
- [ ] Required non-secret environment configuration is present.
- [ ] Error rate remains within ±10% of the previous deploy baseline.
- [ ] p95 latency remains within ±15% of the previous deploy baseline.
- [ ] Results are posted to the deploy thread with screenshots or equivalent evidence.

## Failure modes
- The health endpoint is green but a user flow is broken. Trigger rollback through the release workflow immediately.
- Error rate spikes after deploy. Capture a log excerpt, declare the deploy unhealthy, and start incident response.
- A required environment variable is missing. Update the platform secret or config, redeploy, and re-run verification.
- Baseline metrics are unavailable. Use the most recent stable window, note the gap, and keep monitoring longer.

## Handoff
Leave verification evidence in the deploy thread with a clear healthy or unhealthy verdict. If the deploy is healthy, on-call can stand down; if not, the next agent should begin rollback or incident response with the captured evidence.
