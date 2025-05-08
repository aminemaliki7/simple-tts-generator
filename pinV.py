#!/usr/bin/env python3
import os
import argparse
import subprocess
import shutil
import re
import time
from urllib.parse import urlparse

def download_pinterest_video(url, output_path='pinterest videos', filename=None):
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
        
        print(f"Downloading video from: {url}")
        
        # Extract pin ID for filename
        pin_id = None
        if '/pin/' in url:
            pin_id_match = re.search(r'/pin/(\d+)', url)
            if pin_id_match:
                pin_id = pin_id_match.group(1)
        
        # Set output filename
        if filename:
            output_filename = f"{filename}.mp4"
        elif pin_id:
            output_filename = f"pinterest_{pin_id}.mp4"
        else:
            output_filename = f"pinterest_{int(time.time())}.mp4"
        
        output_file = os.path.join(output_path, output_filename)
        
        # Use yt-dlp to download the Pinterest video
        # Note: We're not specifying format selection to let yt-dlp choose the best option
        cmd = [
            'yt-dlp',
            # No format selection to let yt-dlp choose the best available formats
            '--merge-output-format', 'mp4',  # Ensure output is MP4
            '-o', output_file,               # Output filename
            '--no-warnings',                 # Suppress warnings
            '--verbose',                     # Get more details in case of failure
            url                              # Pinterest URL
        ]
        
        print("Running command:", ' '.join(cmd))
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error occurred during download:")
            print(result.stderr)
            
            # Try alternate approach if first attempt fails
            print("Trying alternate download method...")
            alt_cmd = [
                'yt-dlp',
                '-f', 'b',          # Use best pre-merged format
                '--merge-output-format', 'mp4',
                '-o', output_file,
                url
            ]
            
            alt_result = subprocess.run(alt_cmd, capture_output=True, text=True)
            
            if alt_result.returncode != 0:
                print(f"Error with alternate method:")
                print(alt_result.stderr)
                return None
        
        # Check if file was downloaded successfully
        if os.path.exists(output_file):
            print(f"Successfully downloaded: {output_file}")
            return output_file
        else:
            print("Download completed but could not locate the video file.")
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
    parser = argparse.ArgumentParser(description='Download videos from Pinterest URLs')
    parser.add_argument('url', help='Pinterest URL of the video')
    parser.add_argument('-o', '--output', default='pinterest videos', help='Output directory')
    parser.add_argument('-f', '--filename', help='Output filename (without extension)')
    
    args = parser.parse_args()
    
    # Check if yt-dlp is installed
    if shutil.which('yt-dlp') is None:
        print("Error: yt-dlp is not installed.")
        print("Please install it with: pip install yt-dlp")
        return
    
    download_pinterest_video(args.url, args.output, args.filename)

if __name__ == "__main__":
    main()