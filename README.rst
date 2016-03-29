============
disentangler
============

Simple dependency tree builder, handles forward and reverse dependencies,
returning an ordered tree with it's nodes ordered from root towards leafs.

Example::

    >>> from collections import OrderedDict
    >>> from disentangler import Disentangler
    >>> inst = Disentangler.new()
    >>> inst.add('a', {})
    >>> inst.add('b', {'depends_on': ['d', 'c']})
    >>> inst.add('c', {})
    >>> inst.add('d', {'depends_on': ['a']})
    >>> ordered = inst.solve()
    >>> print(ordered)
    OrderedDict([('a', {}),
                 ('c', {}),
                 ('d', {'depends_on': ['a']}),
                 ('b', {'depends_on': ['d', 'c']})])

