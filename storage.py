from google.cloud import storage
import google.generativeai as genai
import time
import os
import json

storage_client = storage.Client()

def get_list_of_files(bucket_name):
    """Lists all the blobs in the bucket."""
    print("\n")
    print("get_list_of_files: "+bucket_name)

    blobs = storage_client.list_blobs(bucket_name)
    print(blobs)
    files = []
    for blob in blobs:
        files.append(blob.name)

    return files

def upload_file(bucket_name, file_name):
    """Send file to bucket."""
    print("\n")
    print("upload_file: "+bucket_name+"/"+file_name)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    blob.upload_from_filename(file_name)

    return 

def download_file(bucket_name, file_name):
    """ Retrieve an object from a bucket and saves locally"""  
    print("\n")
    print("download_file: "+bucket_name+"/"+file_name)
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(file_name)
    blob.download_to_filename(file_name)
    blob.reload()
    print(f"Blob: {blob.name}")
    print(f"Bucket: {blob.bucket.name}")
    print(f"Storage class: {blob.storage_class}")
    print(f"Size: {blob.size} bytes")
    print(f"Content-type: {blob.content_type}")
    print(f"Public URL: {blob.public_url}")

    return
    
genai.configure(api_key=os.environ['GEMINI_API'])

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

PROMPT1 = "give description the image. No other headings only text in 10 or 20 words"
PROMPT2 = "give title for the image. No other headings only one title"


def image_desc_json(bucket_name, image_path):
    file = genai.upload_file(image_path, mime_type="image/jpeg")
    response1 = model.generate_content([file, "\n\n", PROMPT1])
    description = response1.text
    response2 = model.generate_content([file, "\n\n", PROMPT2])
    title = response2.text
    image_data = {
        "title": title,
        "description": description
    }
    output_path = os.path.splitext(image_path)[0] + "_metadata.json"
    with open(output_path, 'w') as json_file:
        json.dump(image_data, json_file, indent=4)
    upload_file(bucket_name,output_path)
    




