import os
import tempfile
import time
import re
from pydub import AudioSegment
from pydub.effects import low_pass_filter, speedup

async def generate_simple_tts(script_file, output_audio, voice_id, speed=0.3, depth=9, is_ssml=False):
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
    
    # Pre-process script to improve fluency if it's not SSML
    if not is_ssml:
        script = preprocess_script_for_fluency(script)
   
    # Create directory for temporary files
    temp_dir = os.path.join(tempfile.gettempdir(), 'tts_generator')
    os.makedirs(temp_dir, exist_ok=True)
   
    try:
        from edge_tts import Communicate
       
        # Generate base TTS with specified speed
        temp_audio_file = os.path.join(temp_dir, f'base_tts_{int(time.time())}.mp3')
        communicate = Communicate(script, voice_id)
       
        # Apply speed setting for edge-tts
        if speed != 1.0:
            # Convert speed to rate percentage
            rate_percentage = int((1.0/speed) * 100)
            print(f"Setting edge-tts rate to: {rate_percentage}%")
            communicate.rate = f"{rate_percentage}%"
        
        # Set pitch to make the voice more consistent
        pitch_adjustment = "+0Hz"  # Neutral setting
        communicate.pitch = pitch_adjustment
        
        # Reduce break times for more fluent speech
        # This affects how long pauses are between sentences
        communicate.silence_duration = 50  # Milliseconds, default is 200-800ms
        
        await communicate.save(temp_audio_file)
       
        # Check if the audio file was created successfully
        if os.path.exists(temp_audio_file) and os.path.getsize(temp_audio_file) > 0:
            print("Successfully generated voice audio file")
        else:
            raise Exception("Failed to generate audio with voice")
       
        # Load audio for processing
        audio = AudioSegment.from_file(temp_audio_file)
        
        # Process speed again for more dramatic effect if needed
        if speed < 0.8 or speed > 1.2:
            # Apply additional speed adjustment using pydub
            if speed < 0.8:
                # For slow speech, reduce additional slowing to maintain fluency
                playback_speed = 0.9  # Less slowing to preserve flow
                audio = speedup(audio, playback_speed=playback_speed)
                print(f"Applied fluency-preserving slowdown with factor: {playback_speed}")
            elif speed > 1.2:
                # For fast speech, increase speed further
                playback_speed = 1.15  # Additional speedup
                audio = speedup(audio, playback_speed=playback_speed)
                print(f"Applied additional speedup with factor: {playback_speed}")
       
        # Apply enhanced depth processing if needed
        if depth > 1:
            # Use a higher cutoff frequency to maintain speech clarity
            cutoff_frequency = 18000 - (depth * 1200)  # Even gentler range: 16800-12000 Hz
            print(f"Applying fluency-optimized filter with cutoff: {cutoff_frequency}Hz")
            
            # Apply a gentler low-pass filter
            processed_audio = low_pass_filter(audio, cutoff_frequency)
            
            # Apply mid-range enhancement for depth without affecting fluency
            if depth > 1:
                # More moderate bass enhancement
                bass_boost_db = (depth - 1) * 1.5  # Gentler: 0, 1.5, 3, 4.5, 6 dB boost
                print(f"Applying fluency-focused enhancement: +{bass_boost_db}dB")
                
                # Focus on mid-range frequencies that don't disrupt speech flow
                # Avoid very low frequencies completely
                mid_range = processed_audio.high_pass_filter(180).low_pass_filter(700)
                mid_range = mid_range + bass_boost_db
                
                # Mix the boosted mid-range back with the original
                processed_audio = processed_audio.overlay(mid_range)
           
            # Add short fade in/out to avoid clicks
            fade_time = min(100, len(processed_audio) // 30)
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

def preprocess_script_for_fluency(script):
    """
    Preprocess the script to improve fluency by reducing unnecessarily long pauses
    without using SSML tags
    """
    # Replace multiple newlines with single newlines to reduce pauses
    script = re.sub(r'\n{2,}', '\n', script)
    
    # Replace periods followed by newlines with just periods
    # This prevents double-pausing at sentence ends
    script = re.sub(r'\.\n', '. ', script)
    
    # Replace excessive spacing
    script = re.sub(r' {2,}', ' ', script)
    
    # Normalize ellipses to prevent long pauses
    script = re.sub(r'\.{3,}', '...', script)
    
    # Remove extra pauses from common punctuation combinations
    script = re.sub(r'\. +\.', '.', script)  # Remove "dot space dot" patterns
    script = re.sub(r'\, +\.', '.', script)  # Replace "comma space dot" with just dot
    
    # Handle em dashes and other pause-inducing punctuation
    script = re.sub(r' — ', ', ', script)  # Replace em dashes with commas for shorter pauses
    script = re.sub(r' -- ', ', ', script)  # Replace double hyphens with commas
    
    # Replace multiple spaces with single space
    script = re.sub(r' +', ' ', script)
    
    # Add a comma before "but" and "and" if not present to create a natural pause
    script = re.sub(r'(?<!\,) but ', ', but ', script)
    script = re.sub(r'(?<!\,) and ', ', and ', script)
    
    # Remove excess punctuation that might cause long pauses
    script = re.sub(r'[\!\?\.]+(?=[\!\?\.])', '', script)
    
    return script