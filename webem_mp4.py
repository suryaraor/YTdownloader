import os
import sys
from moviepy.editor import VideoFileClip
print(sys.path)
def convert_and_delete_webm_files():
    # Get all .webm files in the current folder
    webm_files = [f for f in os.listdir() if f.endswith('.webm')]
    
    if not webm_files:
        print("No .webm files found in the current directory.")
        return
    
    for webm_file in webm_files:
        mp4_file = webm_file.replace('.webm', '.mp4')  # Create the output file name
        try:
            print(f"Converting {webm_file} to {mp4_file}...")
            # Load the .webm file
            video = VideoFileClip(webm_file)
            
            # Convert to .mp4
            video.write_videofile(mp4_file, codec="libx264", audio_codec="aac")
            video.close()
            
            # If successful, delete the original .webm file
            os.remove(webm_file)
            print(f"Successfully converted and deleted {webm_file}")
        except Exception as e:
            print(f"An error occurred with {webm_file}: {e}")

# Run the function
if __name__ == "__main__":
    convert_and_delete_webm_files()
