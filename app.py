from flask import Flask,redirect,url_for,render_template,request
from paddleocr import PaddleOCR
import paddle
import warnings
import numpy as np
import cv2
import pandas as pd
import os
import json
import re
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types
warnings.filterwarnings('ignore', category=DeprecationWarning)

app=Flask(__name__)

# load api key
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

ocr = PaddleOCR(
    # Use text_detection_model_name (not det_model_name)
    text_detection_model_name="PP-OCRv5_mobile_det",
    # Use text_recognition_model_name (not rec_model_name)  
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    
    # CPU optimizations
    enable_mkldnn=True,
    #use_gpu=False
)
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "static/result"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def process_image(image_path):
    img =cv2.imread(image_path)
    #img = cv2.resize(img,(1000,1000))

    
    # Step 1: Resize proportionally (max dimension becomes 1000px)
    height, width = img.shape[:2]
    scale = 1000 / max(height, width)
    new_width = int(width * scale)
    new_height = int(height * scale)
    img = cv2.resize(img, (new_width, new_height))
    
    gray_img= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #filter_image = cv2.bilateralFilter(gray_img,9,75,75)
    #gamma = 4.6
    #bright_img = np.power(filter_image/255.0,gamma)*255
    #bright_img = bright_img.astype("uint8")
    final_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
    
    
    
    return img,final_img

def clean_text(text):
    # 1. Fix letter-number merging (very common in OCR)
    text = re.sub(r'(\d{2}/\d{2}/\d{4})(\d{1,2}:\d{2}:\d{2}[AP]M)', r'\1 \2', text)
    text = re.sub(r'(\d{2}-\d{2}-\d{2,4})(\d{1,2}:\d{2}:\d{2}[AP]M)',r'\1 \2', text)
    text = re.sub(r'(\d{2}-\d{2}-\d{2,4})(\d{1,2}:\d{2}:\d{2})',r'\1 \2', text)
    text = re.sub(r'(\d{2}/\d{2}/\d{4})(\d{2}:\d{2}:\d{2}).*', r'\1 \2',text)
    return text


def read_ocr(image):
    result = ocr.predict(image)
    text_list = [] 
    conf_list = []
    for item in result[0]["rec_texts"]:
        text_list.append(item)
    for item in result[0]["rec_scores"]:
        conf_list.append(item)
    full_text = "\n".join(text_list)
    full_text = clean_text(full_text)
    text = " ".join(text_list)
    extracted_data = extract_invoice_basic(full_text)
    average_confidence = sum(conf_list)/len(conf_list)
    return image,full_text, average_confidence, extracted_data


def extract_invoice_basic(text):
    prompt = f"""You are a strict JSON generator for invoice extraction.
    Extract:
    - vendor_name
    - invoice_number
    - date
    - total_amount
    - cash
    Return ONLY valid JSON.
    TEXT:
    {text}
    """

    response = client.models.generate_content(
        model="models/gemini-3.5-flash",
        contents = prompt)
    cleaned = response.text.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)
    return data
    

    
    



@app.route('/')
def home():
    
    return render_template('index.html')


@app.route('/upload',methods= ["POST"])
def upload():
    #get images from form
    file = request.files["image"]
    ## save image on upload folder
    path = os.path.join(UPLOAD_FOLDER,file.filename)
    file.save(path)

    # preprocess image
    original, process = process_image(path)

    # extract text,prob and image with bounding box
    result_img, text,confidence, extracted_text = read_ocr(process)
    result_path = os.path.join(RESULT_FOLDER,file.filename)
    cv2.imwrite(result_path,result_img)

    data = {
        "img" : file.filename,
        "fulltext" : text,
        "extrattext": extracted_text,
        "confidence": confidence
        
    }

    with open("static/result/result.json", "w") as f:
        json.dump(data,f)

    
    return redirect("/result")


@app.route('/result')
def result():
    with open("static/result/result.json", "r") as f:
        data = json.load(f)
    return render_template(
        "result.html",
        image_url = "static/result/" +data["img"],
        text = data["fulltext"],
        extracted_text = data["extrattext"],
        confidence = data["confidence"])
        
    
    

  


if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)