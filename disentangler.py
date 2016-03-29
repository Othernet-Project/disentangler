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
        """Add a new dependency to the mess.

        :param node_id: unique identifier of a dependency
                        (may be used by other dependencies to reference it)
        :param node:    dict, optionally containing forward and / or reverse
                        dependencies
        """
        if node_id in self._tree:
            raise self.DependencyAlreadyExists()

        self._tree[node_id] = node

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

    def _collect_dependencies(self, node_id, collected=None):
        """Recursively assemble the list of dependencies for the specified
        node, including the node itself at the end.

        :param node_id:   unique identifier of node which dependency list is
                          being assembled
        :param collected: param used only in recursive calls to collect all
                          dependencies of ``node_id`` down to the root

        For a sample tree:

        A -> [B, E]
        B -> [D]
        C -> []
        D -> [E]
        E -> []

        Finding the dependencies of A would return:

        [E, D, B, A]
        """
        if collected is None:
            # to protect against circular dependencies towards the target node
            # itself too, it must be added to the list initially
            collected = collections.deque([node_id])
        # collect dependencies of the node recursively
        try:
            node = self._tree[node_id]
        except KeyError:
            raise self.UnresolvableDependency(node_id)
        else:
            for dep_id in node.get(self.FORWARD_KEY, []):
                if dep_id in collected:
                    # one of the ancestor nodes already specified this node as
                    # a dependency, and it turned out that this node has a
                    # reference towards the ancestor node as well, which is a
                    # circular dependency
                    raise self.CircularDependency(node_id, dep_id)
                # dependencies are prepended to the list, such that when
                # iterating over the result, dependencies are ordered from
                # lowest to highest, towards the target node
                collected.appendleft(dep_id)
                # collect child dependencies, prepending children the same way
                self._collect_dependencies(dep_id, collected=collected)
            return collected

    def _order_nodes(self):
        """Build a new dependency tree ordered according to the forward
        dependency specifications and replace the unordered tree with it."""
        ordered_tree = collections.OrderedDict()
        for node_id in self._tree:
            # ``node_id`` will be included in the result set returned by
            # ``_collect_dependencies``
            for dep_id in self._collect_dependencies(node_id):
                if dep_id not in ordered_tree:
                    ordered_tree[dep_id] = self._tree[dep_id]
        self._tree = ordered_tree

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
