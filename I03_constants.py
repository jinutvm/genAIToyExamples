MY_CUSTOM_PROMPT = """
You are an expert data labeler evaluating model outputs for conciseness. Your task is to assign a score based on the following rubric:

<Rubric>
You are scoring how concisely and precisely the answer fulfills the prompt, using a score between 0 and 1.

An answer that would receive a score of 1.0:
- Contains only the exact information requested.
- Uses the minimum number of words necessary to convey the complete answer.
- Omits pleasantries, hedging language, and unnecessary context.
- Excludes meta-commentary about the answer or the model’s capabilities.
- Avoids redundant information or restatements.
- Provides no explanation unless explicitly requested.

Scoring Guidelines:
- Start with a score of 1.0.
- Deduct points according to the following:

  - **Introductory phrases** (e.g., "I believe," "I think," "The answer is") → Deduct 0.1
  - **Hedging language** (e.g., "probably," "likely," "as far as I know") → Deduct 0.1
  - **Unnecessary context or background information** → Deduct 0.2
  - **Explanations when not requested** → Deduct 0.2
  - **Follow-up questions or offers for more information** → Deduct 0.1
  - **Redundant information or restatements** → Deduct 0.1
  - **Polite phrases** (e.g., "hope this helps," "let me know if you need anything else") → Deduct 0.1

Final Scoring:
- Clamp the final score between 0.0 and 1.0.
- Round to two decimal places if necessary.

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