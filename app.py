import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
import tools
import divider as dv
import encrypter as enc
import decrypter as dec
import restore as rst

UPLOAD_FOLDER = './uploads/'
UPLOAD_KEY = './key/'
ALLOWED_EXTENSIONS = set(['pem'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_KEY'] = UPLOAD_KEY
app.config['TempKey'] = "/Key"

#port = int(os.getenv('PORT', 8000))

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

def allowed_file(filename):
	print "in allowed_file"
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def start_encryption():
	dv.divide()
	print "start_encryption"
	tools.empty_folder('uploads')
	enc.encrypter()
	return render_template('success.html')

def start_decryption():
	print "in start_decryption"
	dec.decrypter()
	tools.empty_folder('key')
	rst.restore()
	return render_template('restore_success.html')

@app.route('/return_key/Main_Key.pem')
def return_key():
	list_directory = tools.list_dir('key')
	filename = './key/' + list_directory[0]
	print filename
	return send_file(filename, as_attachment=True)

@app.route('/download-file/')
def return_file():
	list_directory = tools.list_dir('restored_file')
	filename = './restored_file/' + list_directory[0]
	return send_file(filename, attachment_filename=list_directory[0], as_attachment=True)

@app.route('/download/')
def downloads():
	print "in download"
	return render_template('download.html')

@app.route('/upload')
def call_page_upload():
	print "in upload"
	return render_template('upload.html')

@app.route('/home')
def back_home():
	print "in home"
	tools.empty_folder('key')
	tools.empty_folder('restored_file')
	return render_template('index.html')

@app.route('/')
def index():
	print "in index"
	return render_template('index.html')

@app.route('/data', methods=['GET', 'POST'])
def upload_file():
	print "in upload_file"
	tools.empty_folder('uploads')
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return 'NO FILE SELECTED'
		if file:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
			return start_encryption()
		return 'Invalid File Format !'
	
@app.route('/download_data', methods=['GET', 'POST'])
def upload_key():
	print "in upload_key"
	tools.empty_folder('key')
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return 'NO FILE SELECTED'
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_KEY'], file.filename))
			return start_decryption()
		return 'Invalid File Format !'

if __name__ == '__main__':
	print "in main"
	app.run(host='127.0.0.1', port=8000, debug=True)