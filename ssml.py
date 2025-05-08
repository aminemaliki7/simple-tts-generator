import asyncio
import argparse
import os
from pathlib import Path
import edge_tts

# Define available voices with language grouping
AVAILABLE_VOICES = [
    # English voices
    {"id": "en-US-GuyNeural", "name": "Guy (Male, US)", "language": "English"},
    {"id": "en-US-JennyNeural", "name": "Jenny (Female, US)", "language": "English"},
    {"id": "en-GB-RyanNeural", "name": "Ryan (Male, UK)", "language": "English"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (Female, UK)", "language": "English"},
    {"id": "en-AU-NatashaNeural", "name": "Natasha (Female, Australian)", "language": "English"},
    
    # Arabic voices
    {"id": "ar-MA-JamalNeural", "name": "Jamal (Male, Moroccan)", "language": "Arabic"},
    {"id": "ar-EG-ShakirNeural", "name": "Shakir (Male, Egyptian)", "language": "Arabic"},
    
    # French voices
    {"id": "fr-FR-HenriNeural", "name": "Henri (Male)", "language": "French"},
    {"id": "fr-FR-DeniseNeural", "name": "Denise (Female)", "language": "French"},
    
    # German voices
    {"id": "de-DE-ConradNeural", "name": "Conrad (Male)", "language": "German"},
    {"id": "de-DE-KatjaNeural", "name": "Katja (Female)", "language": "German"},
    
    # Spanish voices
    {"id": "es-ES-AlvaroNeural", "name": "Álvaro (Male)", "language": "Spanish"},
    {"id": "es-ES-ElviraNeural", "name": "Elvira (Female)", "language": "Spanish"}
]

async def generate_speech_from_ssml(ssml_content, output_path, voice_id):
    """
    Generate speech from SSML content using Edge TTS
    """
    # Ensure SSML content is properly formatted with correct namespace
    if not ssml_content.strip().startswith('<speak'):
        ssml_content = f'<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" version="1.0">{ssml_content}</speak>'
    elif 'xmlns' not in ssml_content:
        ssml_content = ssml_content.replace('<speak', 
            '<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" version="1.0"')
    
    try:
        # Make sure we're using SSML mode
        # Use communicate_ssml method instead of Communicate if available
        if hasattr(edge_tts, 'communicate_ssml'):
            tts = edge_tts.communicate_ssml(ssml_content, voice_id,is_ssml=True)
        else:
            # Explicitly tell edge_tts this is SSML content
            tts = edge_tts.Communicate(text=ssml_content, voice=voice_id, is_ssml=True)
        
        # Generate speech and save to file
        await tts.save(output_path)
        
        print(f"Speech synthesized successfully and saved to '{output_path}'")
        return output_path
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return None

def list_available_voices():
    """Print a list of available voices"""
    print("\nAvailable voices:")
    # Group voices by language for better readability
    languages = {}
    for voice in AVAILABLE_VOICES:
        if voice["language"] not in languages:
            languages[voice["language"]] = []
        languages[voice["language"]].append(voice)
    
    # Print voices grouped by language
    for language, voices in languages.items():
        print(f"\n{language}:")
        for voice in voices:
            print(f"  - {voice['id']}: {voice['name']}")

async def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Generate high-quality audio from SSML using Edge TTS')
    parser.add_argument('-i', '--input', type=str, help='SSML input file path')
    parser.add_argument('-o', '--output', type=str, default='output.mp3', help='Output audio file path')
    parser.add_argument('-v', '--voice', type=str, default='en-US-JennyNeural', help='Voice ID to use')
    parser.add_argument('-l', '--list-voices', action='store_true', help='List available voices')
    parser.add_argument('-t', '--text', type=str, help='SSML text (alternative to input file)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # List voices if requested
    if args.list_voices:
        list_available_voices()
        return
    
    # Get SSML content
    ssml_content = None
    if args.text:
        ssml_content = args.text
    elif args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as file:
                ssml_content = file.read()
        except Exception as e:
            print(f"Error reading input file: {e}")
            return
    else:
        print("Error: Either --input or --text must be provided")
        parser.print_help()
        return
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate speech
    await generate_speech_from_ssml(ssml_content, str(output_path), args.voice)

if __name__ == "__main__":
    print("SSML Audio Generator (using Edge TTS)")
    print("------------------------------------")
    print("Generate high-quality audio from SSML markup")
    
    # Run the async main function
    asyncio.run(main())