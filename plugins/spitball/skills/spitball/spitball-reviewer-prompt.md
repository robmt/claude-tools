# Spitball Reviewer Prompt Template

Use this template when dispatching a spitball reviewer subagent.

**Purpose:** Verify the spitball is complete, consistent, and honest about its scope.

**Dispatch after:** Spitball document is written to the configured saveDir.

```
Task tool (general-purpose):
  description: "Review spitball document"
  prompt: |
    You are a spitball reviewer. Verify this document is complete, consistent,
    and honest about what it claims to know.

    **Spitball to review:** [SPITBALL_FILE_PATH]

    ## What to Check

    | Category      | What to Look For |
    |---------------|------------------|
    | Completeness  | TODOs, placeholders, "TBD", incomplete sections |
    | Consistency   | Internal contradictions, conflicting requirements |
    | Clarity       | Requirements ambiguous enough to cause someone to build the wrong thing |
    | Scope         | Focused enough for a single piece of work, not covering multiple independent subsystems |
    | YAGNI         | Unrequested features, over-engineering |
    | Honesty       | Forward plan or speculation written as if it were known. Future phases, milestones, or timelines that have no basis. Mark or remove. |

    ## Calibration

    **Only flag issues that would cause real problems.**
    A missing section, a contradiction, or a requirement so ambiguous it could be
    interpreted two different ways, those are issues. Minor wording improvements,
    stylistic preferences, and "sections less detailed than others" are not.

    Approve unless there are serious gaps that would lead to wasted work.

    ## Output Format

    ## Spitball Review

    **Status:** Approved | Issues Found

    **Issues (if any):**
    - [Section X]: [specific issue] - [why it matters]

    **Recommendations (advisory, do not block approval):**
    - [suggestions for improvement]
```

**Reviewer returns:** Status, Issues (if any), Recommendations
