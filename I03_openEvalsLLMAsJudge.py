from openevals.llm import create_llm_as_judge
from openevals.prompts import CONCISENESS_PROMPT
from I03_constants import MY_CUSTOM_PROMPT
from dotenv import load_dotenv
load_dotenv()

conciseness_evaluator = create_llm_as_judge(
    # prompt=CONCISENESS_PROMPT,
    prompt=MY_CUSTOM_PROMPT,
    model="openai:o3-mini",
)
inputs = "How is the weather in San Francisco?"
outputs = "Thanks for asking! The current weather in San Francisco is sunny and 90 degrees as far as i feel"

eval_result = conciseness_evaluator(
    inputs=inputs,
    outputs=outputs,
)

print(eval_result)


# Using MY_CUSTOM_PROMPT to evaluate objectively

# outputs = "Thanks for asking! The current weather in San Francisco is sunny and 90 degrees"
# Eval response = {'key': 'score', 'score': 0.9, 'comment': "The answer includes an unnecessary introductory phrase ('Thanks for asking!'), which deducts 0.1 from a perfect score of 1.0. Thus, the score should be: 0.9.", 'metadata': None}

# outputs = "Thanks for asking! The current weather in San Francisco is sunny and 90 degrees as far as i feel"
# Eval response = {'key': 'score', 'score': 0.8, 'comment': "The response includes unnecessary phrases: a greeting ('Thanks for asking!') and a hedging remark ('as far as i feel'), which deduct 0.1 each from the initial score of 1.0. Thus, the score should be: 0.8.", 'metadata': None}

# print(CONCISENESS_PROMPT)
# Below is the CONCISENESS_PROMPT prompt
"""
You are an expert data labeler evaluating model outputs for conciseness. Your task is to assign a score based on the following rubric:

<Rubric>
  A perfectly concise answer:
  - Contains only the exact information requested.
  - Uses the minimum number of words necessary to convey the complete answer.
  - Omits pleasantries, hedging language, and unnecessary context.
  - Excludes meta-commentary about the answer or the model's capabilities.
  - Avoids redundant information or restatements.
  - Does not include explanations unless explicitly requested.

  When scoring, you should deduct points for:
  - Introductory phrases like "I believe," "I think," or "The answer is."
  - Hedging language like "probably," "likely," or "as far as I know."
  - Unnecessary context or background information.
  - Explanations when not requested.
  - Follow-up questions or offers for more information.
  - Redundant information or restatements.
  - Polite phrases like "hope this helps" or "let me know if you need anything else."
</Rubric>

<Instructions>
  - Carefully read the input and output.
  - Check for any unnecessary elements, particularly those mentioned in the <Rubric> above.
  - The score should reflect how close the response comes to containing only the essential information requested based on the rubric above.
</Instructions>

<Reminder>
  The goal is to reward responses that provide complete answers with absolutely no extraneous information.
</Reminder>

<input>
{inputs}
</input>

<output>
{outputs}
</output>
"""