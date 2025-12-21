from groq import Groq
import config

client = Groq(api_key=config.GROQ_API_KEY)

def generate_questions(form_data, old_text=""):
    prompt = f"""
You are an expert professor creating a question paper for {form_data['course_name']} at {form_data['college_name']}.
University: POKHARA UNIVERSITY
Course: {form_data['course_name']}
Programme: {form_data['program']}
Semester: Spring (or as specified)
Year: {form_data['year']}
Full Marks: {form_data['full_marks']}, Time: {form_data['time_hours']} hrs.

Syllabus/Topics:
{form_data['syllabus']}

Generate the question paper in EXACT Pokhara University format:
- 7 Questions
- Each question has a) ~7 marks and b) ~8 marks (or reverse)
- Use OR alternative only in 2-3 questions (not every)
- Include numerical/problems with data/tables where suitable
- Question 7: "Write short notes on: (Any two)" with 3 options → 2 × 5
- Marks on the right big brackets []
-use times new roman font size 12 for all the questions text.
- Total marks exactly {form_data['full_marks']}
- Cover syllabus fairly with application-level questions
-no repetability of same pattern of question, must be more than half of difference beteween two consecutive generated papers.
{old_text}

Output ONLY the questions starting from "1. a) ..."Output ONLY the questions starting from "1. a) ...". No header or instructions.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "authentication" in error_msg.lower():
            return "Invalid Groq API Key – Check https://console.groq.com/keys"
        elif "rate limit" in error_msg.lower():
            return "Your Rate Limit Hit – Wait a bit or check usage"
        else:
            return f"Error: {str(e)}"