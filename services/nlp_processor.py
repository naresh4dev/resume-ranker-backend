from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from utils.text_extractor import match_skills, extract_resume_entities, extract_keywords

sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def process_candidates(job_text, resumes, top_k=None, use_skill_similarity=False):

    """
    Check for the best matching resumes for a given job description.
    """
    job_summary = summarizer(job_text, max_length=240, min_length=60, do_sample=False)[0]['summary_text']
    job_entities = extract_keywords(job_text)
    job_skill_names = [s["skill_name"] for s in job_entities]
    job_input_text = " ".join(job_skill_names) if use_skill_similarity else job_text

    job_embedding = sbert_model.encode(job_input_text, convert_to_tensor=True)
    all_skills_matched_count=dict()
    all_skills_gaps = dict()
    results = []
    for resume_file_path, resume_text in resumes:
        summary = summarizer(resume_text, max_length=120, min_length=60, do_sample=False)[0]['summary_text']
        resume_entities = extract_resume_entities(resume_text)
        resume_skill_names = [s["skill_name"] for s in resume_entities["skill_keywords"]]
        resume_input_text = " ".join(resume_skill_names) if use_skill_similarity else resume_text
        resume_embedding = sbert_model.encode(resume_input_text, convert_to_tensor=True)
        similarity_score = float(util.pytorch_cos_sim(job_embedding, resume_embedding)[0][0])
        skills = match_skills(job_entities,resume_entities["skill_keywords"])
        feedback = []
        for skill in skills["matched_skills"]:
            all_skills_matched_count[skill] = all_skills_matched_count.get(skill, 0) + 1
        for skill in skills["missing_skills"]:
            all_skills_gaps[skill] = all_skills_gaps.get(skill, 0) + 1
        if skills["missing_skills"]:
            feedback.append(f"Consider adding or highlighting these missing skills: {', '.join(skills['missing_skills'][:5])}")
        if skills["partial_skills"]:
            feedback.append(f"Some partially matched skills could be clarified as match score ranging 70 to 89: {', '.join(skills['partial_skills'][:5])}")
        if not skills["missing_skills"] and not skills["partial_skills"]:
            feedback.append("Excellent skill match! All expected skills are present.")
        results.append({
            "candidate_id":resume_file_path.split("$")[0],
            "resume_file_path": resume_file_path,
            "match_score": round(similarity_score*100, 2),
            "summary": summary,
            "resume_entities": resume_entities,
            "skills": skills,
            "feedback": feedback,
        })
    top_skills = sorted(all_skills_matched_count.items(), key=lambda x: x[1], reverse=True)[:5]
    common_skills_gaps = sorted(all_skills_gaps.items(), key=lambda x: x[1], reverse=True)[:5]
    top_skills=[skill[0] for skill in top_skills]
    common_skills_gaps=[skill[0] for skill in common_skills_gaps]
    results.sort(key=lambda x: x["match_score"], reverse=True)
    if top_k is not None:
        results = results[:top_k]
    return job_summary,top_skills,common_skills_gaps,results