from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import os
import asyncio, json, datetime


load_dotenv()

app = FastAPI()

@function_tool
def risk_assesment(data: str):
    """Analyze deadline dates in the text and assess risk accordingly. Deadline should be in DD/MM/YYYY format. Provide a risk management plan accordingly"""
    this_data = data.split()
    for prompt in this_data:
        if '/' in prompt:
            if int((prompt.split('/'))[1]) == (datetime.date.today()).month:
                if int((prompt.split('/'))[0]) <= (datetime.date.today()).day + 3:
                    Risk = "High — The deadline is very close. Immediate action is required. Assign extra resources and prioritize this task in daily stand-ups."
                    Plan = "Assign more team members. Schedule daily stand-ups. Consider scope reduction."

                elif int((prompt.split('/'))[0]) <= (datetime.date.today()).day + 7:
                    Risk = "Medium — The deadline is approaching soon. Progress should be monitored closely. Maintain steady pace and consider small check-ins mid-week."
                    Plan = "Keep task visible in sprint. Review progress every two days. Ensure resource availability."
                else:
                    Risk = "Low — The deadline is comfortably distant. Continue at regular pace. Weekly check-ins are sufficient to stay on track."
                    Plan = "Track casually. Weekly progress check is enough."

            elif int((prompt.split('/'))[1]) == (datetime.date.today()).month + 1:
                if int((prompt.split('/'))[0]) <= (datetime.date.today()).day - 27:
                    Risk = "High — The deadline is very close. Immediate action is required. Assign extra resources and prioritize this task in daily stand-ups."
                    Plan = "Assign more team members. Schedule daily stand-ups. Consider scope reduction."
                elif int((prompt.split('/'))[0]) <= (datetime.date.today()).day - 22:
                    Risk = "Medium — The deadline is approaching soon. Progress should be monitored closely. Maintain steady pace and consider small check-ins mid-week."
                    Plan = "Keep task visible in sprint. Review progress every two days. Ensure resource availability."
                else:
                    Risk = "Low — The deadline is comfortably distant. Continue at regular pace. Weekly check-ins are sufficient to stay on track."
                    Plan = "Track casually. Weekly progress check is enough."
            else:
                Risk = "Low"
                Plan = "Track casually. Weekly progress check is enough."

    return f"Risk strength: {Risk}, \nManagement Plan: {Plan}"

class Database(BaseModel):
    key_points: List[str] = Field(description="List of important points")
    minutes_of_meeting: List[str] = Field(description="Note the minutes of meeting")
    summary: str
    solutions: List[str] = Field(description="Solutions to the problems being raised")
    quiz_questions: List[str] = Field(description="Questions and answers that can be done from the data provided")
    todo_list: List[str] = Field(description="What should be done and how?")
    risk_assesment: str = Field(description="What are the risks associated to the tasks?")

assistant = Agent(
    name="Assistant",
    instructions=("You are an AI assistant that extracts structured information from meeting notes. "
                  "If you detect any deadlines in the format DD/MM/YYYY, use the `risk_assesment` tool to assess project risk."
                  "For the questions that can be asked you also provide the answers that can be given as response."),
    model=os.getenv("AI_MODEL", "gpt-4o-mini"),
    tools=[risk_assesment],
    output_type=Database
)

@app.get('/AI-response/')
async def main(prompt):
    response = await Runner.run(assistant, prompt)
    data = response.final_output
    print(f"Response: \n{json.dumps(data.model_dump(),)}")
    return f"Response: \n{json.dumps(data.model_dump(),)}"
if __name__ == "__main__":
    asyncio.run(main())