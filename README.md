# Voice Generator

A sophisticated web application for generating natural-sounding voice audio from text using advanced AI technology. This project allows users to convert text to speech with multiple voice options across various languages, customize speech parameters, and easily manage generated audio files.

## Features

### Text-to-Speech Conversion
- Multiple voice options across numerous languages
- Support for English, Arabic, French, German, Spanish, Italian, and Portuguese
- Male and female voices with regional accents (US, UK, Australian, etc.)
- Customizable speech parameters:
  - Adjustable speech speed
  - Emotion depth control
  - SSML (Speech Synthesis Markup Language) support

### AI Content Generation
- AI-powered script generator for various content types:
  - Short-form video scripts (30-60 seconds)
  - YouTube video scripts with chapter structure
- Natural, conversational tone tailored to content type

### User Experience
- Clean, modern dark-themed interface
- Real-time job status tracking
- Instant audio preview before download
- Comprehensive job history and management
- Mobile-responsive design

## Technical Details

### Backend
- **Flask**: Python web framework for the application
- **Azure Text-to-Speech API**: For high-quality voice synthesis
- **Google Gemini AI**: For script generation capabilities
- **Asynchronous processing**: Background job handling for better user experience

### Frontend
- **Bootstrap 5**: For responsive UI components
- **Custom CSS**: Modern dark theme with accessibility in mind
- **JavaScript**: Enhanced user interactions and audio player
- **Font Awesome**: For iconography

### Data Storage
- File-based storage for generated audio
- Session-based job tracking
- Optional MongoDB integration (in progress)

## Project Structure

```
voice-generator/
├── app.py              # Main Flask application
├── tts.py              # Text-to-speech generation module
├── templates/          # HTML templates
│   ├── index.html      # Main page for text input
│   ├── status.html     # Job status page
│   ├── dashboard.html  # Job history dashboard
│   ├── ssml.html       # SSML input page
│   ├── script_generator.html  # Script generation page
│   └── shorts_generator.html  # Short-form content generator
├── static/             # Static assets (CSS, JS)
├── uploads/            # Temporary storage for text input
└── outputs/            # Generated audio files
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Internet connection for API access

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/voice-generator.git
   cd voice-generator
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   AZURE_SPEECH_KEY=your_azure_speech_key
   AZURE_SPEECH_REGION=your_azure_region
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage Guide

### Basic Text-to-Speech
1. Navigate to the home page
2. Enter your text or upload a text file
3. Select your preferred voice
4. Adjust speed and emotion depth as needed
5. Click "Generate Voice" to create your audio
6. Preview the audio and download when ready

### SSML Advanced Usage
1. Navigate to the SSML page
2. Enter your SSML markup
3. Select voice options
4. Submit to generate enhanced audio with precise control

### AI Script Generation
1. Navigate to the Script Generator page
2. Enter your video title and main ideas
3. Let AI generate a professionally structured script
4. Use the generated script in the text-to-speech tool

### Short-form Content
1. Navigate to the Shorts Generator page
2. Enter your topic
3. Get a concise, engaging script optimized for short-form content
4. Convert to audio with the voice of your choice

## Customization

The application can be extended with:
- Additional voice options
- New language support
- Enhanced audio controls
- Database integration for persistent storage
- User authentication
- API access for third-party integration

## Contributing

Contributions to improve Voice Generator are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues, questions, or feedback, please create an issue in the GitHub repository or contact the maintainer directly.

---

Created by Amine
