# This function mocks LLM output by splitting PDF-wide and job-specific fields

def mock_llm_summarize(text, pdf_name=None):
    # PDF-wide fields → for JobPosting model
    posting_data = {
        "age_limit": "18-35",
        "application_deadline": "31 July 2025",
        "pay_scale": "20,000 INR",
        "employment_type": "Contract"
    }

    # Job-specific fields → for JobDetails model
    job_details_data = {
        "title": "Test Job",
        "eligibility": "Any graduate",
        "minimum_qualification": "None",
        "overall_skill": "Typing, Communication"
    }

    if pdf_name:
        job_details_data["title"] += f" - {pdf_name}"

    return posting_data, job_details_data
