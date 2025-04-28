import os
import asyncio
import tempfile
import time
import json
from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify, session
from werkzeug.utils import secure_filename
import threading
from datetime import datetime
from flask import send_file

import google.generativeai as genai
from flask import request, jsonify
from dotenv import load_dotenv

# Import from our modules
from tts import generate_simple_tts

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "simple_tts_generator"  # for session management

load_dotenv()

def setup_gemini_api(api_key):
    genai.configure(api_key=api_key)
# Add this to your app initialization
app.config['GEMINI_API_KEY'] = os.getenv("GEMINI_API_KEY")
# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
ALLOWED_EXTENSIONS = {'txt'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Dictionary to store job statuses
jobs = {}

# Define available voices with language grouping
AVAILABLE_VOICES = [
    # English voices
    {"id": "en-US-GuyNeural", "name": "Guy (Male, US)", "language": "English"},
    {"id": "en-US-ChristopherNeural", "name": "Christopher (Male, US)", "language": "English"},
    {"id": "en-US-EricNeural", "name": "Eric (Male, US)", "language": "English"},
    {"id": "en-GB-RyanNeural", "name": "Ryan (Male, UK)", "language": "English"},
    {"id": "en-GB-ThomasNeural", "name": "Thomas (Male, UK)", "language": "English"},
    {"id": "en-AU-WilliamNeural", "name": "William (Male, Australian)", "language": "English"},
    {"id": "en-CA-LiamNeural", "name": "Liam (Male, Canadian)", "language": "English"},
    {"id": "en-US-JennyNeural", "name": "Jenny (Female, US)", "language": "English"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (Female, UK)", "language": "English"},
    {"id": "en-AU-NatashaNeural", "name": "Natasha (Female, Australian)", "language": "English"},
    
    # Arabic voices
    {"id": "ar-MA-JamalNeural", "name": "Jamal (Male, Moroccan)", "language": "Arabic"},
    {"id": "ar-EG-ShakirNeural", "name": "Shakir (Male, Egyptian)", "language": "Arabic"},
    {"id": "ar-SA-FahdNeural", "name": "Fahd (Male, Saudi)", "language": "Arabic"},
    
    # French voices
    {"id": "fr-FR-HenriNeural", "name": "Henri (Male)", "language": "French"},
    {"id": "fr-FR-DeniseNeural", "name": "Denise (Female)", "language": "French"},
    
    # German voices
    {"id": "de-DE-ConradNeural", "name": "Conrad (Male)", "language": "German"},
    {"id": "de-DE-KatjaNeural", "name": "Katja (Female)", "language": "German"},
    
    # Spanish voices
    {"id": "es-ES-AlvaroNeural", "name": "Álvaro (Male)", "language": "Spanish"},
    {"id": "es-ES-ElviraNeural", "name": "Elvira (Female)", "language": "Spanish"},
    
    # Italian voices
    {"id": "it-IT-DiegoNeural", "name": "Diego (Male)", "language": "Italian"},
    {"id": "it-IT-ElsaNeural", "name": "Elsa (Female)", "language": "Italian"},
    
    # Portuguese voices
    {"id": "pt-BR-AntonioNeural", "name": "Antonio (Male, Brazilian)", "language": "Portuguese"},
    {"id": "pt-BR-FranciscaNeural", "name": "Francisca (Female, Brazilian)", "language": "Portuguese"}
]

# Define languages from available voices
AVAILABLE_LANGUAGES = sorted(list(set([voice["language"] for voice in AVAILABLE_VOICES])))
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_id():
    return f"{int(time.time())}_{os.urandom(4).hex()}"

# Custom function to run async tasks in the background
def run_async_task(coroutine, job_id):
    async def wrapper():
        try:
            jobs[job_id]['status'] = 'processing'
            result = await coroutine
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['result'] = result
        except Exception as e:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = str(e)
            print(f"Error in job {job_id}: {str(e)}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(wrapper())
    loop.close()

# Routes
@app.route('/')
def index():
    # Check if there's a prefill parameter
    prefill = request.args.get('prefill', '')
    return render_template('index.html', voices=AVAILABLE_VOICES, languages=AVAILABLE_LANGUAGES, prefill=prefill)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Get the input method (text or file)
    input_method = request.form.get('input-method', 'text')
    
    # Process form data for voice/speed/depth
    voice_id = request.form.get('voice', 'en-US-JennyNeural')
    speed = float(request.form.get('speed', 1.0))
    depth = int(request.form.get('depth', 1))
    
    # Debug logging
    print(f"Received TTS parameters: voice={voice_id}, speed={speed}, depth={depth}")
    
    # Generate a unique job ID
    job_id = generate_unique_id()
    
    # Create temp directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Handle text input
    if input_method == 'text':
        text_content = request.form.get('text-content', '').strip()
        
        if not text_content:
            return render_template('error.html', message="No text provided. Please enter some text to convert to speech.")
        
        # Save the text to a temporary file
        script_filename = f"text_input_{job_id}.txt"
        script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_filename)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
    
    # Handle file upload
    else:
        if 'script' not in request.files:
            return jsonify({'error': 'No script file provided'}), 400
        
        script_file = request.files['script']
        if script_file.filename == '':
            return jsonify({'error': 'No script file selected'}), 400
        
        if not script_file or not allowed_file(script_file.filename):
            return jsonify({'error': 'Invalid file format. Please upload a .txt file for scripts'}), 400
        
        # Save the uploaded file
        script_filename = secure_filename(script_file.filename)
        script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_filename)
        script_file.save(script_path)
    
    # Output file setup
    output_filename = f"tts_{job_id}.mp3"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Store speed and depth values in job info for reference
    jobs[job_id] = {
        'status': 'pending',
        'script_file': script_path,
        'output_file': output_path,
        'start_time': time.time(),
        'input_type': input_method,
        'voice_id': voice_id,
        'speed': speed,
        'depth': depth
    }
    
    # Start the processing task in a background thread
    process_task = generate_simple_tts(
        script_path, output_path, voice_id, speed, depth
    )
    
    thread = threading.Thread(
        target=run_async_task,
        args=(process_task, job_id)
    )
    thread.daemon = True
    thread.start()
    
    # Store job ID in session
    if 'jobs' not in session:
        session['jobs'] = []
    session['jobs'].append(job_id)
    session.modified = True
    
    return redirect(url_for('job_status', job_id=job_id))

@app.route('/ssml')
def ssml_page():
    return render_template('ssml.html', voices=AVAILABLE_VOICES)

@app.route('/upload-ssml', methods=['POST'])
def upload_ssml():
    # Get form data
    ssml_content = request.form.get('ssml-content', '').strip()
    voice_id = request.form.get('voice', 'en-US-JennyNeural')
    
    if not ssml_content:
        return render_template('error.html', message="No SSML provided. Please enter SSML markup to convert to speech.")
    
    # Make sure the SSML is properly formatted
    if not ssml_content.startswith('<speak') or not ssml_content.endswith('</speak>'):
        ssml_content = f'<speak>{ssml_content}</speak>'
    
    # Generate a unique job ID
    job_id = generate_unique_id()
    
    # Create temp directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Save the SSML to a temporary file
    script_filename = f"ssml_input_{job_id}.xml"
    script_path = os.path.join(app.config['UPLOAD_FOLDER'], script_filename)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(ssml_content)
    
    # Output file setup
    output_filename = f"tts_{job_id}.mp3"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Initialize job status
    jobs[job_id] = {
        'status': 'pending',
        'script_file': script_path,
        'output_file': output_path,
        'start_time': time.time(),
        'input_type': 'ssml',
        'is_ssml': True,
        'voice_id': voice_id
    }
    
    # Start the processing task in a background thread
    process_task = generate_simple_tts(
        script_path, output_path, voice_id, 1.0, 1, True
    )
    
    thread = threading.Thread(
        target=run_async_task,
        args=(process_task, job_id)
    )
    thread.daemon = True
    thread.start()
    
    # Store job ID in session
    if 'jobs' not in session:
        session['jobs'] = []
    session['jobs'].append(job_id)
    session.modified = True
    
    return redirect(url_for('job_status', job_id=job_id))

@app.route('/status/<job_id>')
def job_status(job_id):
    if job_id not in jobs:
        return render_template('error.html', message="Job not found.")
    
    job = jobs[job_id]
    # Pass the AVAILABLE_VOICES list to the template
    return render_template('status.html', job_id=job_id, job=job, voices=AVAILABLE_VOICES)

@app.route('/api/status/<job_id>')
def api_job_status(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id].copy()
    # Calculate elapsed time
    elapsed = time.time() - job['start_time']
    job['elapsed_time'] = elapsed
    
    return jsonify(job)

@app.route('/download/<job_id>')
def download_file(job_id):
    if job_id not in jobs or jobs[job_id]['status'] != 'completed':
        return render_template('error.html', message="File not available for download.")
    
    output_file = jobs[job_id]['result']
    return send_file(output_file, as_attachment=True)

@app.route('/stream-audio/<job_id>')
def stream_audio(job_id):
    # Get the job data from your jobs dictionary
    job = jobs.get(job_id)
    
    if not job:
        return "Job not found", 404
    
    # Check if job is completed
    if job['status'] != 'completed':
        return "Audio not ready for streaming", 404
    
    # For completed jobs, your app stores the output path in different ways
    # When a job completes successfully, sometimes it stores the path in 'result'
    # and sometimes in 'output_file'
    if 'result' in job and job['result']:
        audio_file = job['result']
    else:
        audio_file = job['output_file']
    
    # Return the file as a streaming response
    return send_file(
        audio_file, 
        mimetype='audio/mpeg',
        as_attachment=False,
        conditional=True
    )
@app.route('/dashboard')
def dashboard():
    user_jobs = session.get('jobs', [])
    user_job_data = {}
    
    for job_id in user_jobs:
        if job_id in jobs:
            user_job_data[job_id] = jobs[job_id]
    
    # Pass the AVAILABLE_VOICES list to the template
    return render_template('dashboard.html', jobs=user_job_data, voices=AVAILABLE_VOICES)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Internal server error. Please try again later."), 500

# Add this after creating your Flask app
@app.template_filter('strftime')
def _jinja2_filter_datetime(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M')

@app.route('/shorts-generator')
def shorts_generator():
    """Route for the AI shorts script generator page"""
    return render_template('shorts_generator.html', voices=AVAILABLE_VOICES, languages=AVAILABLE_LANGUAGES)

@app.route('/generate-shorts-script', methods=['POST'])
def generate_shorts_script():
    # Get data from request
    topic = request.form.get('topic', '').strip()
    
    if not topic:
        return jsonify({'error': 'Please provide a topic'}), 400
    
    # Configure prompt for Gemini
    prompt = f"""
Write a concise, engaging voiceover script for a short-form video (30-60 seconds) based on the following:

TOPIC: {topic}

Style and Guidelines:
- Create a script that is EXACTLY 30-60 seconds when read aloud (approximately 80-160 words)
- Start with an attention-grabbing hook
- Use conversational, energetic language that feels authentic and spontaneous
- Create a sense of urgency and excitement
- Keep sentences short and punchy for easy delivery
- Include a strong call-to-action at the end
- NO lists, NO special formatting, NO bullet points, NO asterisks, NO text in brackets
- The output must ONLY contain the spoken script — nothing else
- Make it sound like a human conversation, not a corporate announcement

Make sure the final result is clean, pure, flowing text ready for an AI voiceover, and the perfect length for short-form video platforms.
"""
    
    try:
        # Configure the Gemini API with your key
        setup_gemini_api(app.config['GEMINI_API_KEY'])
           
        # Generate content with Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
       
        # Extract the generated text
        script_text = response.text
       
        # Return the generated script
        return jsonify({
            'success': True,
            'script': script_text
        })
    
    except Exception as e:
        print(f"Error generating shorts script: {e}")
        return jsonify({'error': 'Failed to generate script. Please try again later.'}), 500
@app.route('/generate-script', methods=['POST'])
def generate_script():
    # Get data from request
    title = request.form.get('title', '').strip()
    idea1 = request.form.get('idea1', '').strip()
    idea2 = request.form.get('idea2', '').strip()
    idea3 = request.form.get('idea3', '').strip()
    
    if not title:
        return jsonify({'error': 'Please provide a video title'}), 400
    
    # Configure prompt for Gemini
    prompt = f"""
Write a calm, relatable, and emotionally engaging voiceover script for a YouTube video based on the following:

TITLE: {title}

MAIN IDEAS:
1. {idea1}
2. {idea2}
3. {idea3}

Style and Guidelines:
- Speak directly to the listener like a friend having a real conversation
- Use a warm, lightly humorous, and very human tone
- Start with a strong, relatable hook (a personal question or a shared feeling)
- Organize the script into 3 chapters based on the main ideas (mention "Chapter 1", "Chapter 2", "Chapter 3" naturally in the text)
- Add real-life relatable examples and emotional touches
- Include simple practical tips in a conversational way
- Smooth, natural transitions between sections
- Keep paragraphs short and sentences simple for easy reading aloud
- The total script length should be around 600–750 words
- NO lists, NO special formatting, NO bullet points, NO asterisks, NO text in brackets
- The output must ONLY contain the spoken script — nothing else
- Write it as if it will be directly read aloud by an AI voice
-End the script with a natural, genuine call to action encouraging the listener to connect, comment, or apply the idea shared, phrased warmly and conversationally

Make sure the final result is clean, pure, flowing text ready for an AI voiceover.
"""

    
    try:
        # Configure the Gemini API with your key
        # No need to check if API key is set - just configure it each time
        setup_gemini_api(app.config['GEMINI_API_KEY'])
           
        # Generate content with Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
       
        # Extract the generated text
        script_text = response.text
       
        # Return the generated script
        return jsonify({
            'success': True,
            'script': script_text
        })
    
    except Exception as e:
        print(f"Error generating script: {e}")
        return jsonify({'error': 'Failed to generate script. Please try again later.'}), 500

@app.route('/script-generator')
def script_generator():
    """Route for the AI script generator page"""
    return render_template('script_generator.html', voices=AVAILABLE_VOICES, languages=AVAILABLE_LANGUAGES)
    
if __name__ == '__main__':
    app.run(debug=True)