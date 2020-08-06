import collections


class GraphNode(object):

    def __init__(self, layer):
        self.in_edges = list()
        self.out_edges = list()
        self.layer = layer
        self.covered = False
        self.real_name = self.name

    @property
    def name(self):
        assert False

    @property
    def variable_name(self):
        return self.real_name.replace('/', '_').replace('-', '_').replace('[', '_').replace(']', '_')

    @property
    def real_variable_name(self):
        return self.real_name.replace('/', '_').replace('-', '_').replace('[', '_').replace(']', '_')


class Graph(object):

    def __init__(self, model):
        # key: layer_name    value: keras layer
        self.layer_map = collections.OrderedDict()
        self.input_layers = list()
        self.output_layers = list()
        self.layer_name_map = collections.OrderedDict()
        self.topological_sort = list()
        self.model = model

    def build(self):
        self._make_input_layers()
        self._make_output_layers()
        self._get_topological_sort()

    def _make_input_layers(self):
        for name, layer in self.layer_map.items():
            layer.left_in_edges = len(layer.in_edges)
            if len(layer.in_edges) == 0:
                self.input_layers.append(name)

    def _make_output_layers(self):
        for name, layer in self.layer_map.items():
            if len(layer.out_edges) == 0:
                self.output_layers.append(name)

    def get_node(self, name):
        if name not in self.layer_map:
            raise IOError("Graph doesn't have node [%s]." % name)
            return None
        else:
            return self.layer_map[name]

    def get_son(self, name, path, set_flag=False):
        if name is None:
            return None
        current_node = self.get_node(name)
        for idx in path:
            if len(current_node.out_edges) <= idx:
                return None
            son_name = current_node.out_edges[idx]
            current_node = self.get_node(son_name)
            if set_flag:
                current_node.covered = True
        return current_node

    def get_parent(self, name, path, set_flag=False):
        if name is None:
            return None
        current_node = self.get_node(name)
        for idx in path:
            if len(current_node.in_edges) <= idx:
                return None
            parent_name = current_node.in_edges[idx]
            current_node = self.get_node(parent_name)
            if set_flag:
                current_node.covered = True
        return current_node

    def get_real_parent_name(self, name, path, set_flag=False):
        if name is None:
            return None
        current_node = self.get_node(name)
        for idx in path:
            if len(current_node.in_edges) <= idx:
                return None
            parent_name = current_node.in_edges[idx]
            current_node = self.get_node(parent_name)
            if set_flag:
                current_node.covered = True
        return self.layer_name_map[current_node.name]

    # private functions
    def _get_topological_sort(self):
        self.topological_sort = self.input_layers[:]
        idx = 0
        while idx < len(self.topological_sort):
            current_node = self.get_node(self.topological_sort[idx])
            for next_node in current_node.out_edges:
                next_node_info = self.get_node(next_node)
                next_node_info.left_in_edges -= 1
                if next_node_info.left_in_edges == 0:
                    self.topological_sort.append(next_node)
            idx += 1

    def _make_connection(self, src, dst):
        if (src == dst) or (src not in self.layer_map) or (dst not in self.layer_map):
            if src.split(':')[0] in self.layer_map:
                src = src.split(':')[0]
            else:
                print("Warning: Graph Construct a self-loop node {}. Ignored.".format(src))
                return

        if dst not in self.layer_map[src].out_edges:
            self.layer_map[src].out_edges.append(dst)
        if src not in self.layer_map[dst].in_edges:
            self.layer_map[dst].in_edges.append(src)
