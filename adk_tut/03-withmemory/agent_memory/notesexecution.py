"""
Notes taking application which uses persistent SQLLITE memory 
Based on the user input will decide which tool to call which updates the state
"""

from dotenv import load_dotenv
load_dotenv()

import  uuid
import asyncio

from google.adk.sessions import DatabaseSessionService
from notesagent import memory_agent
from google.adk.runners import Runner
from google.genai import types


# Using SQLite database for persistent storage
db_url = "sqlite:///./my_session.db"
session_service = DatabaseSessionService(db_url=db_url)

async def main():

    APP_NAME ="notes"
    USER_ID ="jinu3"

    # Check for existing sessions for this user
    existing_sessions = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    print("Existing Sessions", existing_sessions)

    # If there's an existing session, use it, otherwise create a new one
    if existing_sessions and len(existing_sessions.sessions) > 0:
        # Use the most recent session
        SESSION_ID = existing_sessions.sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
    else:
        # Create a new session with initial state

        initial_state = {
            "user_name": USER_ID,
            "reminders": [],
        }

        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session: {SESSION_ID}")

    # Create a new Runner 

    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    print("Type your question (or 'quit' to exit):")

    while True:

        session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            session_id=SESSION_ID
        )

        print("Session state BEFORE", session.state)


        user_text = input("You: ").strip()
        if user_text.lower() == 'quit':
            print("\nInterrupted. Goodbye!")
            break

        #Pass on the messages using the types 
        new_message = types.Content(
            role="user", parts=[types.Part(text=user_text)]
        )

        # Create the runner with the userId, session and new message
        trigger_runner = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=new_message,
        )

        # Trigger the runner with the userId, session and new message and wait for the final response. 
        async for event in trigger_runner:
            print("="*50)
            print("Event Content", event)     
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(f"Final Response: {event.content.parts[0].text}")


    session = await session_service.get_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )

    # Log final Session state
    print("=== Final Session State ===")
    for key, value in session.state.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())