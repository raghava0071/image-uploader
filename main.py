import os
from flask import Flask, redirect, request, send_file
from storage import upload_file,image_desc_json
from datetime import datetime

os.makedirs('files', exist_ok = True)

app = Flask(__name__)

@app.route('/')
def index():
    index_html="""
<form method="post" enctype="multipart/form-data" action="/upload" method="post">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="form_file" accept="image/jpeg"/>
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>"""    

    for file in list_files():
        index_html += "<li><a href=\"/files/" + file + "\">" + file + "</a></li>"

    return index_html

@app.route('/upload', methods=["POST"])
def upload():
    bucket_name = "image-and-json"
    file = request.files['form_file']  
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ') 
    new_filename = f"{timestamp}_{file.filename}"
    image_path = "files/"+ new_filename
    file.save(image_path)
    upload_file(bucket_name, image_path) 
    image_desc_json(bucket_name, image_path)
    return redirect("/")

@app.route('/files')
def list_files():
    files = os.listdir("./files")
    jpegs = []
    for file in files:
        if file.lower().endswith(".jpeg") or file.lower().endswith(".jpg"):
            jpegs.append(file)
    
    return jpegs

@app.route('/files/<filename>')
def get_file(filename):
  return send_file('./files/'+filename)

if __name__ == '__main__':
    app.run(debug=True)
