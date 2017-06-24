ASTFormatter
============

The ASTFormatter class accepts an AST tree and returns a valid source code representation of that tree.

Example Usage
-------------

::

    from astformatter import ASTFormatter
    import ast

    tree = ast.parse(open('modulefile.py'), 'modulefile.py', mode='exec')
    src  = ASTFormatter().format(tree, mode='exec')

Bugs
----

- Currently, indentation is fixed at 4 spaces.

- Too many methods are exposed that shouldn't be, in order to properly subclass `ast.NodeVisitor`.

- Need to make the statement visitor methods consistent about returning a list of strings; most still just return a string.

- Code modified to work with 3.x needs cleanup

Latest Changes
--------------

`0.6.3 <'https://pypi.python.org/pypi?:action=display&name=ASTFormatter&version=0.6.3'>`_ (2017-06-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Process docstring if exsts in Module, ClassDef, and FunctionDef
   nodes.
   `#9 <https://github.com/darkfoxprime/python-astformatter/pull/9>`_
   (`darkfoxprime <https://github.com/darkfoxprime>`_)
-  Add parens around unary operands if necessary
   `#8 <https://github.com/darkfoxprime/python-astformatter/pull/8>`_
   (`zerebubuth <https://github.com/zerebubuth>`_)

Copyright
---------

Copyright |copy| 2015-2016 by Johnson Earls.  Some rights reserved.  See the license_ for details.

.. _license: https://raw.githubusercontent.com/darkfoxprime/python-astformatter/master/LICENSE
.. |copy| unicode:: 0xA9 .. copyright sign
