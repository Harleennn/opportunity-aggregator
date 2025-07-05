from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_jobs(user_input, job_queryset):
    job_texts = [job.overall_skill or '' for job in job_queryset]
    all_texts = [user_input] + job_texts

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(all_texts)
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    job_scores = list(zip(job_queryset, similarity_scores))
    job_scores.sort(key=lambda x: x[1], reverse=True)

    return job_scores[:5]  # Top 5 results
