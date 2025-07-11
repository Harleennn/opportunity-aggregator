from Scraper.models import JobDetails

def recommend_jobs(query, all_jobs):
    input_terms = [term.strip().lower() for term in query.split(",") if term.strip()]
    recommendations = []

    for job in all_jobs:
        job_skills = job.overall_skill.lower() if job.overall_skill else ""
        job_title = job.title.lower() if job.title else ""
        
        # Combine title + skills for searching
        searchable_text = job_title + " " + job_skills

        # Count how many input terms match
        match_count = sum(1 for term in input_terms if term in searchable_text)

        if match_count > 0:
            recommendations.append((job, match_count))

    # Sort by highest match first
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations
