# Skill: release-ship
*Ship a verified build to production with a documented rollback.*

## Purpose
Use this skill to move a known-good build from `main` into production without guesswork. The release must be tagged, validated in preview or staging, promoted through the documented deploy path, and paired with a rollback plan that is explicit enough to execute under pressure. Use it for regular release trains, hotfixes, and scheduled deploy windows.

## When to invoke
- A scheduled release window opens.
- A hotfix on `main` needs promotion to production.
- A green build is approved for the next release train.
- The team needs a documented production deploy with rollback notes.

## Inputs
- Commit SHA or tag to ship.
- Target environment, usually production.
- Deploy runbook link or platform command reference.
- On-call owner for the release window.
- Preview or staging URL used for pre-production validation.

## Steps
1. Confirm the target SHA is green.
   - Verify required checks on the exact commit that will ship.
   - Refuse to release a SHA with unknown or pending status.
   - Use:
     ```bash
     gh run list --branch main --limit 5
     gh run view <run-id>
     ```

2. Tag the release.
   - Follow semantic versioning and keep the tag message descriptive.
   - Push the tag before starting the production promotion flow.
   - Use:
     ```bash
     git fetch origin
     git checkout main
     git pull --ff-only
     git tag -a vX.Y.Z -m "release vX.Y.Z"
     git push origin vX.Y.Z
     ```

3. Deploy to preview or staging first.
   - Use the same artifact or SHA that will go to production.
   - Run the smoke script against the preview URL before human validation.
   - Use:
     ```bash
     ./scripts/smoke.sh <preview-url>
     ```

4. Verify three canonical user flows on preview.
   - Exercise login, the primary product action, and logout, or the closest stack-equivalent flows.
   - Record expected results and any screenshots needed for later comparison.

5. Document the rollback path in the release notes draft.
   - Name the previous stable SHA or tag.
   - Include the exact command to redeploy it and who is authorized to trigger the rollback.
   - Use:
     ```bash
     git rev-parse <previous-tag>
     gh run list --workflow deploy.yml --limit 10
     ```

6. Promote to production with the documented deploy mechanism.
   - Use the platform-specific command from the runbook and keep the SHA explicit.
   - Avoid manual UI clicks when a repeatable CLI or workflow trigger exists.
   - Use:
     ```bash
     gh workflow run deploy.yml -f environment=production -f sha=<target-sha>
     flyctl deploy --image <image-ref>
     vercel deploy --prod
     ```

7. Run post-deploy verification.
   - Hit the health endpoint, smoke-test the critical flows, and watch error rate for ten minutes.
   - If any canonical flow fails, stop and execute the rollback path immediately.

8. Publish release notes on GitHub.
   - Include Summary, What Changed, Known Issues, and Rollback.
   - Keep the notes tied to the exact tag and SHA that shipped.
   - Use:
     ```bash
     gh release create vX.Y.Z --generate-notes --notes-file <release-notes.md>
     ```

9. Announce the release.
   - Post the tag, deploy time, and on-call owner in the release channel.
   - Link the release notes and note the monitoring window end time.

## Success criteria
- [ ] The target SHA has all required checks green before tagging.
- [ ] The release tag is pushed and points to the intended commit.
- [ ] Preview or staging smoke checks pass before production promotion.
- [ ] Three canonical user flows pass on preview and again after production deploy.
- [ ] Production `/health` returns `200` after deploy.
- [ ] Error rate is at or below the pre-deploy baseline after ten minutes of observation.
- [ ] Release notes are published and include rollback instructions.
- [ ] The rollback command is documented and was validated against preview or staging.
- [ ] The release announcement names the tag, deploy time, and on-call owner.

## Failure modes
- Preview smoke fails. Abort the release and fix the defect before any production promotion.
- The health endpoint returns `200` but a user flow fails. Roll back immediately using the documented command.
- Release notes are still missing during the window. Block promotion until the notes and rollback instructions exist.
- The deploy mechanism is manual and underspecified. Stop and update the runbook instead of improvising a production change.

## Handoff
Leave a published GitHub release, a production deploy record, and an announcement in the release channel. The next agent should inherit a tagged release with active monitoring assigned to the on-call owner.
