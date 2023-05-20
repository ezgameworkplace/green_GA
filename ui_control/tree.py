'''
File:tree.py
Author:ezgameworkplace
Date:2022/12/4
'''
import xml.dom.minidom
import xml.etree.ElementTree

import lxml.etree as ET

ExactSearch = 1
FuzzySearch = 0
CaseSensitive = 1
CaseInsensitive = 0


class UITree(object):

    def __init__(self):
        self._xml_tree = None

    def __str__(self):
        if self._xml_tree != None:
            return self.get_pretty_tree()
        else:
            return None

    @property
    def xml_tree(self):
        return self._xml_tree

    @xml_tree.setter
    def xml_tree(self, tree):
        self._xml_tree = tree

    def get_pretty_tree(self) -> str:
        _xml = xml.dom.minidom.parseString(self._xml_tree)
        pretty_xml_as_string = _xml.toprettyxml()
        return pretty_xml_as_string

    def get_all_nodes(self) -> [ET._Element]:
        tree = ET.fromstring(self._xml_tree)
        ret = []
        for branches in tree.iter():
            ret.append([b for b in branches])
        ret = sum(ret, [])
        return ret

    def __parsed_tree(self, case=CaseSensitive):
        tree = self._xml_tree
        if case == CaseSensitive:
            parsed_tree = ET.fromstring(tree)
            return parsed_tree
        elif case == CaseInsensitive:
            parsed_tree = ET.fromstring(tree.lower())
            return parsed_tree

    def __parsed_search(self, search: str, case=CaseSensitive):
        if case == CaseSensitive:
            return search
        elif case == CaseInsensitive:
            return search.lower()

    def __get_nodes_by_attr_value(self, attr, search, mode=ExactSearch, case=CaseSensitive) -> [ET._Element]:
        tree = self.__parsed_tree(case)
        parsed_search = self.__parsed_search(search, case)
        ret = []
        for branches in tree.iter():
            if mode == ExactSearch:
                nodes = branches.findall(f"./*[@{attr}='{parsed_search}']")
            elif mode == FuzzySearch:
                nodes = branches.xpath(f"./*[contains(@{attr}, '{parsed_search}')]")
            else:
                raise Exception('must choose ExactSearch or FuzzySearch')
            if nodes != []:
                ret.append([_ for _ in nodes])
        ret = sum(ret, [])
        return ret

    def get_node_attr(self, node: [ET._Element]) -> dict:
        return node.attrib

    def get_nodes_by_attr_value(self, attr: str, search: str, mode=ExactSearch, case=CaseSensitive) -> [dict]:
        return [self.get_node_attr(node) for node in self.__get_nodes_by_attr_value(attr, search, mode, case)]
