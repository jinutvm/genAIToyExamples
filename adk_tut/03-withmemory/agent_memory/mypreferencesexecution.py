"""
Building your preferences memory using InMemory Service.

Application will store your preferences. If you ask anything about you it will respond from the preferences. 
It will also add to the preferences. 

"""



from dotenv import load_dotenv
load_dotenv()

import  uuid
import asyncio
import json

from google.adk.sessions import InMemorySessionService
from mypreferencesagent import preference_managing_agent
from google.adk.runners import Runner
from google.genai import types
from google.adk.events.event import Event, EventActions
from google.adk.sessions.state import State  # gives you USER_PREFIX / APP_PREFIX


import re, json

def clean_json_text(raw: str) -> str:
    """Remove ```json ... ``` fences if present, return pure JSON string."""
    # Strip code fences
    s = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.I)
    s = re.sub(r"\s*```$", "", s, flags=re.I)
    return s

async def main():
    session_service = InMemorySessionService()
    app_name ="notes"
    user_id ="jinu"
    session_id = str(uuid.uuid4())
    initial_state = {
        "user_name": "jinu",
        "user_preferences": """
        """,
    }

    stateful_session = await session_service.create_session(
        app_name=app_name,
        state = initial_state,
        user_id=user_id,
        session_id=session_id
    ) 

    runner = Runner(
        agent=preference_managing_agent,
        app_name=app_name,
        session_service=session_service
    )

    print("Type your question (or 'quit' to exit):")

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() == 'quit':
            print("\nInterrupted. Goodbye!")
            break

        #Pass on the messages using the types 
        new_message = types.Content(
            role="user", parts=[types.Part(text=user_text)]
        )

        # While starting the runner the user id and session id will be used to pick up the respective session from available sessions 
        trigger_runner = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
        )

        # check each of the events happening and wait for final one. is_final_response() will provide this information
        async for event in trigger_runner:
            print("="*50)
            print("Event Content", event)    
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(event.content)
                    raw_text = event.content.parts[0].text
                    json_text = clean_json_text(raw_text)
                    final_response = json.loads(json_text)

                    print(f"Final Response: {final_response['ai_response']}")


        session = await session_service.get_session(
            app_name=app_name, 
            user_id=user_id, 
            session_id=session_id
        )

        print("session state final", session.state)

        # Log final Session state
        print("=== Final Session State ===")
        for key, value in session.state.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
