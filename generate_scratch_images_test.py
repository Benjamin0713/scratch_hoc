# -*- coding: utf-8 -*- 
# @Time : 2021/6/5 19:33
# @Author : hangzhouwh 
# @Email: hangzhouwh@gmail.com
# @File : generate_scratch_images_test.py
# @Software: PyCharm


import json
import pandas as pd
import numpy as np
import networkx as nx
import os
from tqdm import tqdm
from PIL import Image
from PIL import ImageDraw
import colorsys
import random
import glob


def load_json(filepath):
    file = open(filepath, 'rb')
    data = json.load(file)
    return data


def write_json(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f)


def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step

    return hls_colors


def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [int(x * 255.0) for x in (_r, _g, _b)]
        rgb_colors.append([r, g, b])

    return rgb_colors


def color(value):
    digit = list(map(str, range(10))) + list("ABCDEF")
    if isinstance(value, tuple):
        string = '#'
        for i in value:
            a1 = i // 16
            a2 = i % 16
            string += digit[a1] + digit[a2]
        return string
    elif isinstance(value, str):
        a1 = digit.index(value[1]) * 16 + digit.index(value[2])
        a2 = digit.index(value[3]) * 16 + digit.index(value[4])
        a3 = digit.index(value[5]) * 16 + digit.index(value[6])
        return (a1, a2, a3)


def buildGraph(filepath):
    # project 第一层
    sb3 = load_json(filepath)
    targets = sb3['targets']
    G = nx.Graph(name="graph")  # 创建无向图
    id = 0
    id2blockid = dict()
    blockid2id = dict()

    # 为所有Stage, role, block 构建映射
    for target in targets:
        isStage = target['isStage']
        if isStage is True:
            name = target['name']
            if name not in blockid2id.keys():
                id2blockid[id] = name
                blockid2id[name] = id
                id += 1

            # Stage也有block
            blocks = target['blocks']
            for block_id in blocks:
                block = blocks[block_id]
                if block_id not in blockid2id.keys() and isinstance(block, dict):
                    id2blockid[id] = block_id
                    blockid2id[block_id] = id
                    id += 1
        else:
            name = target['name']
            if name not in blockid2id.keys():
                id2blockid[id] = name
                blockid2id[name] = id
                id += 1

            # Role's blocks
            blocks = target['blocks']
            for block_id in blocks:
                block = blocks[block_id]
                if block_id not in blockid2id.keys() and isinstance(block, dict):
                    id2blockid[id] = block_id
                    blockid2id[block_id] = id
                    id += 1

    # 遍历过程中父亲节点还没有计算到的节点

    # 构建Graph
    for target in targets:
        isStage = target['isStage']
        if isStage is True:
            name = target['name']
            stage_id = blockid2id[name]
            G.add_node(stage_id, feature=checkFeature["stage"], opcode="stage")

            blocks = target['blocks']
            for block_id in blocks:
                block = blocks[block_id]
                if isinstance(block, dict):
                    id = blockid2id[block_id]
                    opcode = block['opcode']
                    parent = block['parent']
                    isToplevel = block['topLevel']
                    if isToplevel is True:
                        G.add_node(id, feature=checkFeature[opcode], opcode=opcode)
                        G.add_edge(stage_id, id)
                    else:
                        if parent is None:
                            G.add_node(id, feature=checkFeature[opcode], opcode=opcode)
                            G.add_edge(stage_id, id)
                        else:
                            parent_id = blockid2id[parent]
                            G.add_node(id, feature=checkFeature[opcode], opcode=opcode)
                            G.add_edge(parent_id, id)
        else:
            name = target['name']
            role_id = blockid2id[name]
            G.add_node(role_id, id=role_id, feature=checkFeature["role"], opcode="role")  # 將角色加入Graph
            G.add_edge(stage_id, role_id)

            blocks = target['blocks']
            for block_id in blocks:
                block = blocks[block_id]
                if isinstance(block, dict):
                    id = blockid2id[block_id]
                    opcode = block['opcode']
                    parent = block['parent']
                    isToplevel = block['topLevel']
                    if isToplevel is True:
                        G.add_node(id, feature=checkFeature[opcode], opcode=opcode)
                        G.add_edge(role_id, id)
                    else:
                        if parent is None:
                            G.add_node(id, feature=checkFeature[opcode], opcode=opcode)
                            G.add_edge(role_id, id)
                        else:
                            parent_id = blockid2id[parent]
                            G.add_node(id, feature=checkFeature[opcode], opcode=opcode)
                            G.add_edge(parent_id, id)

    G.nodes[0]['depth'] = 0
    depth_dic = {}
    depth_dic[0] = 0
    bfs_path = list(nx.bfs_edges(G, source=0))
    for e in bfs_path:
        node1 = e[0]
        node2 = e[1]
        node1_depth = depth_dic[node1]
        node2_depth = node1_depth + 1
        depth_dic[node2] = node2_depth
        G.nodes[node2]['depth'] = node2_depth
    return G


# 每种代码块对应的编号
checkFeature = {}

# 统计所有的代码块类型
dirpath = "D:/PYc/Re/scode/*.json"
filelist = glob.glob(dirpath)

opcode_set = set()
for i in tqdm(range(len(filelist))):
    filepath = filelist[i]
    scode = load_json(filepath)
    targets = scode['targets']
    for e in targets:
        name = e['name']
        blocks = e['blocks']
        for k, v in blocks.items():
            try:
                opcode = v['opcode']
                opcode_set.add(opcode)
            except:
                pass

opcode_set = list(opcode_set)
opcode_set.append("stage")
opcode_set.append("role")
i = 0
for op in opcode_set:
    checkFeature[op] = i
    i += 1

fileList = os.listdir("D:/PYc/Re/scode/")
fileId = []
for filename in fileList:
    filePre = filename.split('.')[0]
    if filePre.isdigit():
        fileId.append(int(filePre))
fileId.sort()

colors = list(map(lambda x: color(tuple(x)), ncolors(len(opcode_set))))
print(len(opcode_set))
print(len(colors))

# TODO 建图，把所有建好的AST加入graphs列表

graphs = []
for i in tqdm(fileId):
    G = buildGraph("D:/PYc/Re/scode/" + str(i) + ".json")  # 这是其中一个标准答案
    graphs.append(G)


# TODO 读取标签
labelpath = 'D:/PYc/Re/test_text.txt'
labels = []

with open(labelpath, 'r') as file:
    for line in file:
        labels.append(int(line.split()[0]))

index = 0
for graph in tqdm(graphs):
    DG = graph
    root = list(DG.nodes())[0]
    dfs_seqs = list(nx.dfs_tree(DG, root))

    array = np.ndarray((250, 250, 3), np.uint8)
    array[:, :, 0] = 255
    array[:, :, 1] = 255
    array[:, :, 2] = 255
    image = Image.fromarray(array)
    draw = ImageDraw.Draw(image)

    num = 0
    for node in dfs_seqs:
        draw.rectangle((DG.nodes()[node]['depth']*10, num*10, DG.nodes()[node]['depth']*10 + 70, num*10 + 10),
                       colors[checkFeature[DG.nodes()[node]['opcode']]], 'black')
        num += 1

    image.save('D:/PYc/Test-images2/' + str(index) + '_' + str(labels[index]) + '.jpg')
    index += 1