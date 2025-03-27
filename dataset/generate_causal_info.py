
from abc import ABC, abstractmethod
from typing import Dict, Any

import pygame as pg
from pyGameWorld import PGWorld, ToolPicker
from pyGameWorld.viewer import drawPathSingleImageWithTools, drawWorldWithTools, drawSingleImageWithPlacement, drawPathSingleImageWithTools2, makeImageArray
from PIL import Image
import numpy as np
import copy

import json
import imageio
import pygame.surfarray
import networkx as nx

def simulate(tp) -> Dict[str, Any]:
    """Execute action and return raw outcome"""
    path_dict, collisions, success, _, world_dict = tp.runStatePath(
        noisy=False,
        returnDict=True
    )
    
    if path_dict is None:
        outcome = {"Paths": path_dict, "Collisions": collisions, "Success": success, "Image": None, "video": None}
    else:
        tp = copy.deepcopy(tp)
        tp.set_worlddict(world_dict)
        pg.display.set_mode((10,10))
        sc = drawPathSingleImageWithTools2(tp, path_dict)
        img = sc.convert_alpha()
        pg.image.save(img, f"path.png")
        img_array = makeImageArray(world_dict, path_dict)
        outcome = {"paths": path_dict, "collisions": collisions, "success": success, "image": img, "video": img_array}
        # TODO - should output video
    return outcome


import os

task_names = []
for filename in os.listdir("/nfs/turbo/coe-chaijy/jungchun/p-phy-strat/src/tasks"):
    if filename.endswith(".json"):
        task_names.append(filename[:-5])  # Remove .json extension

for task_name in task_names:

    with open(f"/nfs/turbo/coe-chaijy/jungchun/p-phy-strat/src/tasks/{task_name}.json", "r") as f:
        btr = json.load(f)

    tp = ToolPicker(btr)

    outcome = simulate(tp)
    os.makedirs(f"/nfs/turbo/coe-chaijy/jungchun/p-phy-strat/src/dataset/{task_name}", exist_ok=True)
    print(outcome["collisions"])
    print(outcome["success"])

    col_list = []
    # extract the data
    for collision in outcome["collisions"]:
        obj1, obj2, time1, time2 = collision[0:4]
        are_objects = (obj1 in tp.objects and obj2 in tp.objects)
        if not are_objects:
            continue
        are_not_static = (not tp.objects[obj1].isStatic() and not tp.objects[obj2].isStatic())
        if are_not_static or (tp.objects[obj1].name == "Goal" or  tp.objects[obj2].name == "Goal"):
            time1 = round(time1*10+1)
            if "Goal" in [tp.objects[obj1].name, tp.objects[obj2].name]:
                time2 = round(time2*10+1)
                col_list.append([obj1, obj2, time2, 'goal'])
                if obj1 == "Ball" or obj2 == "Ball":
                    break
            if time2 is None:
                col_list.append([obj1, obj2, time1, 'collision'])
            else:
                time2 = round(time2*10+1)
                if time2 - time1 <= 1:
                    col_list.append([obj1, obj2, time1, 'collision'])
                else:
                    col_list.append([obj1, obj2, time1, 'starttouching'])
                    col_list.append([obj1, obj2, time2, 'endtouching'])

    if col_list and col_list[-1][3] != "goal":
        col_list.append(['Ball', 'Goal', len(outcome["video"]), 'goal'])
    
    col_list.sort(key=lambda x: x[2])

    curr_timestamps = [0]
    colission_dict = {}
    filtered_col_list = []
    for col in col_list:
        if abs(colission_dict.get(col[0]+col[1], [0,0])[1] - col[2]) <= 5 and col[3] == "collision":
            continue
            
        if abs(curr_timestamps[-1] - col[2]) >= 5:
            prev_timestamp = curr_timestamps[-1]
            clip = outcome["video"][prev_timestamp:col[2]]
            colission_dict[col[0]+col[1]] = [prev_timestamp,col[2]]
            curr_timestamps.append(col[2])
        else:
            prev_timestamp = curr_timestamps[-2]
            clip = outcome["video"][prev_timestamp:col[2]]
            colission_dict[col[0]+col[1]] = [prev_timestamp,col[2]]
        filtered_col_list.append([col[0], col[1], prev_timestamp, col[2], col[3]])
        clip = [pygame.surfarray.array3d(frame).transpose(1, 0, 2) for frame in clip]
        
        os.makedirs(f"/nfs/turbo/coe-chaijy/jungchun/p-phy-strat/src/dataset/{task_name}/videos", exist_ok=True)
        imageio.mimsave(f"/nfs/turbo/coe-chaijy/jungchun/p-phy-strat/src/dataset/{task_name}/videos/clip_{col[2]}_{col[0]}{col[1]}_{col[3]}.gif", clip, fps=10)

    for col in filtered_col_list:
        print(col)
    print()

    curr_node = "Goal"
    graph = nx.DiGraph()
    for col in reversed(filtered_col_list):
        if col[0] == curr_node:
            graph.add_edge(col[1], col[0])
            graph.edges[col[1], col[0]]["start_frame"] = col[2]
            graph.edges[col[1], col[0]]["end_frame"] = col[3]
            graph.edges[col[1], col[0]]["type"] = col[4]
            curr_node = col[1]
        elif col[1] == curr_node:
            graph.add_edge(col[0], col[1])
            curr_node = col[0]
            graph.edges[col[0], col[1]]["start_frame"] = col[2]
            graph.edges[col[0], col[1]]["end_frame"] = col[3]
            graph.edges[col[0], col[1]]["type"] = col[4]

    start_nodes = [n for n, d in graph.in_degree() if d == 0]

    edge_info = {"edges": [], "collisions": []}
    for start_node in start_nodes:
        for path in nx.all_simple_paths(graph, start_node, "Goal"):
            for i in range(len(path)-1):
                edge_info["edges"].append(
                    {"from": path[i], 
                     "to": path[i+1], 
                     "start_frame": graph.edges[path[i], path[i+1]]["start_frame"], 
                     "end_frame": graph.edges[path[i], path[i+1]]["end_frame"], 
                     "type": graph.edges[path[i], path[i+1]]["type"]}
                )

    with open(f"/nfs/turbo/coe-chaijy/jungchun/p-phy-strat/src/dataset/{task_name}/causal_info.json", "w") as f:
        json.dump(edge_info, f, indent=4)

