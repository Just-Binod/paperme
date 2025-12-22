# from flask import Flask, render_template, request, send_file, flash, redirect, url_for
# import os
# from utils.ai_generator import generate_questions
# from utils.docx_generator import create_question_paper_doc
# from utils.pdf_extractor import extract_text_from_pdf
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.secret_key = "supersecretkey"
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

##
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from utils.ai_generator import generate_questions
from utils.docx_generator import create_question_paper_doc
from utils.pdf_extractor import extract_text_from_pdf
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='../templates', static_folder='../static')  # Adjust paths since app is in api/
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")  # Use env var for production
UPLOAD_FOLDER = '/tmp/uploads'  # MUST use /tmp – only writable place!
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
##


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

# if __name__ == '__main__':
#     app.run(debug=True)

# if __name__ == '__main__':
#     # Render provides a 'PORT' environment variable. If it's not there, use 10000.
#     port = int(os.environ.get("PORT", 10000))
#     # '0.0.0.0' tells the OS to listen on all public IPs (required for Render)
#     app.run(host='0.0.0.0', port=port)

# ... (Keep all your imports and logic exactly as they are) ...

# if __name__ == '__main__':
#     # Koyeb uses 'PORT' environment variable (usually 8000 or 8080)
#     # If not found, it defaults to 8080 for safety
#     port = int(os.environ.get("PORT", 8080))
    
#     # Must use 0.0.0.0 to be accessible externally
#     app.run(host='0.0.0.0', port=port)