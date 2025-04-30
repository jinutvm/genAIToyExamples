from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig, Controller
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import streamlit as st
import json

import asyncio

# Configure the browser to connect to your Chrome instance with our id
browser = Browser(
    config=BrowserConfig(
        browser_binary_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
    )
)

# Define the structured output 
class Post(BaseModel):
    user : str = Field(...,description="user name provided in Linkedin ")
    role : str = Field(...,description="Role provided the user in Linkedin")
    post : str = Field(...,description="Detailed post by the user")
    summary: str = Field(...,description="Provide a summary about the what is in the post")

class Posts(BaseModel):
    posts: List[Post]

controller = Controller(output_model=Posts)

llm = ChatAnthropic(
    model_name="claude-3-5-sonnet-20240620",
    temperature=0.0,
    timeout=100, # Increase for complex tasks
)

initial_actions = [
    {'open_tab':{'url':'https://www.linkedin.com/feed/'}}
]

# Browser will be ensure my browser will be used. 
# Controller will ensure the structured output 
#  
async def linkedin_feed(user_linkedin_task: str):
    agent = Agent(
        task=user_linkedin_task,
        llm=llm,
        browser=browser,
        controller=controller,
        initial_actions=initial_actions
    )
    result = await agent.run()
    await browser.close()
  
    return {"model_actions":result.model_actions(), "final_result":result.final_result()}

if __name__ == '__main__':

    print("=====Linkedin Feed Extractor=====")
    print("Provide the task to be performed")
    user_linkedin_task = input(">>")
    # user_linkedin_task = "Look at the linkedin feed and pick up the latest 2 posts and extract name and designation of the person who posted, along with the visible post and provide an overall summary"
    response = asyncio.run(linkedin_feed(user_linkedin_task))

    # model_action_dict = json.loads(response['model_actions'])
    model_actions=response['model_actions']
    final_result = response['final_result']
    # final_result = json.loads(response['final_result'])

    # model_actions = [{'scroll_down': {}, 'interacted_element': None}, {'extract_content': {'goal': 'Extract information from the latest 2 posts including name, designation, post content, and provide a summary', 'should_strip_link_urls': True}, 'interacted_element': None}, {'extract_content': {'goal': 'Extract information from the latest 2 non-promoted posts including name, designation, post content, and provide a summary', 'should_strip_link_urls': True}, 'interacted_element': None}, {'scroll_down': {}, 'interacted_element': None}, {'extract_content': {'goal': "Extract information from Shantanu Ladhwe's post including name, designation, post content, and provide a summary", 'should_strip_link_urls': True}, 'interacted_element': None}, {'scroll_down': {}, 'interacted_element': None}, {'extract_content': {'goal': "Extract information from Shantanu Ladhwe's post and Miguel Otero Pedrido's post including name, designation, post content, and provide a summary for each", 'should_strip_link_urls': True}, 'interacted_element': None}, {'extract_content': {'goal': "Extract information from Shantanu Ladhwe's post and Miguel Otero Pedrido's post including name, designation, post content, and provide a summary for each", 'should_strip_link_urls': True}, 'interacted_element': None}, {'done': {'success': True, 'data': {'posts': [{'user': 'Shantanu Ladhwe', 'role': 'Author, AI/ML Engineering Manager - Posts on AI Agents, RAG, Recommender Systems, Search & MLOps', 'post': "The post content is not fully visible in the current view. However, there is a comment from Miguel asking 'thanks man! Do you think this applies to UK company as well? Based on your experience', which suggests Shantanu's original post was about some advice or information related to companies, possibly in the context of AI/ML.", 'summary': 'Shantanu Ladhwe, an AI/ML Engineering Manager, made a post that seems to have provided some advice or information about companies, possibly in the context of AI/ML. The exact content is not visible, but it generated engagement and a follow-up question about its applicability to UK companies.'}, {'user': 'Miguel Otero Pedrido', 'role': 'ML Engineer | Founder @ The Neural Maze - Just a guy who builds AI Systems that actually work', 'post': "The post content is not fully visible, but there is a comment from Shantanu Ladhwe saying 'NIce tips !! 🙌', which suggests Miguel's original post contained some helpful tips, likely related to ML or AI systems.", 'summary': 'Miguel Otero Pedrido, an ML Engineer and founder, shared a post that appears to have contained useful tips, probably related to machine learning or AI systems. The post received positive feedback, with Shantanu Ladhwe commenting on the quality of the tips shared.'}]}}, 'interacted_element': None}]
    
    # final_result = """{"posts": [{"user": "Shantanu Ladhwe", "role": "Author, AI/ML Engineering Manager - Posts on AI Agents, RAG, Recommender Systems, Search & MLOps", "post": "The post content is not fully visible in the current view. However, there is a comment from Miguel asking 'thanks man! Do you think this applies to UK company as well? Based on your experience', which suggests Shantanu's original post was about some advice or information related to companies, possibly in the context of AI/ML.", "summary": "Shantanu Ladhwe, an AI/ML Engineering Manager, made a post that seems to have provided some advice or information about companies, possibly in the context of AI/ML. The exact content is not visible, but it generated engagement and a follow-up question about its applicability to UK companies."}, {"user": "Miguel Otero Pedrido", "role": "ML Engineer | Founder @ The Neural Maze - Just a guy who builds AI Systems that actually work", "post": "The post content is not fully visible, but there is a comment from Shantanu Ladhwe saying 'NIce tips !! \ud83d\ude4c', which suggests Miguel's original post contained some helpful tips, likely related to ML or AI systems.", "summary": "Miguel Otero Pedrido, an ML Engineer and founder, shared a post that appears to have contained useful tips, probably related to machine learning or AI systems. The post received positive feedback, with Shantanu Ladhwe commenting on the quality of the tips shared."}]}"""

    actions_list = []
    for model_action in model_actions:
        for model_key, model_value in model_action.items():
            if model_key == 'extract_content':
                for extract_key, extract_value in model_value.items():
                    if extract_key == 'goal':
                        actions_list.append(extract_value) 
                    break
                break
            else:
                actions_list.append(model_key)
                break

    # Actions takens 
    count = 0
    print("Model Actions")
    print("=============")
    for action in actions_list:
        count+=1
        print(count,": ",action)

    
    
final_result_dict = json.loads(final_result)
final_posts = final_result_dict['posts']

# Set display options
# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.expand_frame_repr', False)

# print('final_post',final_posts)
result = pd.DataFrame(final_posts)

def clean_surrogates(text):
    if isinstance(text, str):
        return text.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')
    return text  # fallback for non-str types

for index, row in result.iterrows():
    print("-" * 50)
    print(f"User: {clean_surrogates(row['user'])}")
    print(f"Role: {clean_surrogates(row['role'])}")
    print(f"Post: {clean_surrogates(row['post'])}")
    print(f"Summary: {clean_surrogates(row['summary'])}")

print("-" * 50)

# def clean_text(text):
#     return text.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')



# for index, row in result.iterrows():
#     print(f"User: {clean_text(row['user'])}")
#     print(f"Role: {clean_text(row['role'])}")
#     print(f"Post: {clean_text(row['post'])}")
#     print("-" * 50)
    
# for index, row in result.iterrows():
#     print(f"User: {row['user']}")
#     print(f"Role: {row['role']}")
#     print(f"Post: {row['post']}")
# print(f"Summary: {row['summary']}\n{'-'*50}")