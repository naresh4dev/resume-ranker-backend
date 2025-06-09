from sklearn.feature_extraction.text import TfidfVectorizer
import re
from spacy.matcher import PhraseMatcher
import spacy
from rapidfuzz import fuzz
from utils.skill_db_processor import preprocess_skill_db


import json
# spacy.cli.download("en_core_web_sm")
def build_spacy_with_phraseMatcher():
    nlp = spacy.load("en_core_web_sm")
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    patterns = [
        {"label": "EMAIL", "pattern": [{"TEXT": {"REGEX": r"^[\w\.-]+@[\w\.-]+\.\w+$"}}]},
        {"label": "PHONE", "pattern": [{"TEXT": {"REGEX": r"^(\+?\d{1,3})?[\s\-\.]?\(?\d{2,4}\)?[\s\-\.]?\d{3,5}[\s\-\.]?\d{4,6}$"}}]},
        {"label": "URL", "pattern": [{"TEXT": {"REGEX": r"^https?://[^\s]+$"}}]}
    ]
    ruler.add_patterns(patterns)
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    forms, meta = preprocess_skill_db()
    patterns = []
    skill_id_to_name = {}
    for form, m in zip(forms, meta):
        patterns = [nlp.make_doc(f) for f in form if f.strip()]
        if patterns:
            matcher.add(m["skill_id"], patterns)
            skill_id_to_name[m["skill_id"]] = m["skill_name"]

    
    return nlp, matcher, skill_id_to_name
nlp, matcher, skill_id_to_name = build_spacy_with_phraseMatcher()

def extract_keywords(text):
    doc = nlp(text)
    matches = matcher(doc)
    matched_skills = []
    seen_skills = set()
    for skill_id, start, end in matches:
        span = doc[start:end]
        
        if len(span.text) >= 3:  # filter by token count
            skill_key = nlp.vocab.strings[skill_id]
            if skill_key not in seen_skills:
                matched_skills.append({"skill_id":skill_key,"skill_name":skill_id_to_name.get(skill_key, span.text)})
                seen_skills.add(skill_key)

    return matched_skills

def match_skills(keywords, resume_keywords):
    matched, partial, missing = set() , set(), set()

    resume_skill_ids = {r["skill_id"] for r in resume_keywords}

    
    for job_skill in keywords:
        skill_id = job_skill.get("skill_id")
        skill_name = job_skill.get("skill_name").lower()

        if skill_id in resume_skill_ids:
            matched.add(job_skill["skill_name"]) 
            continue

        best_score = max(
            [fuzz.partial_ratio(skill_name, text["skill_name"].lower()) for text in resume_keywords],
            default=0
        )

        if best_score >= 90:
            matched.add(job_skill["skill_name"])
        elif 70 >= best_score < 90:
            partial.add(job_skill["skill_name"])
        else:
            missing.add(job_skill["skill_name"])

    return { 
        "matched_skills": list(matched),
        "partial_skills": list(partial),
        "missing_skills": list(missing)
    }
def extract_name_from_header(text):
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    
    for line in lines[:3]:
        if 1 < len(line.split()) <= 5 and all(w.istitle() for w in line.split()) and not re.search(r'\d|\W', line.replace(" ", "")):
            return line.strip()
    return None

def extract_resume_entities(resume_text):
    doc = nlp(resume_text)
    skills = extract_keywords(resume_text)
    education, achievements, experience, links = [], [], [],[]
    full_name = extract_name_from_header(resume_text) 
    email, phone = None, None

    for ent in doc.ents:
        if ent.label_ == "EMAIL" and not email:
            email = ent.text
        elif ent.label_ == "PHONE" and not phone:
            phone = ent.text
        elif ent.label_ == "URL":
            links.append(ent.text)
        elif ent.label_ == "PERSON" and not full_name:
            full_name = ent.text

    for sent in doc.sents:
        s = sent.text.lower()
        ents = None
        if not email or not phone or not full_name:
            # Re-evaluate entities in each sentence if not already found
            ents = {ent.label_ for ent in sent.ents}
            if  "EMAIL" in ents and not email:
                email = ent.text
            elif "PHONE" in ents and not phone:
                phone = ent.text
            elif "URL" in ents:
                links.append(ent.text)
            elif "PERSON" in ents and not full_name:
                full_name = ent.text

        if any(k in s for k in ["experience", "worked", "intern", "employment", "job", "role", "company"]):
            experience.append(sent.text)
        elif any(k in s for k in ["degree", "education", "bachelor", "master", "phd", "university", "college", "school", "academic"]):
            education.append(sent.text)
        elif any(k in s for k in ["award", "achieve", "certified", "achievement", "certification", "honor", "recognition", "accomplishment", "distinction", "merit", "accolade", "commendation", "credential"]  ):
            achievements.append(sent.text)

    return {
        "full_name": full_name,
        "email": email if email else "",
        "phone": phone if phone else "",
        "skill_keywords": skills,
        "links": links,
        "education": list(set(education)),
        "achievements": list(set(achievements)),
        "experience": list(set(experience))
    }
