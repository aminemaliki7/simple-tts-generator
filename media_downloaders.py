import os
import subprocess
import shutil
import re
import time
import uuid
from urllib.parse import urlparse

def download_mp3(url, output_path='youtube_audio', filename=None):
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
        
        # Generate a unique filename if none provided
        if not filename:
            filename = f"audio_{uuid.uuid4().hex[:8]}"
        
        # Ensure filename is safe
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        output_file = os.path.join(output_path, f"{filename}.mp3")
       
        print(f"Downloading audio from: {url}")
       
        # Use yt-dlp to download and convert directly to MP3
        cmd = [
            'yt-dlp',
            '-x',                    # Extract audio
            '--audio-format', 'mp3', # Convert to MP3
            '--audio-quality', '0',  # Best quality
            '-o', output_file,       # Output filename
            '--no-playlist',         # Don't download playlists
            url                      # Video URL
        ]
       
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
       
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        
        # Check if file exists
        if os.path.exists(output_file):
            print(f"Successfully downloaded: {output_file}")
            return output_file
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

def download_pinterest_video(url, output_path='pinterest_videos', filename=None):
    """
    Download video from a Pinterest URL and save it.
    
    Args:
        url (str): Pinterest URL of the video
        output_path (str): Directory to save the video file
        filename (str): Output filename (without extension)
    
    Returns:
        str: Path to the saved video file
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Validate Pinterest URL
        parsed_url = urlparse(url)
        if 'pinterest' not in parsed_url.netloc:
            print("Error: URL does not appear to be a Pinterest link.")
            return None
        
        # Extract pin ID for filename
        pin_id = None
        if '/pin/' in url:
            pin_id_match = re.search(r'/pin/(\d+)', url)
            if pin_id_match:
                pin_id = pin_id_match.group(1)
        
        # Set output filename
        if filename:
            filename = re.sub(r'[^\w\-_.]', '_', filename)  # Ensure filename is safe
            output_filename = f"{filename}.mp4"
        elif pin_id:
            output_filename = f"pinterest_{pin_id}.mp4"
        else:
            output_filename = f"pinterest_{uuid.uuid4().hex[:8]}.mp4"
        
        output_file = os.path.join(output_path, output_filename)
        
        # Use yt-dlp to download the Pinterest video
        cmd = [
            'yt-dlp',
            '--merge-output-format', 'mp4',  # Ensure output is MP4
            '-o', output_file,               # Output filename
            '--no-warnings',                 # Suppress warnings
            url                              # Pinterest URL
        ]
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Try alternate approach if first attempt fails
            alt_cmd = [
                'yt-dlp',
                '-f', 'b',          # Use best format
                '--merge-output-format', 'mp4',
                '-o', output_file,
                url
            ]
            
            alt_result = subprocess.run(alt_cmd, capture_output=True, text=True)
            
            if alt_result.returncode != 0:
                return None
        
        # Check if file was downloaded successfully
        if os.path.exists(output_file):
            print(f"Successfully downloaded: {output_file}")
            return output_file
        else:
            print("Download completed but could not locate the video file.")
            return None
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def check_yt_dlp_installed():
    """Check if yt-dlp is installed on the system"""
    return shutil.which('yt-dlp') is not None