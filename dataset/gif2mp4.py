DATASET = r"C:\Users\emlin\Desktop\CSE-692\dataset\causal_segmentation_with_caption_v2-20250403T191340Z-001"

import os
from moviepy.editor import *

def convert_gif_to_mp4(gif_path, output_path):
    clip = VideoFileClip(gif_path)
    clip.write_videofile(output_path, codec="libx264")

def main():
    # example path to videos directory in /general subdirectory: C:\Users\emlin\Desktop\CSE-692\dataset\causal_segmentation_with_caption_v2-20250403T191340Z-001\causal_segmentation_with_caption_v2\general\Catapult\Catapult_failure_0\videos
    # example path to videos directory in /simple subdirectory:C:\Users\emlin\Desktop\CSE-692\dataset\causal_segmentation_with_caption_v2-20250403T191340Z-001\causal_segmentation_with_caption_v2\simple

    # convert all gif files in the videos directory to mp4 files
    for root, dirs, files in os.walk(DATASET):
        for file in files:
            if file.endswith(".gif"):
                gif_path = os.path.join(root, file)
                convert_gif_to_mp4(gif_path, os.path.join(root, file.replace(".gif", ".mp4")))

if __name__ == "__main__":
    main()
