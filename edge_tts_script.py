#!/usr/bin/env python3
"""
TTS Generator with Advanced Options

This script generates high-quality audio from text using Microsoft Edge TTS
with advanced options for audio segmentation, processing, and playback.
It includes comprehensive debugging and error handling.

Usage:
  python tts_generator.py --text "Text to convert to speech" --output output.mp3
  python tts_generator.py --file input.txt --output output.mp3
  python tts_generator.py --list-voices
  python tts_generator.py --play "Text to speak directly"

Requirements:
  pip install edge-tts numpy soundfile pyaudio
"""

import os
import sys
import json
import time
import asyncio
import argparse
import tempfile
import threading
from datetime import datetime
from pathlib import Path

try:
    import edge_tts
    import numpy as np
    import soundfile as sf
    import pyaudio
except ImportError as e:
    print(f"Error importing required libraries: {str(e)}")
    print("Please install required packages: pip install edge-tts numpy soundfile pyaudio")
    sys.exit(1)

# Constants
DEFAULT_VOICE = "en-US-JennyNeural"
DEFAULT_RATE = "+0%"
DEFAULT_VOLUME = "+0%"
DEFAULT_PITCH = "+0Hz"
MAX_SEGMENT_LENGTH = 3000  # Maximum text segment length to ensure stability

# Configure debug logging
DEBUG_MODE = True  # Set to False to disable verbose debug output
LOG_FILE = "tts_generator.log"

def log_debug(message, to_console=True, to_file=True):
    """
    Log debug messages with timestamp
    
    Args:
        message: The message to log
        to_console: Whether to print to console
        to_file: Whether to write to log file
    """
    if not DEBUG_MODE and to_console:
        return
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted_message = f"[DEBUG] {timestamp} - {message}"
    
    # Write to console
    if to_console:
        print(formatted_message)
    
    # Write to file
    if to_file:
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(formatted_message + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {str(e)}")

def segment_text(text, max_length=MAX_SEGMENT_LENGTH):
    """
    Split text into smaller segments for better TTS processing
    
    Args:
        text: Text to segment
        max_length: Maximum length of each segment
    
    Returns:
        List of text segments
    """
    log_debug(f"Segmenting text of length {len(text)} characters")
    
    # If text is shorter than max_length, return as single segment
    if len(text) <= max_length:
        log_debug(f"Text is shorter than max length, returning as single segment")
        return [text]
    
    segments = []
    current_pos = 0
    
    while current_pos < len(text):
        # Find a good breaking point (end of sentence or paragraph)
        end_pos = min(current_pos + max_length, len(text))
        
        if end_pos < len(text):
            # Try to find sentence or paragraph breaks
            for delim in ['\n\n', '\n', '. ', '! ', '? ', '; ']:
                last_delim = text.rfind(delim, current_pos, end_pos)
                if last_delim != -1:
                    end_pos = last_delim + len(delim)
                    break
        
        # Extract segment and add to list
        segment = text[current_pos:end_pos].strip()
        if segment:
            segments.append(segment)
            log_debug(f"Created segment {len(segments)}: {len(segment)} characters")
        
        current_pos = end_pos
    
    log_debug(f"Text segmented into {len(segments)} parts")
    return segments

def clean_text(text):
    """
    Clean text to avoid potential SSML interpretation issues
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    log_debug("Cleaning text for TTS processing")
    
    # Replace characters that might cause SSML issues
    replacements = {
        '<': ' less than ',
        '>': ' greater than ',
        '&': ' and ',
        '"': ' quote ',
        "'": ' apostrophe ',
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    log_debug(f"Text cleaned, length: {len(text)} characters")
    return text

async def get_available_voices():
    """
    Get all available voices from Edge TTS
    
    Returns:
        List of voice dictionaries
    """
    log_debug("Retrieving available voices")
    
    try:
        voices = await edge_tts.list_voices()
        log_debug(f"Successfully retrieved {len(voices)} voices")
        return voices
    except Exception as e:
        log_debug(f"ERROR: Failed to retrieve voices: {str(e)}")
        return []

async def generate_speech_segment(text, output_file, voice=DEFAULT_VOICE, rate=DEFAULT_RATE, 
                                 volume=DEFAULT_VOLUME, pitch=DEFAULT_PITCH):
    """
    Generate speech for a single text segment
    
    Args:
        text: Text to synthesize
        output_file: Output file path
        voice: Voice to use
        rate: Speech rate
        volume: Speech volume
        pitch: Speech pitch
    
    Returns:
        True if successful, False otherwise
    """
    log_debug(f"Generating speech for segment: {len(text)} characters")
    log_debug(f"Parameters - Voice: {voice}, Rate: {rate}, Volume: {volume}, Pitch: {pitch}")
    
    try:
        # Clean text to ensure it doesn't have SSML interpretation issues
        clean_text_content = clean_text(text)
        
        # Create communicate object
        communicate = edge_tts.Communicate(
            clean_text_content, 
            voice, 
            rate=rate, 
            volume=volume,
            pitch=pitch
        )
        
        # Save to file
        log_debug(f"Saving speech to file: {output_file}")
        await communicate.save(output_file)
        
        # Verify file was created
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            log_debug(f"Successfully saved speech segment: {os.path.getsize(output_file)} bytes")
            return True
        else:
            log_debug(f"ERROR: Output file is empty or not created: {output_file}")
            return False
            
    except Exception as e:
        log_debug(f"ERROR: Failed to generate speech: {str(e)}")
        return False

async def generate_speech(text, output_file, voice=DEFAULT_VOICE, rate=DEFAULT_RATE, 
                         volume=DEFAULT_VOLUME, pitch=DEFAULT_PITCH, segment_audio=True):
    """
    Generate speech from text, segmenting if necessary
    
    Args:
        text: Text to synthesize
        output_file: Output file path
        voice: Voice to use
        rate: Speech rate
        volume: Speech volume
        pitch: Speech pitch
        segment_audio: Whether to segment text for better quality
    
    Returns:
        True if successful, False otherwise
    """
    log_debug(f"Starting speech generation for {len(text)} characters of text")
    
    # Prepare output directory if needed
    output_path = Path(output_file)
    os.makedirs(output_path.parent, exist_ok=True)
    
    if not segment_audio or len(text) <= MAX_SEGMENT_LENGTH:
        # For shorter text, no need to segment
        log_debug("Processing text as a single segment")
        return await generate_speech_segment(
            text, output_file, voice, rate, volume, pitch
        )
    else:
        # For longer text, segment and merge
        log_debug("Processing text as multiple segments")
        segments = segment_text(text)
        
        if not segments:
            log_debug("ERROR: Text segmentation resulted in no segments")
            return False
            
        # Create a temporary directory for segment files
        with tempfile.TemporaryDirectory() as temp_dir:
            log_debug(f"Created temporary directory: {temp_dir}")
            segment_files = []
            
            # Generate speech for each segment
            for i, segment in enumerate(segments):
                segment_file = os.path.join(temp_dir, f"segment_{i:03d}.wav")
                success = await generate_speech_segment(
                    segment, segment_file, voice, rate, volume, pitch
                )
                
                if success:
                    segment_files.append(segment_file)
                else:
                    log_debug(f"ERROR: Failed to generate segment {i}")
            
            if not segment_files:
                log_debug("ERROR: No segments were successfully generated")
                return False
                
            # Merge audio segments
            log_debug(f"Merging {len(segment_files)} audio segments")
            try:
                merge_audio_files(segment_files, output_file)
                log_debug(f"Successfully merged audio to: {output_file}")
                return True
            except Exception as e:
                log_debug(f"ERROR: Failed to merge audio segments: {str(e)}")
                return False

def merge_audio_files(input_files, output_file):
    """
    Merge multiple audio files into a single file
    
    Args:
        input_files: List of input audio file paths
        output_file: Output audio file path
    """
    log_debug(f"Merging {len(input_files)} audio files")
    
    # Load and concatenate audio data
    audio_data = []
    sample_rate = None
    
    for file_path in input_files:
        log_debug(f"Loading audio file: {file_path}")
        data, rate = sf.read(file_path)
        
        if sample_rate is None:
            sample_rate = rate
        elif rate != sample_rate:
            log_debug(f"WARNING: Sample rate mismatch: {rate} vs {sample_rate}")
        
        audio_data.append(data)
    
    # Concatenate audio data
    merged_data = np.concatenate(audio_data)
    
    # Write merged audio to output file
    log_debug(f"Writing merged audio to: {output_file}")
    sf.write(output_file, merged_data, sample_rate)
    
    # Verify output file
    output_size = os.path.getsize(output_file)
    log_debug(f"Merged audio file created: {output_size} bytes")

def play_audio_file(file_path):
    """
    Play an audio file using PyAudio
    
    Args:
        file_path: Path to audio file to play
    """
    log_debug(f"Playing audio file: {file_path}")
    
    try:
        # Load audio file
        audio_data, sample_rate = sf.read(file_path)
        
        # Convert to expected format if needed
        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]  # Use first channel if stereo
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sample_rate,
            output=True
        )
        
        # Play audio
        log_debug(f"Starting audio playback, sample rate: {sample_rate}Hz")
        stream.write(audio_data.astype(np.float32).tobytes())
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        log_debug("Audio playback completed")
        
    except Exception as e:
        log_debug(f"ERROR: Failed to play audio: {str(e)}")

async def play_speech_directly(text, voice=DEFAULT_VOICE, rate=DEFAULT_RATE, 
                             volume=DEFAULT_VOLUME, pitch=DEFAULT_PITCH):
    """
    Generate and play speech directly without saving to file
    
    Args:
        text: Text to synthesize and play
        voice: Voice to use
        rate: Speech rate
        volume: Speech volume
        pitch: Speech pitch
    
    Returns:
        True if successful, False otherwise
    """
    log_debug("Playing speech directly")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        # Generate speech to temporary file
        success = await generate_speech(
            text, temp_path, voice, rate, volume, pitch
        )
        
        if not success:
            log_debug("ERROR: Failed to generate speech for direct playback")
            return False
        
        # Play the temporary file
        play_audio_file(temp_path)
        
        return True
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
            log_debug(f"Removed temporary file: {temp_path}")
        except Exception as e:
            log_debug(f"Warning: Failed to remove temporary file: {str(e)}")

async def list_and_print_voices():
    """List and print all available voices"""
    voices = await get_available_voices()
    
    if not voices:
        print("Failed to retrieve voices. Check the log for details.")
        return
    
    print("\nAvailable Voices:")
    print("-" * 100)
    print(f"{'Voice Name':<30} {'Gender':<10} {'Locale':<10} {'Voice Type':<15}")
    print("-" * 100)
    
    for voice in sorted(voices, key=lambda v: (v['Locale'], v['ShortName'])):
        name = voice['ShortName']
        gender = voice['Gender']
        locale = voice['Locale']
        voice_type = "Neural" if "Neural" in name else "Standard"
        
        print(f"{name:<30} {gender:<10} {locale:<10} {voice_type:<15}")
    
    print("-" * 100)
    print(f"Total Voices: {len(voices)}\n")

async def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Generate high-quality TTS audio using Edge TTS")
    
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--text", "-t", help="Text to convert to speech", type=str)
    input_group.add_argument("--file", "-f", help="Text file to read content from", type=str)
    input_group.add_argument("--play", "-p", help="Generate and play speech directly", type=str)
    input_group.add_argument("--list-voices", "-l", help="List available voices", action="store_true")
    
    parser.add_argument("--output", "-o", help="Output audio file path", default="output.mp3", type=str)
    parser.add_argument("--voice", "-v", help="Voice to use", default=DEFAULT_VOICE, type=str)
    parser.add_argument("--rate", "-r", help="Speech rate (e.g. +0%, -10%)", default=DEFAULT_RATE, type=str)
    parser.add_argument("--volume", "-vol", help="Volume level (e.g. +0%, +50%)", default=DEFAULT_VOLUME, type=str)
    parser.add_argument("--pitch", "-pit", help="Speech pitch (e.g. +0Hz, -2Hz)", default=DEFAULT_PITCH, type=str)
    parser.add_argument("--no-segment", "-ns", help="Disable text segmentation", action="store_true")
    parser.add_argument("--debug", "-d", help="Enable debug mode", action="store_true")
    
    args = parser.parse_args()
    
    # Update debug mode based on args
    global DEBUG_MODE
    DEBUG_MODE = args.debug if args.debug is not None else DEBUG_MODE
    
    log_debug("Script started")
    
    # Handle list voices option
    if args.list_voices:
        log_debug("Listing available voices")
        await list_and_print_voices()
        return
    
    # Handle direct playback
    if args.play:
        log_debug(f"Direct playback requested: {len(args.play)} characters")
        await play_speech_directly(
            args.play,
            voice=args.voice,
            rate=args.rate,
            volume=args.volume,
            pitch=args.pitch
        )
        return
    
    # Ensure we have input text
    if not args.text and not args.file:
        log_debug("ERROR: No text input provided. Use --text, --file, or --play")
        parser.print_help()
        return
    
    # Read text from file if specified
    if args.file:
        try:
            log_debug(f"Reading text from file: {args.file}")
            with open(args.file, 'r', encoding='utf-8') as f:
                text_content = f.read()
            log_debug(f"Successfully read {len(text_content)} characters from file")
        except Exception as e:
            log_debug(f"ERROR: Failed to read file: {str(e)}")
            print(f"Error reading file: {str(e)}")
            return
    else:
        text_content = args.text
        log_debug(f"Using provided text input ({len(text_content)} characters)")
    
    # Generate the speech
    log_debug(f"Generating speech with voice: {args.voice}")
    start_time = time.time()
    
    success = await generate_speech(
        text_content,
        args.output,
        voice=args.voice,
        rate=args.rate,
        volume=args.volume,
        pitch=args.pitch,
        segment_audio=not args.no_segment
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    if success:
        log_debug(f"Speech generation completed successfully in {duration:.2f} seconds")
        print(f"\nSpeech generated successfully: {args.output} ({duration:.2f} seconds)")
        
        # Get file size
        file_size = os.path.getsize(args.output)
        print(f"File size: {file_size/1024:.2f} KB")
    else:
        log_debug("Speech generation failed")
        print("\nSpeech generation failed. Check debug log for details.")

# Additional utility functions
def format_duration(milliseconds):
    """Format milliseconds to HH:MM:SS.mmm format"""
    seconds, ms = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"

def create_subtitles_vtt(word_boundaries, output_file):
    """
    Create WebVTT subtitles from word boundaries
    
    Args:
        word_boundaries: List of word boundary data
        output_file: Path to output VTT file
    """
    log_debug(f"Creating WebVTT subtitles: {output_file}")
    
    lines = ["WEBVTT", ""]
    current_line = ""
    line_start = None
    line_end = None
    
    for word in word_boundaries:
        if not current_line:
            current_line = word["text"]
            line_start = word["offset"] / 10000  # Convert to milliseconds
            line_end = (word["offset"] + word["duration"]) / 10000
        elif len(current_line) + len(word["text"]) + 1 <= 80:  # Max 80 chars per line
            current_line += " " + word["text"]
            line_end = (word["offset"] + word["duration"]) / 10000
        else:
            # Write completed line
            lines.append(f"{format_duration(line_start)} --> {format_duration(line_end)}")
            lines.append(current_line)
            lines.append("")
            
            # Start new line
            current_line = word["text"]
            line_start = word["offset"] / 10000
            line_end = (word["offset"] + word["duration"]) / 10000
    
    # Add the last line if not empty
    if current_line:
        lines.append(f"{format_duration(line_start)} --> {format_duration(line_end)}")
        lines.append(current_line)
    
    # Write VTT file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    log_debug(f"WebVTT subtitles created with {len(lines)} lines")

# Example of streaming audio generation using Edge TTS
async def stream_speech_to_speaker(text, voice=DEFAULT_VOICE, rate=DEFAULT_RATE, 
                                  volume=DEFAULT_VOLUME, pitch=DEFAULT_PITCH):
    """
    Stream speech directly to speakers as it's being generated
    
    Args:
        text: Text to synthesize
        voice: Voice to use
        rate: Speech rate
        volume: Speech volume
        pitch: Speech pitch
    """
    log_debug("Streaming speech to speakers")
    
    try:
        # Clean text to ensure it doesn't have SSML interpretation issues
        clean_text_content = clean_text(text)
        
        # Create communicate object
        communicate = edge_tts.Communicate(
            clean_text_content, 
            voice, 
            rate=rate, 
            volume=volume,
            pitch=pitch
        )
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = None
        
        # Process audio chunks as they arrive
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                # Initialize audio stream with first chunk if not already done
                if stream is None:
                    log_debug("Initializing audio stream")
                    stream = p.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=24000,  # Edge TTS typically uses 24kHz
                        output=True
                    )
                
                # Play the audio chunk
                stream.write(chunk["data"])
                
            elif chunk["type"] == "WordBoundary":
                # Can be used for visualization or subtitles in real-time
                log_debug(f"Word: {chunk['text']}, Offset: {chunk['offset']}, Duration: {chunk['duration']}")
        
        # Cleanup
        if stream:
            log_debug("Closing audio stream")
            stream.stop_stream()
            stream.close()
        
        p.terminate()
        log_debug("Streaming completed")
        
        return True
        
    except Exception as e:
        log_debug(f"ERROR: Failed to stream speech: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Initialize log file
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"[LOG START] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Run the main function
        asyncio.run(main())
        
    except KeyboardInterrupt:
        log_debug("Script interrupted by user", to_file=True)
        print("\nScript interrupted by user")
        
    except Exception as e:
        log_debug(f"Unhandled error: {str(e)}", to_file=True)
        print(f"\nError: {str(e)}")
        
    finally:
        log_debug(f"[LOG END] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", to_file=True)