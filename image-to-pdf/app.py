from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from converter import convert_images_to_pdf
import os, uuid, json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400

    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400

    # Parse options from form
    options = {
        'page_size':    request.form.get('page_size', 'a4'),
        'orientation':  request.form.get('orientation', 'portrait'),
        'margin':       int(request.form.get('margin', 20)),
        'fit_mode':     request.form.get('fit_mode', 'fit'),
        'add_filename': request.form.get('add_filename') == 'true',
        'bg_color':     request.form.get('bg_color', '#ffffff'),
    }

    # Save uploaded images to /uploads
    session_id = str(uuid.uuid4())
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder)

    saved_paths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(session_folder, filename)
            file.save(path)
            saved_paths.append(path)

    if not saved_paths:
        return jsonify({'error': 'No valid image files'}), 400

    # Convert to PDF
    output_pdf = os.path.join(session_folder, 'output.pdf')
    try:
        convert_images_to_pdf(saved_paths, output_pdf, options)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(output_pdf, as_attachment=True,
                     download_name='converted.pdf',
                     mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)