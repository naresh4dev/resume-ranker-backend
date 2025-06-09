import json
from pathlib import Path
def preprocess_skill_db():
    BASE_DIR= Path(__file__).resolve().parent.parent
    fileObj =  open(f"{BASE_DIR}/data/skill_db/skill_db_relax_20.json", 'r')
    file =  json.load(fileObj)
    fileObj.close()
    forms = []
    meta = []

    for skill_id, data in file.items():
        full_form = data['high_surfce_forms']['full']
        form = []
        form.append(full_form.lower())
        form.append(data['skill_name'].lower())
        meta.append({
            "skill_id": skill_id,
            "skill_name": data['skill_name'],
            "skill_type": data['skill_type'],
            "matched_text": full_form
        })

        for variant in data.get('low_surface_forms', []):
            form.append(variant.lower())
        forms.append(form)
    return forms, meta

# forms, meta = preprocess_skill_db()
# print(f"Total unique skill surface forms: {len(forms)}")
# print(f"Total unique skill metadata entries: {len(meta)}")
# print(f"Sample skill metadata: {meta[:5]}")
# print(f"Sample skill surface forms: {forms[:5]}")