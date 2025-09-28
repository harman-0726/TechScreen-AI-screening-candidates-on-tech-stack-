def generate_technical_questions_prompt(tech_stack):
    return f"""
Generate 5 technical multiple-choice questions (MCQs) related to the following technologies:

{tech_stack}

Each question must follow this format:

Q1. <question>
a) Option A
b) Option B
c) Option C
d) Option D
Answer: b

Return only the questions in that format.
"""
