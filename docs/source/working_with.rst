Working with disentangler
=========================

This section gives you a quick overview of disentangler library usage.

Creating a new dependency tree
------------------------------

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
