from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from utils.ai_generator import generate_questions
from utils.docx_generator import create_question_paper_doc
from utils.pdf_extractor import extract_text_from_pdf
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return "OK", 200

@app.route('/generate', methods=['POST'])
def generate():
    # Collect form data
    data = {
        'college_name': request.form['college_name'],
        'college_address': request.form['college_address'],
        'exam_type': request.form['exam_type'],
        'program': request.form['program'],
        'semester': request.form['semester'],
        'course_name': request.form['course_name'],
        'year': request.form['year'],
        'full_marks': request.form['full_marks'],
        'pass_marks': request.form['pass_marks'],
        'time_hours': request.form['time_hours'],
        'syllabus': request.form['syllabus']
    }

    # Handle syllabus PDF
    syllabus_text = data['syllabus']
    if 'syllabus_pdf' in request.files:
        file = request.files['syllabus_pdf']
        if file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            syllabus_text += "\n\n" + extract_text_from_pdf(path)

    # Handle old papers
    old_text = ""
    if 'old_papers' in request.files:
        files = request.files.getlist('old_papers')
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                old_text += extract_text_from_pdf(path) + "\n"

    old_context = f"Reference previous questions (rephrase all):\n{old_text[:4000]}" if old_text else ""

    # Generate questions
    questions = generate_questions({**data, 'syllabus': syllabus_text}, old_context)

    if "Error" in questions:
        flash("AI Error: Check your Groq API key or internet connection.")
        return redirect(url_for('index'))

    # Create DOCX
    doc = create_question_paper_doc(data, questions)
    filename = f"{data['course_name'].replace(' ', '_')}_{data['year']}.docx"
    doc.save(filename)

    return send_file(filename, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)