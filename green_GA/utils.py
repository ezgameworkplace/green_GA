# -*- coding: utf-8 -*-
"""
File:utils.py
Author:ezgameworkplace
Date:2023/7/11
"""
import hashlib
from typing import List

from lxml import etree

USEFUL_ATTR = ['name', 'txt', 'img']


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


def filter_attr(element: etree.Element, useful_attr: List) -> List[str]:
    return [v for k, v in element.items() if k in useful_attr]


def _get_parent_by_level(element: etree.Element, level: int) -> List[etree.Element] or None:
    ancestors = list(element.iterancestors())
    if len(ancestors) >= level:
        return ancestors[:level]
    return None  # 如果没有足够的祖先，返回None


def get_great_grandparent(element: etree.Element) -> List[etree.Element] or None:
    return _get_parent_by_level(element, 4)


def get_following_siblings(element: etree.Element) -> List[etree.Element] or None:
    return list(element.itersiblings(preceding=False))


def get_preceding_siblings(element: etree.Element) -> List[etree.Element] or None:
    return list(element.itersiblings(preceding=True))


def get_parent_features(element: etree.Element, attr_filter: List = None) -> str:
    if attr_filter is None:
        attr_filter = USEFUL_ATTR
    string_attributes = []
    great_grandparents = get_great_grandparent(element)
    if great_grandparents:
        for parent in great_grandparents:
            string_attributes.extend(filter_attr(parent, attr_filter))

            # 考虑前兄弟
            for sibling in parent.itersiblings(preceding=True):
                string_attributes.extend(filter_attr(sibling, attr_filter))

            # 考虑后兄弟
            for sibling in parent.itersiblings(preceding=False):
                string_attributes.extend(filter_attr(sibling, attr_filter))
    return ''.join(string_attributes)


def get_sibling_features(element: etree.Element, attr_filter: List = None) -> str:
    if attr_filter is None:
        attr_filter = USEFUL_ATTR
    string_attributes = []
    following_siblings = get_following_siblings(element)
    preceding_siblings = get_preceding_siblings(element)
    # 考虑前兄弟
    for sibling in following_siblings:
        string_attributes.extend(filter_attr(sibling, attr_filter))
    # 考虑后兄弟
    for sibling in preceding_siblings:
        string_attributes.extend(filter_attr(sibling, attr_filter))
    return ''.join(string_attributes)


def normalize_feature_string(feature_string: str) -> str:
    return ''.join(sorted(feature_string))


def get_element_hash(element: etree.Element, attr_filter: List = None):
    if attr_filter is None:
        attr_filter = USEFUL_ATTR
    parent_features = normalize_feature_string(get_parent_features(element, attr_filter))
    sibling_features = normalize_feature_string(get_sibling_features(element, attr_filter))
    features = [
        parent_features,
        sibling_features,
        element.tag,
        element.get('name'),
        # element.get('components'), 有时组件会被关闭，不建议将组件加入哈希特征
        element.get('img'),
        element.get('txt'),
        # 添加更多特性
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
