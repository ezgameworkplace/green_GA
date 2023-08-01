# -*- coding: utf-8 -*-
"""
File:utils.py
Author:ezgameworkplace
Date:2023/7/11
"""
import hashlib

from lxml import etree


def count_parent(element) -> int:
    return len(list(element.iterancestors()))


def get_bfs_position(element: etree.Element) -> int:
    # 获取父节点的根
    root = element.getroottree().getroot()
    # 广度优先遍历（BFS）位置
    bfs_position = -1
    for i, e in enumerate(root.iter()):
        if e == element:
            bfs_position = i
            break
    return bfs_position


def get_dfs_position(element: etree.Element) -> int:
    # 获取父节点的根
    root = element.getroottree().getroot()
    # 深度优先遍历（DFS）位置
    dfs_position = -1
    for i, e in enumerate(root.iterdescendants()):
        if e == element:
            dfs_position = i
            break
    return dfs_position


def get_element_hash(element: etree.Element):
    # 通过父亲节点制作哈希值
    weighted_attributes = []
    for parent in element.iterancestors():
        parent_attributes = parent.items()
        weighted_attributes.extend((k, v) for k, v in parent_attributes)

    parent_features = '|'.join([f'{k}={v}' for k, v in weighted_attributes if k != 'id'])

    features = [
        parent_features,
    ]
    feature_string = '|'.join([f for f in features if f is not None])  # 忽略 None 值
    return hashlib.sha256(feature_string.encode()).hexdigest()  # 用16进制保存特征


def distance(element, target_hashcode: str):
    element_hashcode = get_element_hash(element)
    print(element_hashcode)
    # 将哈希码从十六进制转换为二进制
    element_hashcode_binary = bin(int(element_hashcode, 16))[2:].zfill(256)
    target_hashcode_binary = bin(int(target_hashcode, 16))[2:].zfill(256)

    # 计算两个二进制哈希码之间的汉明距离
    return sum(x != y for x, y in zip(element_hashcode_binary, target_hashcode_binary))
