import json
import os
import re
from datetime import date
from typing import List

import uvicorn
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="AI Meeting Insight Extractor")

DEADLINE_PATTERN = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")  # DD/MM/YYYY


def assess_deadline(days_left: int) -> tuple[str, str]:
    """Map the number of days left to a risk level and a management plan."""
    if days_left < 0:
        return (
            "High - The deadline has already passed. Re-plan immediately and agree a new date.",
            "Escalate to the project lead. Re-scope or renegotiate the deadline.",
        )
    if days_left <= 3:
        return (
            "High - The deadline is very close. Immediate action is required. "
            "Assign extra resources and prioritize this task in daily stand-ups.",
            "Assign more team members. Schedule daily stand-ups. Consider scope reduction.",
        )
    if days_left <= 7:
        return (
            "Medium - The deadline is approaching soon. Progress should be monitored "
            "closely. Maintain steady pace and consider small check-ins mid-week.",
            "Keep task visible in sprint. Review progress every two days. Ensure resource availability.",
        )
    return (
        "Low - The deadline is comfortably distant. Continue at regular pace. "
        "Weekly check-ins are sufficient to stay on track.",
        "Track casually. Weekly progress check is enough.",
    )


def build_risk_report(data: str, today: date | None = None) -> str:
    """Find every DD/MM/YYYY date in `data` and assess the risk for each one."""
    today = today or date.today()
    lines = []
    for day, month, year in DEADLINE_PATTERN.findall(data):
        try:
            deadline = date(int(year), int(month), int(day))
        except ValueError:  # e.g. 31/02/2026
            continue
        days_left = (deadline - today).days
        risk, plan = assess_deadline(days_left)
        lines.append(
            f"Deadline {deadline.isoformat()} ({days_left} days left)\n"
            f"Risk strength: {risk}\nManagement Plan: {plan}"
        )
    if not lines:
        return "No valid DD/MM/YYYY deadline found. Risk: Low. Track casually."
    return "\n\n".join(lines)


@function_tool
def risk_assessment(data: str) -> str:
    """Analyze every deadline in the text (DD/MM/YYYY) and assess the risk of each, with a management plan."""
    return build_risk_report(data)


class Database(BaseModel):
    key_points: List[str] = Field(description="List of important points")
    minutes_of_meeting: List[str] = Field(description="Note the minutes of meeting")
    summary: str
    solutions: List[str] = Field(description="Solutions to the problems being raised")
    quiz_questions: List[str] = Field(description="Questions and answers that can be done from the data provided")
    todo_list: List[str] = Field(description="What should be done and how?")
    risk_assessment: str = Field(description="What are the risks associated to the tasks?")


assistant = Agent(
    name="Assistant",
    instructions=(
        "You are an AI assistant that extracts structured information from meeting notes. "
        "If you detect any deadlines in the format DD/MM/YYYY, use the `risk_assessment` tool to assess project risk. "
        "For the questions that can be asked you also provide the answers that can be given as response."
    ),
    model=os.getenv("AI_MODEL", "gpt-4o-mini"),
    tools=[risk_assessment],
    output_type=Database,
)


@app.get("/AI-response/", response_model=Database)
async def main(prompt: str):
    """Send meeting notes as `prompt`; get structured insights back."""
    response = await Runner.run(assistant, prompt)
    return response.final_output


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
