import re
from openai import OpenAI

def summarize(content: str):
    client = OpenAI(api_key="sk-d2484100bf1444b6a8ee278dcf9ed69b", base_url="https://api.deepseek.com")

    input_prompt = f"""
    You are a government job summarizer. Summarize the key points from this PDF recruitment notice for retired professionals in under 100 words. 
    
    Instructions:
    - Read the content carefully.
    - Return a JSON with two keys, title of the post "title" and summary of the post "summary".
    - Highlight only the useful information like skills and post name.
    - Exclude instructions, forms and annexures, age limit, pay scale and application deadline. 
    - Summarize the following job posting strictly in a single, well-structured paragraph. Do not use bullet points or lists. Keep the summary concise, clear, and human-readable. 
    - Output ONLY the JSON. Do NOT add introductions, disclaimers, or extra sentences. Begin directly with the first word of the summary.
    
    Text: {content} 
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": input_prompt},
        ],
        stream=False
    )
    message = response.choices[0].message.content.strip()
    print("\n[ RAW LLM OUTPUT]:\n", message)
    return(response.choices[0].message.content)