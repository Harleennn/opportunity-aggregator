import re
from openai import OpenAI

#  Real DeepSeek LLM summarizer
def llm_summarize(text: str):
    client = OpenAI(
        api_key="sk-d2484100bf1444b6a8ee278dcf9ed69b",  # Replace with your actual key if needed
        base_url="https://api.deepseek.com"
    )

    # Clean text
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    input_prompt = f"""
    You are a government job summarizer. Summarize the key points from this PDF recruitment notice for retired professionals in under 150 words. 

    Instructions:
    - Read the content carefully.
    - Highlight only the useful information like skills, post name and job duration. 
    - Exclude instructions, forms and annexures, age limit, pay scale and application deadline. 
    - Summarize the following job posting strictly in a single, well-structured paragraph. Do not use bullet points or lists. Keep the summary concise, clear, and human-readable. 
    - Output ONLY the summary as plain text. Do NOT add introductions, disclaimers, or extra sentences. Begin directly with the first word of the summary.

    Text: {text} 
    Summary: 
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": input_prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(" [LLM ERROR]:", e)
        return None  # Return None on error


#  Mock fallback for testing or failed LLM calls
def mock_llm_summarize(text, pdf_name=None):
    posting_data = {
        "age_limit": "18-35",
        "application_deadline": "31 July 2025",
        "pay_scale": "20,000 INR",
        "employment_type": "Contract"
    }

    job_details_data = {
        "title": f"Test Job - {pdf_name}" if pdf_name else "Test Job",
        "eligibility": "Any graduate",
        "minimum_qualification": "None",
        "overall_skill": "Typing, Communication",
        "summary": "This is a mock summary of the job post."  # You can display this too
    }

    return posting_data, job_details_data
