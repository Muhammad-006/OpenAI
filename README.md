# AI Meeting Insight Extractor

A small FastAPI service that turns raw meeting notes into structured output using the OpenAI Agents SDK: key points, minutes, a summary, proposed solutions, quiz questions, a to-do list and a deadline risk assessment.

If the notes contain deadlines written as `DD/MM/YYYY`, the agent calls a custom tool (`risk_assessment`) that works out how many days are left for each deadline and returns a High / Medium / Low risk level with a management plan.

## How it works

```
GET /AI-response/?prompt=<meeting notes>
        │
        ▼
  OpenAI Agent ──(deadline found?)──► risk_assessment tool
        │                              • finds every DD/MM/YYYY date
        │                              • days left = deadline - today
        │                              • overdue or ≤3 days High, ≤7 Medium, else Low
        ▼
  Structured JSON (validated by a Pydantic model)
```

Response fields: `key_points`, `minutes_of_meeting`, `summary`, `solutions`, `quiz_questions`, `todo_list`, `risk_assessment`.

## Run it

Requires Python 3.10+ and an OpenAI API key.

```bash
git clone https://github.com/Muhammad-006/OpenAI.git
cd OpenAI
pip install -r requirements.txt
cp .env.example .env      # then put your OPENAI_API_KEY in .env
python main.py            # serves on http://127.0.0.1:8000
```

Try it at `http://127.0.0.1:8000/docs`, or:

```bash
curl -G "http://127.0.0.1:8000/AI-response/" \
  --data-urlencode "prompt=Sprint review. Login bug blocks release. Fix due 20/10/2026, QA sign-off 30/10/2026."
```

Set `AI_MODEL` in `.env` to use a different model (default: `gpt-4o-mini`).

## Tech

Python · FastAPI · Pydantic · OpenAI Agents SDK · python-dotenv · Uvicorn

## Notes

- The deadline-risk thresholds (3 and 7 days) are simple rules I chose for the demo, not a project-management standard.
- Overdue deadlines are reported as High risk; invalid dates (e.g. `31/02/2026`) are ignored.
- Never commit your `.env` file. It is listed in `.gitignore`.
