# Tasker integration

Requirements:
- Tasker
- Termux
- Termux:Tasker plugin

Setup:
1. Import `sovereign-trigger.tsk.xml` into Tasker.
2. Assign the task to a power-button, volume-key, or launcher gesture profile.
3. Update the `x-sovereign-token` value and endpoint if your orchestrator differs.
4. Optionally use `power-button.sh` through Termux:Tasker for clipboard-driven triggers.

Tasker action codes can vary by version. This sample uses code `339` for Tasker 6.x HTTP Request; verify on your device before relying on it.
