"""
All previous executions we have used adk web to trigger. That can be for testing. We will show how to implement all activities by
adk web below

1. Sessions Service is where all the sessions are executed.
2. Each Session will have Id, app_name, user_id, last_update_time. Each session is a combination of State and Events
    State - User state at any point of time
    Events - Messages by User, Tool Response and even Agent Response.
3. Runner - Runner is a collection of Session and Available agents. A user response is actioned by a session in runner, which will
    use available agents and execute the same. The agents will use the State in the session and will update after every execution.
"""


from dotenv import load_dotenv
load_dotenv()

import  uuid
import asyncio

"Memory"
# Add the memory. There are Inmemory, DB or VertexAI. This usecase InMemory

async def main():

    #Create session service to store state
    from google.adk.sessions import InMemorySessionService
    session_service = InMemorySessionService()

    "Session - Events and Memory"
    # In ADK Architecture, Session constitues of State and Events. There can be multiple sessions
    # Following fields are used to denote a session - Id, app_name, user_id, last_update_time
    #
    # State - Stores the memory for all the events in this session to use. 
    # All the events will store the results in the state and it could be used by other events. 
    # Events are Messages by User, Tool Response and even Agent Response.

    # Creating a new session iwth the required fields

    app_name ="jinuapp"
    user_id ="jinu"
    session_id = str(uuid.uuid4())
    initial_state = {
        "user_name": "Jinu",
        "user_preferences": """
            I like to play Badminton, Cricket, and Kabaddi.
            My favorite food is South Indian meals and Biryani.
            My favorite TV show is Family Man.
            Love it when people follow and support my YouTube channel.
        """,
    }

    stateful_session = await session_service.create_session(
        app_name=app_name,
        state = initial_state,
        user_id=user_id,
        session_id=session_id
    ) 

    "Runner - Sessions and Available Agents are grouped"
    # In ADK Architecture, Runner is a group which consists of Available Agents and Sessions. Create a runner
    # vairables are agents and session information is shared. Which session to pick up will provided while 
    # runner is triggered.

    from agent import question_answering_agent
    from google.adk.runners import Runner

    runner = Runner(
        agent=question_answering_agent,
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
        from google.genai import types
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
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(event.content)
                    print(f"Final Response: {event.content.parts[0].text}")

    print("==== Session Event Exploration ====")

    # From the available sessions in session service pick up the session using userid, app name and session id
    session = await session_service.get_session(
        app_name=app_name, 
        user_id=user_id, 
        session_id=session_id
    )

    # Log final Session state
    print("=== Final Session State ===")
    for key, value in session.state.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
