# captioning.py
# Given path to annotations directory, generate captions for each event 
# Usage: python captioning.py <path to annotations directory>
# Structure of annotations directory: Note that the causal_info.json has the annotations that we will generate captions from.
# causal_segmentation/
#      general/
#         {Catapult, Gap, Launch, Slope, Table, Unbox}/
#               {Catapult, Gap, Launch, Slope, Table, Unbox}_{0,1,2,None}/
#                   videos/
#                       {video_name}.gif
#                   causal_info.json
#      simple/
#           Simple_{Collision, Slope, Unbox}/       
#                 {Catapult, Gap, Launch, Slope, Table, Unbox}_{0,1,2,None}/
#                     videos/
#                         {video_name}.gif
#                     causal_info.json
import sys
import tqdm
import os
import json

def generate_collision_caption(a, b):
    return f"A collision occurs between the {a} and the {b}."

def generate_start_touching_caption(a, b):
    return f"The {a} and the {b} start touching."

def generate_stop_touching_caption(a, b):
    return f"The {a} and the {b} stop touching."

def generate_goal_caption(a):
    return f"The {a} reaches the goal."


def main():
    # Get all the videos in the general directory
    general_dir = "causal_segmentation/general"
    categories = os.listdir(general_dir)
    for category in tqdm.tqdm(categories):
        category_dir = os.path.join(general_dir, category)
        instances = os.listdir(category_dir)
        for instance in tqdm.tqdm(instances):
            instance_dir = os.path.join(category_dir, instance)
            causal_info = os.path.join(instance_dir, "causal_info.json")
            captions_path = os.path.join(instance_dir, "captions.txt")
            # clear the captions file
            with open(captions_path, "w") as f:
                f.truncate(0)
            with open(causal_info, "r") as f:
                causal_info_dict = json.load(f)
            edges = causal_info_dict["edges"]
            for edge in edges:
                from_node = edge["from"].lower()
                to_node = edge["to"].lower()
                start_frame = edge["start_frame"]
                end_frame = edge["end_frame"]
                type = edge["type"]
                caption = ""

                if type == "collision":
                    caption = generate_collision_caption(from_node, to_node)
                elif type == "starttouching":
                    caption = generate_start_touching_caption(from_node, to_node)
                elif type == "endtouching":
                    caption = generate_stop_touching_caption(from_node, to_node)
                elif type == "goal":
                    caption = generate_goal_caption(from_node)

                with open(captions_path, "a") as f:
                    f.write(caption + "\n")

    # Perform the same captioning procedure as above for the simple directory
    simple_dir = "causal_segmentation/simple"
    categories = os.listdir(simple_dir)
    for category in tqdm.tqdm(categories):
        category_dir = os.path.join(simple_dir, category)
        instances = os.listdir(category_dir)
        for instance in tqdm.tqdm(instances):
            instance_dir = os.path.join(category_dir, instance)
            causal_info = os.path.join(instance_dir, "causal_info.json")
            captions_path = os.path.join(instance_dir, "captions.txt")
            # clear the captions file
            with open(captions_path, "w") as f:
                f.truncate(0)
            with open(causal_info, "r") as f:
                causal_info_dict = json.load(f)
            edges = causal_info_dict["edges"]
            for edge in edges:
                from_node = edge["from"].lower()
                to_node = edge["to"].lower()
                start_frame = edge["start_frame"]
                end_frame = edge["end_frame"]
                type = edge["type"] 
                caption = ""

                if type == "collision":
                    caption = generate_collision_caption(from_node, to_node)
                elif type == "starttouching":
                    caption = generate_start_touching_caption(from_node, to_node)
                elif type == "endtouching":
                    caption = generate_stop_touching_caption(from_node, to_node)
                elif type == "goal":
                    caption = generate_goal_caption(from_node)

                with open(captions_path, "a") as f:
                    f.write(caption + "\n")


if __name__ == "__main__":
    main()
