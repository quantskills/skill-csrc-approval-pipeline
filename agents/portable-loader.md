# Portable Loader Prompt

Use this prompt in agents that do not natively discover `SKILL.md` folders.

```text
You have access to a local skill named csrc-approval-pipeline at:
<CSRC_APPROVAL_PIPELINE_ROOT>

When the user asks about CSRC approval pipeline, regulatory announcements, approval progress tracking, or pipeline status reports:
1. Read <CSRC_APPROVAL_PIPELINE_ROOT>/SKILL.md.
2. Consult <CSRC_APPROVAL_PIPELINE_ROOT>/references/api_guide.md for API details.
3. Set environment variables before use:
   - PANDA_DATA_USERNAME
   - PANDA_DATA_PASSWORD
   - PANDA_DATA_BASE_URL (optional, default: http://pandadata.pandaaiquant.com)
4. For pipeline data, run:
   python <CSRC_APPROVAL_PIPELINE_ROOT>/scripts/build.py
5. For validation, run:
   python <CSRC_APPROVAL_PIPELINE_ROOT>/scripts/test.py
6. Use result_json for detailed announcement info.
7. Do not invent data fields, API parameters, or authentication methods.
```
