import re


SKILLS_LIST = [
    "Python", "SQL", "Java", "C++", "HTML", "CSS",
    "FastAPI", "Flask", "Django", "Machine Learning",
    "Deep Learning", "Generative AI", "LLM",
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow",
    "PyTorch", "Power BI", "Excel", "AWS", "Docker"
]


def extract_email(text: str):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str):
    match = re.search(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)", text)
    return match.group(0) if match else None


def extract_name(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if lines:
        return lines[0]

    return None


def extract_skills(text: str):
    found_skills = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills




def extract_experience(text: str):
    patterns = [
        r"\b\d+\+?\s+years?\s+(?:of\s+)?(?:work\s+)?experience\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0)

    section = re.search(
        r"\bExperience\b\s*\n+(.*?)(?=\n\s*(?:Education|Projects|Skills|Technologies|Certificates?)\b|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if section:
        lines = [
            line.strip()
            for line in section.group(1).splitlines()
            if line.strip()
        ]

        if lines:
            return " – ".join(lines[:2])

    return None




def extract_resume_data(text: str):
    return {
        "full_name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "extracted_text": text
    }