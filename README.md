# Project Name
Invoice Image OCR Using Paddle OCR and Gemini Pro AI

# Project Description
PaddleOCR extract text from images and after Cleaning text it is send to Gemini Pro AI stored model to extract informations

# Install
Requirement.txt file contains all libraries that need to install in this project

# Deploy the project
Flask API is use for Deployment

# Gemini Pro Model
The Gemini Pro model requires a valid Google AI API key for verification. After obtaining the API key from Google AI Studio, a Gemini client is initialized using the key. To enhanced security, the API key is normally kept in a .env file instead of being placed directly in the source code. The API key is retrieved from the .env file by the application and is utilized to set up the Gemini client. The model is subsequently accessed by indicating its name in the request, enabling it to produce answers according to user input.The .env file is included in the .gitignore to safeguard the API key from exposure. This guarantees that the file is left out of version control and not uploaded to public repositories, aiding in safeguarding sensitive credentials from unauthorized access.
