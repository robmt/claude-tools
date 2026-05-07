# At-bat watcher (main-agent step 6, watchAtBat path)

The main `at-bat` agent reads this file at step 6 ONLY when
`watchAtBat: true` was in the resolved config. The default path
(no watcher) is a foreground subagent spawn and is described
inline in SKILL.md.

The watcher gives the main agent (and the user, by escalation)
in-flight visibility into a long-running at-bat. It uses
`Monitor` against the at-bat file's `## Progress` section, plus
a parallel runtime-ceiling check.

## Triggers the watcher emits on

- **Thrash signal in a Progress line.** The subagent appends a
  line containing one of: `attempt 3+`, `still failing`,
  `reverting`, `going in circles`, `stuck`.
- **Runtime ceiling.** The at-bat has been running longer than
  the configured ceiling (default 30 min).

The watcher does NOT emit on staleness (no recent Progress line) -
that was a deliberate design choice. A subagent thinking deeply
between Edits is not a problem; thrashing or steady-but-too-long
is.

## Procedure

1. **Stamp the start time.** Append a single line to the at-bat
   file's `## Progress` section:

   ```
   Started: <ISO 8601 timestamp, e.g. 2026-05-07T14:02:11>
   ```

   Use Edit (or a small bash redirect) - do not rewrite the
   whole file. Capture the unix-seconds equivalent for the
   Monitor command.

2. **Spawn the subagent in the background.** Use the Agent tool
   exactly as the foreground path describes (subagent prompt
   built from `subagent-prompt.md`, the same brief and body),
   but pass `run_in_background: true`. Capture the task id from
   the tool result.

3. **Start the Monitor.** Use the Monitor tool with this command
   (substitute `<ABFILE>` with the absolute at-bat file path,
   `<START_TS>` with the unix start time from step 1, and
   `<CEILING_SEC>` with `30 * 60` unless the user has overridden
   `watchCeilingSec` in config):

   ```bash
   ABFILE="<ABFILE>"
   START_TS=<START_TS>
   CEILING_SEC=<CEILING_SEC>
   prev_size=0
   ceiling_emitted=0
   while true; do
     NOW=$(date +%s)
     ELAPSED=$((NOW - START_TS))
     if [ "$ceiling_emitted" -eq 0 ] && [ "$ELAPSED" -ge "$CEILING_SEC" ]; then
       echo "ceiling: at-bat has run ${ELAPSED}s (ceiling ${CEILING_SEC}s)"
       ceiling_emitted=1
     fi
     cur_size=$(stat -c %s "$ABFILE" 2>/dev/null || echo 0)
     if [ "$cur_size" -gt "$prev_size" ]; then
       tail -c +$((prev_size + 1)) "$ABFILE" 2>/dev/null \
         | grep -iE --line-buffered '(attempt [3-9]|attempt [1-9][0-9]+|still failing|reverting|going in circles|stuck)' \
         || true
       prev_size=$cur_size
     fi
     sleep 30
   done
   ```

   Set `description` to `at-bat NNN watcher` (substitute the
   counter) so notifications are self-explanatory. Use
   `persistent: true` - the watcher runs until the at-bat
   completes, not for a fixed timeout. Capture the monitor task
   id.

4. **Wait passively for the subagent's completion notification.**
   Do NOT poll, sleep, or call TaskOutput speculatively. The
   harness sends a `<task-notification>` when the background
   subagent exits; that is the resume signal. While waiting,
   Monitor events arrive as in-conversation notifications - see
   step 5 for what to do with them.

5. **Handle Monitor events as they arrive.** Each line emitted
   by the watcher script becomes a notification in your stream.
   For each one:

   - **Thrash signal line** (matches the grep above): send a
     PushNotification to the user. Body: `at-bat NNN may be
     thrashing: <line>`. Keep it under 200 chars. Do NOT
     interrupt the subagent (no TaskStop) - the subagent's own
     thrashing stop trigger should fire and return
     `approach_unclear`. The user's notification is so they can
     intervene early if they want.
   - **Ceiling line** (`ceiling: ...`): send a PushNotification.
     Body: `at-bat NNN past runtime ceiling: <line>`. Again do
     NOT interrupt - this is informational. The subagent finishes
     when it finishes; the user decides whether to wait or stop.

   Either way, log the event in your own working memory so you
   can mention it in the eventual hand-back to lineup. Do not
   write to the at-bat file from the main agent during the run -
   the subagent owns the Progress section.

6. **On the subagent's task-notification:**

   - Stop the Monitor: `TaskStop` with the monitor task id.
   - Fetch the subagent's report: `TaskOutput` with the subagent
     task id, `block: true`. The result is the structured report
     defined in `subagent-prompt.md`. For local_agent tasks, use
     the Agent tool result fields - do NOT Read the .output file
     (it's a transcript symlink and will overflow context).
   - Append a closing line to the at-bat's `## Progress`:
     `<HH:MM> finished: <status>` (e.g. `14:31 finished: ok`).
     This is the only Progress write the main agent does; all
     other entries belong to the subagent.

7. **Proceed to SKILL.md step 7** with the report. From here on
   the flow is identical to the foreground path.

## Failure modes

- **Monitor command fails to start.** Continue without the
  watcher - the subagent's own stop triggers still apply. Log
  one line in your eventual hand-back: `Watcher failed to
  start: <error>; ran without it`. Do not block the at-bat.
- **Subagent task-notification never arrives** within a sane
  bound (the harness handles this; you should not poll). If the
  user interrupts the session, the watcher's persistent flag
  means it dies with the session - acceptable.
- **`watchAtBat` was true but no `Monitor` tool is available**
  (older harness). Same as the start-failure case: continue
  foreground, log one line in the hand-back.

## Why these choices

- **Background spawn + Monitor** is the native way to give the
  main agent in-flight visibility into a subagent. CronCreate
  cannot fire mid-query, so a cron-based watcher would be silent
  during exactly the window we care about.
- **No staleness trigger.** A subagent that's reading code
  carefully looks identical to a stuck one if you only watch
  file mtime. Thrash signals come from the subagent's own words;
  the runtime ceiling comes from the clock. Both are signal, not
  noise.
- **No mid-flight interrupt by default.** The subagent's own
  thrashing stop trigger is the primary mechanism; the watcher
  is a backstop that informs the user. Interrupting from the
  main agent would race the subagent's own bail-out and lose its
  report.
