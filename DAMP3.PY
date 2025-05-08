#!/usr/bin/env python3
import os
import argparse
import subprocess
import shutil

def download_mp3(url, output_path='youtube audio', filename=None):
    """
    Download audio from a video URL and save as MP3.
   
    Args:
        url (str): URL of the video
        output_path (str): Directory to save the MP3 file
        filename (str): Output filename (without extension)
   
    Returns:
        str: Path to the saved MP3 file
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
       
        # Set output filename format
        output_template = os.path.join(output_path, "%(title)s.%(ext)s")
        if filename:
            output_template = os.path.join(output_path, f"{filename}.%(ext)s")
       
        print(f"Downloading audio from: {url}")
       
        # Use yt-dlp to download and convert directly to MP3
        cmd = [
            'yt-dlp',
            '-x',                    # Extract audio
            '--audio-format', 'mp3', # Convert to MP3
            '--audio-quality', '0',  # Best quality
            '-o', output_template,   # Output filename template
            '--no-playlist',         # Don't download playlists
            url                      # Video URL
        ]
       
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
       
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
       
        # Find the filename from the output
        for line in result.stdout.split('\n'):
            if '[ExtractAudio] Destination:' in line:
                mp3_file = line.split('[ExtractAudio] Destination: ')[1]
                print(f"Successfully downloaded: {mp3_file}")
                return mp3_file
       
        # If we can't find the filename in the output, look for MP3 files in the directory
        if not filename:
            print("Successfully downloaded MP3 file.")
            return None
        else:
            mp3_path = os.path.join(output_path, f"{filename}.mp3")
            if os.path.exists(mp3_path):
                print(f"Successfully downloaded: {mp3_path}")
                return mp3_path
            else:
                print("Download completed but could not locate the MP3 file.")
                return None
           
    except subprocess.CalledProcessError as e:
        print(f"Error executing yt-dlp: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return None
       
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Download MP3 audio from a video URL')
    parser.add_argument('url', help='URL of the video')
    parser.add_argument('-o', '--output', default='youtube audio', help='Output directory')
    parser.add_argument('-f', '--filename', help='Output filename (without extension)')
   
    args = parser.parse_args()
   
    # Check if yt-dlp is installed
    if shutil.which('yt-dlp') is None:
        print("Error: yt-dlp is not installed.")
        print("Please install it with: pip install yt-dlp")
        return
   
    download_mp3(args.url, args.output, args.filename)

if __name__ == "__main__":
    main()