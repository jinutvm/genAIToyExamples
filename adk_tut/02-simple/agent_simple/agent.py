from google.adk.agents import Agent

from dotenv import load_dotenv
load_dotenv()

"""
Different conditions below 
1. Create an Agent which can invoke a tool. 
2. Create an Agent which can invoke a self declared tool. 
3. Create an Agent with structured output. 
"""

"""
### 1 Create an Agent which can invoke a tool. 
Here we are using google_search which is an inbuilt tools 
We could also make our own tools 
"""


# from google.adk.tools import google_search

# root_agent = Agent(
#     name="search_agent",
#     model="gemini-2.0-flash",
#     description="Search Web for information",
#     instruction="""You are a helpful assistant that can use the following tools:
#     - google_search""",
#     tools=[google_search]
# )


"""
### 2 Create an Agent which can invoke a self declared tool. 

"""
# def word_counter(input: str) -> dict:
#     """
#     Get the input and provide the word count as a response 
#     """
#     words = input.split(" ")
#     return {"total_words": len(words)}


# root_agent = Agent(
#     name="wordcount_agent",
#     model="gemini-2.0-flash",
#     description="Conver the message to precise and count the words in incoming and outgoing messages",
#     instruction="""When a user sends a message
#     1. Count the number of words in the incoming message
#     2. Create a concise, precise message
#     3. Count the number of words in the outgoing message
#     4. Respond with a json structure like 
#         - incoming: {{text, word_count}}
#         - outgoing: {{text, word_count}} 
#     You have access to the following tools:
#     - word_counter""",
#     tools=[word_counter]
# )

"""
### 3 Create an Agent with structured output. 

Eventhough the above could provide json properly while testing, it can fail in multiple execution. Use structured output

1. Define the message format PreciseMessage using pydantic
2. Provide this while calling the agent in output_schema
3. Provide the state to store the results. Give output_key into the agent and it will be stored there.
"""

from pydantic import BaseModel, Field

def word_counter(input: str) -> dict:
    """
    Get the input and provide the word count as a response 
    """
    words = input.split(" ")
    return {"total_words": len(words)}

class PreciseMessage(BaseModel):
    input_message : str = Field(description="The Input message from the user")
    input_word_count : str = Field(description="The word count of the input message")
    output_message : str = Field(description="The Output improved precise message to the user")
    output_word_count : str = Field(description="The word count of the output message")

root_agent = Agent(
    name="wordcount_agent",
    model="gemini-2.0-flash",
    description="Conver the message to precise and count the words in incoming and outgoing messages",
    instruction="""When a user sends a message
    1. Count the number of words in the incoming message
    2. Create a concise, precise message
    3. Count the number of words in the outgoing message
    4. Respond with a json structure like 
        - incoming: {{text, word_count}}
        - outgoing: {{text, word_count}} 
    You have access to the following tools:
    - word_counter""",
    tools=[word_counter],
    output_schema=PreciseMessage,
    output_key="word_counters"
)