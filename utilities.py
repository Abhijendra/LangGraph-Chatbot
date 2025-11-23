from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import csv

load_dotenv()

model = ChatOpenAI(temperature=0.9)

def assign_topic(message_list):
    prompt = f"Given the Human Message and AIMessage in dictionary form. Provide a short crisp topic in not more than 4 words. Messages:\n {message_list}"
    response = model.invoke(prompt)
    return response.content

def save_topic(thread_id:str, topic: str):
    # Save to database or file
    with open('topic_mapping.csv', 'a') as f:
        return f.write(f"{thread_id}, {topic}\n")
    
    
def load_topics():
    chat_topics = {}
    with open("topic_mapping.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            chat_topics[row[0]] = row[1]
    return chat_topics  # Return None if not found

if __name__ == "__main__":

    messages =  [
        HumanMessage(content='Name my any two Horror hindi movies.', additional_kwargs={}, response_metadata={}, id='f051c149-cc10-413f-8e1c-72b1cec6b12d'),
        AIMessage(content='Anabelle and conjuring', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 42, 'prompt_tokens': 13, 'total_tokens': 55, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_8bda4d3a2c', 'id': 'chatcmpl-CDF4MFMB33n1wCQtwvvUcZQEOVRDl', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='run--2ac25021-b80a-476e-baa1-f338ea2b80c4-0', usage_metadata={'input_tokens': 13, 'output_tokens': 42, 'total_tokens': 55, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})]
    
    message_contents = []

    for msg in messages:
        # print(msg.content)
        if isinstance(msg, HumanMessage):
            role = 'Human'
        else:
            role = 'AI'
        message_contents.append({role:msg.content})

    # print(message_contents)

    # print('Assigned topic is:')    
    # assigned_topic = assign_topic(message_contents)
    # save_topic('abc-def-123',assigned_topic)
    print(load_topics())
