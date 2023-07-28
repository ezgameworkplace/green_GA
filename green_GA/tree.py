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

    def get_sibling_node_by_search_name_and_txt(self, search_name: str, search_ui_txt: str, sibling_name: str,
                                                case=CaseSensitive) -> [dict]:
        # get nodes by 'name' attribute
        search_nodes = self.__get_nodes_by_attr_value('name', search_name, ExactSearch, case)

        # filter nodes by 'txt' attribute
        search_nodes = [node for node in search_nodes if node.attrib.get('txt') == search_ui_txt]

        # raise error if no search node found
        if not search_nodes:
            raise Exception(f"No node found with name '{search_name}' and text '{search_ui_txt}'")

        # assume the first node as the search node
        search_node = search_nodes[0]

        # find the sibling node
        parent = search_node.getparent()
        for child in parent:
            if 'name' in child.attrib and child.attrib['name'] == sibling_name:
                return self.get_node_attr(child)

        raise Exception(f"No sibling node found with name '{sibling_name}'")

    def get_sibling_child_by_search_name_and_txt(self, search_name: str, search_ui_txt: str, sibling_child_name: str,
                                                 case=CaseSensitive) -> [dict]:
        # get nodes by 'name' attribute
        search_nodes = self.__get_nodes_by_attr_value('name', search_name, ExactSearch, case)

        # filter nodes by 'txt' attribute
        search_nodes = [node for node in search_nodes if node.attrib.get('txt') == search_ui_txt]

        # raise error if no search node found
        if not search_nodes:
            raise Exception(f"No node found with name '{search_name}' and text '{search_ui_txt}'")

        # assume the first node as the search node
        search_node = search_nodes[0]

        # find the sibling node's child
        sibling_child = None
        parent = search_node.getparent()
        for child in parent:
            grandchilds = child.getchildren()
            for grandchild in grandchilds:
                if 'name' in grandchild.attrib and grandchild.attrib['name'] == sibling_child_name:
                    return self.get_node_attr(grandchild)

        raise Exception(f"No sibling child node found with name '{sibling_child_name}'")

    def get_closest_node(self, search_node_name: str, search_ui_txt: str, another_node_name: str,
                         case=CaseSensitive) -> [dict]:
        # get nodes by 'name' attribute
        search_nodes = self.__get_nodes_by_attr_value('name', search_node_name, ExactSearch, case)

        # filter nodes by 'txt' attribute
        search_nodes = [node for node in search_nodes if node.attrib.get('txt') == search_ui_txt]

        # raise error if no search node found
        if not search_nodes:
            raise Exception(f"No node found with name '{search_node_name}' and text '{search_ui_txt}'")

        # assume the first node as the search node
        search_node = search_nodes[0]

        # check children of the search node first
        closest_node = self._dfs(search_node, another_node_name)
        if closest_node is not None:
            return self.get_node_attr(closest_node)

        # find the closest node with another_node_name
        closest_node = self._bfs_dfs(search_node, another_node_name)

        if closest_node is None:
            raise Exception(f"No closest node found with name '{another_node_name}'")
        else:
            return self.get_node_attr(closest_node)

    def _bfs_dfs(self, node, another_node_name):
        queue = [node]
        while queue:
            current_node = queue.pop(0)
            if 'name' in current_node.attrib and current_node.attrib['name'] == another_node_name:
                return current_node
            closest_node = self._dfs(current_node, another_node_name)
            if closest_node is not None:
                return closest_node
            if current_node.getparent() is not None:
                queue.append(current_node.getparent())
        return None

    def _dfs(self, node, another_node_name):
        for child in node:
            if 'name' in child.attrib and child.attrib['name'] == another_node_name:
                return child
            closest_node = self._dfs(child, another_node_name)
            if closest_node is not None:
                return closest_node
        return None
