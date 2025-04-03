import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import io
import google.generativeai as genai
from flask import send_from_directory
import logging
import base64

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set your API key (ensure it's configured correctly)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Fetch files for display
def get_files():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename) or filename.endswith('.txt'):
            files.append(filename)
    files.sort(reverse=True)
    return files

# Check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Process the audio file with Gemini API
def process_audio_with_llm(file_path):
    # Read the audio file
    with io.open(file_path, 'rb') as audio_file:
        content = audio_file.read()

    
    model = genai.GenerativeModel('gemini-2.0-flash')

    try:
        # Define the prompt for transcription and sentiment analysis
        prompt = """
        Analyze the provided audio and provide the following:

        1. A complete transcript of the audio.
        2. A sentiment analysis of the audio, indicating the overall sentiment (positive, negative, or neutral) and providing a brief explanation of why."""
        
        # Correct request format to match Gemini API structure
        response = model.generate_content(
            [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",  # Specify the mime type
                                "data": content           # Send raw binary audio data directly
                            }
                        }
                    ]
                }
            ])

        # Assuming the response has 'transcript' and 'sentiment' parts
        response_str = response.text
        file_dir = os.path.dirname(file_path)

        # Generate a filename for the response text file
        response_file_path = os.path.splitext(file_path)[0] + '.txt'

        # Save to text file
        with open(response_file_path, 'w') as file:
            file.write(response_str)

        logging.info(f"Full response saved to: {response_file_path}")

        if hasattr(response, 'parts') and len(response.parts) > 1:
            transcript = response.parts[0].text if hasattr(response.parts[0], 'text') else ''
            sentiment = response.parts[1].inline_data if hasattr(response.parts[1], 'inline_data') else {}
            
            sentiment_score = sentiment.get('score', 0)
            sentiment_magnitude = sentiment.get('magnitude', 0)

            if not transcript:
                logging.warning(f"Failed to transcribe audio file: {file_path}")
            if sentiment_score == 0 and sentiment_magnitude == 0:
                logging.warning(f"Sentiment analysis failed for audio file: {file_path}")

            logging.info(f"Processed audio file: {file_path}")
            return transcript, sentiment_score, sentiment_magnitude

        else:
            logging.error(f"Unexpected response format for audio file: {file_path}")
            return '', 0, 0

    except Exception as e:
        logging.error(f"Error processing audio file {file_path}: {e}")
        raise  # Re-raise the exception to be handled in the route

@app.route('/')
def index():
   # files = get_files()  # List of uploaded audio files (from uploads folder)
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.wav')]  
    return render_template('index.html', files=files)

# Route to upload an audio file
@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio_data' not in request.files:
        logging.error("No audio data in request")
        return "No audio data in request", 400

    file = request.files['audio_data']
    if file.filename == '':
        logging.error("No file selected")
        return "No file selected", 400

    # Save the uploaded audio file
    filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.wav'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    logging.info(f"Uploaded audio file: {filename}")

    try:
        process_audio_with_llm(file_path)
        return "Uploaded, transcribed, and sentiment analyzed successfully. Check the generated text file.", 200
    except Exception as e:
        logging.error(f"Error during processing: {e}")
        return f"Error during processing: {e}", 500
     

# Route to serve uploaded files (audio and text)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
