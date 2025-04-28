import os
import tempfile
import time
from pydub import AudioSegment

async def generate_simple_tts(script_file, output_audio, voice_id, speed=1.0, depth=1):
    """Generate TTS audio with customizable speed and depth.
    
    Args:
        script_file: Path to the script file
        output_audio: Path for the output file
        voice_id: Voice ID to use for TTS (includes language selection)
        speed: Playback speed (1.0 = normal, <1.0 = slower, >1.0 = faster)
        depth: Voice depth level (1-5, higher values = deeper voice tone)
        
    Returns:
        Path to the generated audio file
    """
    print(f"Generating voice with {voice_id}, speed={speed}, depth={depth}...")
    
    # Read the script
    with open(script_file, 'r', encoding='utf-8') as file:
        script = file.read()
    
    # Create directory for temporary files
    temp_dir = os.path.join(tempfile.gettempdir(), 'tts_generator')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        from edge_tts import Communicate
        
        # Generate base TTS with specified speed
        temp_audio_file = os.path.join(temp_dir, f'base_tts_{int(time.time())}.mp3')
        communicate = Communicate(script, voice_id)
        
        # Apply speed setting
        if speed != 1.0:
            # Convert speed to rate percentage (inverse relationship)
            # slower speed (0.5) = higher rate (200%)
            # higher speed (2.0) = lower rate (50%)
            rate_percentage = int((1.0/speed) * 100)
            communicate.rate = f"{rate_percentage}%"
            
        await communicate.save(temp_audio_file)
        
        # Check if the audio file was created successfully
        if os.path.exists(temp_audio_file) and os.path.getsize(temp_audio_file) > 0:
            print("Successfully generated voice audio file")
        else:
            raise Exception("Failed to generate audio with voice")
        
        # Apply depth processing if needed
        if depth > 1:
            audio = AudioSegment.from_file(temp_audio_file)
            
            # Simple depth processing using low-pass filter
            cutoff_frequency = 12000 - (depth * 1000)  # Lower cutoff for deeper voice
            processed_audio = audio.low_pass_filter(cutoff_frequency)
            
            # Add basic fade in/out
            fade_time = min(200, len(processed_audio) // 20)
            processed_audio = processed_audio.fade_in(fade_time).fade_out(fade_time)
            
            # Save processed audio
            processed_file = os.path.join(temp_dir, f'processed_voice_{int(time.time())}.mp3')
            processed_audio.export(processed_file, format="mp3", bitrate="192k")
            return processed_file
        else:
            return temp_audio_file
            
    except ImportError:
        print("Required libraries not found, installing...")
        import subprocess
        subprocess.call(["pip", "install", "edge-tts"])
        from edge_tts import Communicate
        
        # Try again after installation
        temp_audio_file = os.path.join(temp_dir, f'base_tts_{int(time.time())}.mp3')
        communicate = Communicate(script, voice_id)
        
        # Apply speed setting on retry
        if speed != 1.0:
            rate_percentage = int((1.0/speed) * 100)
            communicate.rate = f"{rate_percentage}%"
            
        await communicate.save(temp_audio_file)
        return temp_audio_file
        
    except Exception as e:
        print(f"Error generating TTS: {e}")
        
        # Create a silent audio file as fallback
        silent_file = os.path.join(temp_dir, f'silent_{int(time.time())}.mp3')
        silence = AudioSegment.silent(duration=5000)
        silence.export(silent_file, format="mp3")
        return silent_file