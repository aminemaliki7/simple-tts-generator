import os
import tempfile
import time
from pydub import AudioSegment
from pydub.effects import low_pass_filter, speedup

async def generate_simple_tts(script_file, output_audio, voice_id, speed=-0.1, depth=9, is_ssml=False):
    """Generate TTS audio with customizable speed and depth.
   
    Args:
        script_file: Path to the script file
        output_audio: Path for the output file
        voice_id: Voice ID to use for TTS (includes language selection)
        speed: Playback speed (1.0 = normal, <1.0 = slower, >1.0 = faster)
        depth: Voice depth level (1-5, higher values = deeper voice tone)
        is_ssml: Whether the input is SSML markup
       
    Returns:
        Path to the generated audio file
    """
    print(f"Generating voice with {voice_id}, speed={speed}, depth={depth}...,SSML={is_ssml}")
   
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
       
        # Apply speed setting for edge-tts
        # Note: We'll apply additional speed processing later for more dramatic effect
        if speed != 1.0:
            # Convert speed to rate percentage with enhanced effect
            # We'll use both edge-tts rate AND pydub speedup for more noticeable effect
            rate_percentage = int((1.0/speed) * 100)
            print(f"Setting edge-tts rate to: {rate_percentage}%")
            communicate.rate = f"{rate_percentage}%"
           
        await communicate.save(temp_audio_file)
       
        # Check if the audio file was created successfully
        if os.path.exists(temp_audio_file) and os.path.getsize(temp_audio_file) > 0:
            print("Successfully generated voice audio file")
        else:
            raise Exception("Failed to generate audio with voice")
       
        # Load audio for processing
        audio = AudioSegment.from_file(temp_audio_file)
        
        # Process speed again for more dramatic effect if needed (for very slow or very fast)
        if speed < 0.8 or speed > 1.2:
            # Apply additional speed adjustment using pydub
            # For slow speech: stretch it further
            # For fast speech: speed it up more
            if speed < 0.8:
                # For slow speech, we need to lengthen it more (use a lower playback speed)
                playback_speed = 0.85  # Additional slowing
                audio = speedup(audio, playback_speed=playback_speed)
                print(f"Applied additional slowdown with factor: {playback_speed}")
            elif speed > 1.2:
                # For fast speech, increase speed further
                playback_speed = 1.15  # Additional speedup
                audio = speedup(audio, playback_speed=playback_speed)
                print(f"Applied additional speedup with factor: {playback_speed}")
       
        # Apply enhanced depth processing if needed
        if depth > 1:
            # More dramatic cutoff frequency range for deeper voice effect
            # Original: 12000 - (depth * 1000) = range of 11000-8000
            # New: 18000 - (depth * 3000) = range of 15000-6000
            cutoff_frequency = 18000 - (depth * 3000)  # Much lower cutoff for deeper voice
            print(f"Applying low-pass filter with cutoff: {cutoff_frequency}Hz")
            processed_audio = low_pass_filter(audio, cutoff_frequency)
            
            # Add bass boost for deeper voice effect
            # We'll boost frequencies below 300Hz
            # Higher depth = more bass boost
            bass_boost_db = (depth - 1) * 3  # 0, 3, 6, 9, 12 dB boost
            if bass_boost_db > 0:
                print(f"Applying bass boost: +{bass_boost_db}dB")
                # Create a bass-boosted version
                bass_part = processed_audio.low_pass_filter(300)  # Get just the bass frequencies
                bass_part = bass_part + bass_boost_db  # Boost the bass
                # Mix the boosted bass back with the original
                processed_audio = processed_audio.overlay(bass_part)
           
            # Add basic fade in/out
            fade_time = min(200, len(processed_audio) // 20)
            processed_audio = processed_audio.fade_in(fade_time).fade_out(fade_time)
           
            # Save processed audio
            processed_file = os.path.join(temp_dir, f'processed_voice_{int(time.time())}.mp3')
            processed_audio.export(processed_file, format="mp3", bitrate="192k")
            return processed_file
        else:
            # Return the speed-adjusted file
            if speed < 0.8 or speed > 1.2:
                # Save the speed-processed file
                speed_processed_file = os.path.join(temp_dir, f'speed_processed_{int(time.time())}.mp3')
                audio.export(speed_processed_file, format="mp3", bitrate="192k")
                return speed_processed_file
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