import collections


class Disentangler(object):
    FORWARD_KEY = 'depends_on'
    REVERSE_KEY = 'required_by'

    class Error(Exception):
        pass

    class DependencyAlreadyExists(Error):
        pass

    class UnresolvableDependency(Error):
        pass

    class CircularDependency(Error):
        pass

    def __init__(self, tree):
        self._tree = tree

    def add(self, node_id, node):
        """Add a new node to the not yet ordered tree.

        :param node_id: unique identifier of a dependency
                        (may be used by other dependencies to reference it)
        :param node:    dict, optionally containing forward and / or reverse
                        dependencies
        """
        if node_id in self._tree:
            raise self.DependencyAlreadyExists()

        self._tree[node_id] = node

    def pop(self, node_id):
        """
        Remove a node from the tree.
        """
        self._tree.pop(node_id)

    def _invert_reverse_dependencies(self):
        """Turns reverse dependencies into forward dependencies over the whole
        tree."""
        for (node_id, node) in self._tree.items():
            for dependent_id in node.pop(self.REVERSE_KEY, []):
                try:
                    dependent = self._tree[dependent_id]
                except KeyError:
                    raise self.UnresolvableDependency(dependent_id)
                else:
                    dependent_deps = dependent.get(self.FORWARD_KEY, [])
                    deps = dependent_deps + [node_id]
                    self._tree[dependent_id][self.FORWARD_KEY] = deps

    def _get_ordered_nodes(self, met=None, unmet=None):
        """ Return nodes IDs oredered to satisfy dependencies """
        if not self._tree:
            return []
        if unmet is None:
            # This is our first run, so initialize the unmet dependecies to
            # complete list of all nodes in the tree.
            unmet = list(self._tree.keys())
        if not unmet:
            # There are no more unmet dependencies, so we are free to return
            return met

        met = met or []
        still_unmet = []  # Deps that will still have unmet deps after the run
        requested = []    # Depds which will be requested but not met

        for node_id in unmet:
            deps = self._tree[node_id].get(self.FORWARD_KEY, [])
            # Filter out deps that are already met
            deps = [d for d in deps if d not in met]
            if not deps:
                # This node either has no dependencies or all of its
                # dpeendencies were met, so we can add it to the list of nodes
                # with met dependencies.
                met.append(node_id)
                continue
            if any(d not in unmet for d in deps):
                # This node still has at least unmet dependency, but that
                # dependecy is not even in the list of remaining nodes. This
                # means we can never resolve this node's dependencies.
                raise self.UnresolvableDependency(node_id)
            # Dependencies are not met yet, so we are adding the node to the
            # remaining nodes bucket.
            still_unmet.append(node_id)
            # Let's record the dependencies we have asked for
            requested.extend([d for d in deps if d not in met])

        if requested and set(requested) == set(still_unmet):
            # If the unique node IDs that we asked for matches the unique node
            # IDs that still have unmet dependencies, we are probably looking
            # at circular dependency issue.
            raise self.CircularDependency(requested)
        return self._get_ordered_nodes(met, still_unmet)

    def _order_nodes(self):
        """ Order the nodes according to forward dependency relationships, and
        update the tree """
        new_tree = collections.OrderedDict()
        for node_id in self._get_ordered_nodes():
            new_tree[node_id] = self._tree[node_id]
        self._tree = new_tree

    def solve(self):
        """Disentangle the graph by ordering nodes according to the specified
        dependency tree."""
        self._invert_reverse_dependencies()
        self._order_nodes()
        return self._tree

    @classmethod
    def new(cls, forward_key=None, reverse_key=None):
        """Create an empty dependency graph.

        :param forward_key: set the key used in the dependency specification
                            which points to forward dependencies
        :param reverse_key: set the key used in the dependency specification
                            which points to reverse dependencies
        """
        instance = cls(collections.OrderedDict())
        if forward_key:
            instance.FORWARD_KEY = forward_key
        if reverse_key:
            instance.REVERSE_KEY = reverse_key
        return instance
