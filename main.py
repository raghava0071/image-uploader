import os
from flask import Flask, redirect, request, send_file,render_template_string
from storage import upload_file,image_desc_json
from datetime import datetime
import json

os.makedirs('files', exist_ok = True)

bucket_name = "image-and-json"

app = Flask(__name__)

@app.route('/')
def index():
    index_html = """
    <html>
    <head>
        <style>
            body {
                background-color: #8DB600;
                color: white; 
                font-family: Arial, sans-serif;
            }
            h1, h2, p {
                color: white;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin-bottom: 10px;
            }
            a {
                color: white;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Upload Form</h1>
        <form method="post" enctype="multipart/form-data" action="/upload">
            <div>
                <label for="file">Choose file to upload</label>
                <input type="file" id="file" name="form_file" accept="image/jpeg"/>
            </div>
            <div>
                <button>Submit</button>
            </div>
        </form>
        
        <h2>Uploaded Files:</h2>
        <ul>
        """
    for file in list_files():
        index_html += f"<li><a href=\"/response/{file}\">{file}</a></li>"

    index_html += """
        </ul>
    </body>
    </html>
    """
    return index_html

@app.route('/upload', methods=["POST"])
def upload():
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
    files = get_list_of_files(bucket_name)
    jpegs = []
    for file in files:
        if file.lower().endswith(".jpeg") or file.lower().endswith(".jpg"):
            jpegs.append(file)
    
    return jpegs

@app.route('/response/<filename>')
def send_response(filename):
  json_file = filename.replace(".jpg","").replace(".jpeg","")+"_metadata.json"
  json_path = "./files/" + json_file

  with open(json_path, 'r') as file:
      json_data = json.load(file)
  page =  f"""
   <html>
   <style>
          .fixed-size {{
            width: 300px;
            height: 300px;
            object-fit: cover;
          }}
    </style>
   <body>
       <img src='/files/{filename}' class="fixed-size" />
       <p><strong> {json_data.get("title")} </strong> </p>
       <p>{json_data.get("description")}</p>
   </body>
   </html>"""

  return render_template_string(page)

@app.route('/files/<filename>')
def get_file(filename):
  return send_file('./files/'+filename)

if __name__ == '__main__':
    app.run(debug=True)
