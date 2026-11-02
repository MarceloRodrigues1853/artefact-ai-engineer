# Project workflow

- Explain each development milestone and the user's test results in Portuguese:
  what changed, why, what the output means, and relevant limitations.
- Write delivery documentation and commit messages in simple English.
- Present each completed milestone for review before staging or committing.
- Do not stage, commit, push, create PRs, merge, publish, deploy or submit the
  challenge without the user's explicit authorization for that specific action.
- Commit authorization does not authorize pushing or other external operations.

## Commit message format

Use a short Conventional Commit title, then a blank line and a structured body.
Include only sections that apply to the actual changes:

```text
feat: short description of the milestone

Implemented:
- New behavior or capabilities.

Changed:
- Updates to existing behavior or documentation.

Removed:
- Features or files actually removed.

Validation:
- Checks performed and their actual results.
```

- Choose the appropriate type, such as feat, fix, docs, test or chore.
- Omit empty sections; do not invent removals or successful checks.
- Describe real progress; never simulate retrospective commits.
