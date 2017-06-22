Feature: Generate proper Python code
    In order to be able to transform and recreate Python modules,
    as a software developer,
    I want the ASTFormatter class to be able to generate proper
    Python code for any given AST tree.

    Scenario Outline: AST structures common to all versions of python should work
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | def foo(x): pass                                      | def foo(x):\n    pass                                     |
        | class foo(object): pass                               | class foo(object):\n    pass                              |
        | return x                                              | return x                                                  |
        | del foo[0]                                            | del foo[0]                                                |
        | foo = x                                               | foo = x                                                   |
        | foo += y                                              | foo += y                                                  |
        | for target in (1,2,3):\n  pass\nelse:\n  pass         | for target in (1, 2, 3):\n    pass\nelse:\n    pass       |
        | while foo:\n  pass\nelse:\n  pass                     | while foo:\n    pass\nelse:\n    pass                     |
        | if foo:\n  pass\nelif foo:\n  pass\nelse:\n  pass     | if foo:\n    pass\nelif foo:\n    pass\nelse:\n    pass   |
        | with foo as x:\n  pass                                | with foo as x:\n    pass                                  |
        | raise foo(x)                                          | raise foo(x)                                              |
        | try:\n  pass\nfinally:\n  pass                        | try:\n    pass\nfinally:\n    pass                        |
        | assert foo,x                                          | assert foo,x                                              |
        | import foo,bar as x                                   | import foo\nimport bar as x                               |
        | from foo import bar as x                              | from foo import bar as x                                  |
        | from foo import *                                     | from foo import *                                         |
        | from .foo import x                                    | from .foo import x                                        |
        | global foo, x                                         | global foo,x                                              |
        | foo                                                   | foo                                                       |
        | pass                                                  | pass                                                      |
        | break                                                 | break                                                     |
        | continue                                              | continue                                                  |
        | x and y                                               | x and y                                                   |
        | x or y                                                | x or y                                                    |
        | x or y or z                                           | x or y or z                                               |
        | x + y                                                 | x + y                                                     |
        | x - y                                                 | x - y                                                     |
        | x * y                                                 | x * y                                                     |
        | x / y                                                 | x / y                                                     |
        | x % y                                                 | x % y                                                     |
        | x ** y                                                | x ** y                                                    |
        | x << y                                                | x << y                                                    |
        | x >> y                                                | x >> y                                                    |
#       | x | y                                                 | x | y                                                     |
        | x & y                                                 | x & y                                                     |
        | x // y                                                | x // y                                                    |
        | +x                                                    | + x                                                       |
        | -x                                                    | - x                                                       |
        | ~x                                                    | ~ x                                                       |
        | lambda foo: x                                         | lambda foo: x                                             |
        | foo if x else y                                       | foo if x else y                                           |
        | { foo: x, bar: y }                                    | {foo:x, bar:y}                                            |
        | [ foo for foo in x if y ]                             | [foo for foo in x if y]                                   |
        | ( foo for foo in x if y )                             | (foo for foo in x if y)                                   |
        | yield foo                                             | yield foo                                                 |
        | foo < x                                               | foo < x                                                   |
        | foo < x < y                                           | foo < x < y                                               |
        | y > x                                                 | y > x                                                     |
        | x == y                                                | x == y                                                    |
        | x != y                                                | x != y                                                    |
        | x <= y                                                | x <= y                                                    |
        | x >= y                                                | x >= y                                                    |
        | x is y                                                | x is y                                                    |
        | x is not y                                            | x is not y                                                |
        | x in y                                                | x in y                                                    |
        | x not in y                                            | x not in y                                                |
        | 123                                                   | 123                                                       |
        | foo = "foo"                                           | foo = 'foo'                                               |
        | foo = 'foo'                                           | foo = 'foo'                                               |
        | foo = """foo\nbar"""                                  | foo = 'foo\\nbar'                                         |
        | "foo"                                                 | """foo"""                                                 |
        | 'bar"""baz'                                           | """bar\\"\\"\\"baz"""                                     |
        | """quux\nfoobar"""                                    | """quux\nfoobar\n"""                                      |
        | foo.x                                                 | foo.x                                                     |
        | foo[x]                                                | foo[x]                                                    |
        | foo[x:y:z]                                            | foo[x:y:z]                                                |
        | [x,y,z]                                               | [x, y, z]                                                 |
        | (x,y,z)                                               | (x, y, z)                                                 |
        | None                                                  | None                                                      |
        | True                                                  | True                                                      |
        | False                                                 | False                                                     |

    @v2.6 @v2.7 @v3.3 @v3.4
    Scenario Outline: AST structures in pre-3.5 python should work
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | foo(x, y=1, *z, **q)                                  | foo(x, y=1, *z, **q)                                      |

    @v2.6 @v2.7
    Scenario Outline: AST structures in 2.6+ should work.
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | print >> foo, x,                                      | print >> foo, x,                                          |
        | raise foo,x                                           | raise foo,x                                               |
        | try:\n  pass\nexcept foo,x:\n  pass\nelse:\n  pass    | try:\n    pass\nexcept foo,x:\n    pass\nelse:\n    pass  |
        | exec "foo" in x,y                                     | exec 'foo' in x, y                                        |
        | x <> y                                                | x != y                                                    |
        | `foo`                                                 | `foo`                                                     |

    @v2.7 @v3.3 @v3.4 @v3.5
    Scenario Outline: AST structures in 2.7+ and 3.3+ should work.
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | {"first", 2, 'third', 4}                              | {'first', 2, 'third', 4}                                  |
        | {x for x in foo}                                      | {x for x in foo}                                          |
        | {k:v for (k,v) in foo}                                | {k:v for (k, v) in foo}                                   |

    @v2.7
    Scenario Outline: AST structures in 2.7+ should work.
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | with foo as x,bar as y:\n  pass                       | with foo as x, bar as y:\n    pass                        |

    @v3.3 @v3.4 @v3.5
    Scenario Outline: AST structures in 3.3+ should work.
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | try:\n  pass\nexcept foo as x:\n  pass\nelse:\n  pass | try:\n    pass\nexcept foo as x:\n    pass\nelse:\n    pass |
        | exec("foo",x,y)                                       | exec('foo', x, y)                                         |
        | b"foo"                                                | b'foo'                                                    |
        | *foo = bar                                            | *foo = bar                                                |
        | class foo(bar=baz): pass                              | class foo(bar=baz):\n    pass                             |
        | nonlocal foo,bar                                      | nonlocal foo,bar                                          |

    @v3.5
    Scenario Outline: AST structures in 3.5+ python should work
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | foo(x, y=1, *z, **q)                                  | foo(x, *z, y=1, **q)                                      |

    Scenario Outline: Operator precedence should be taken into account
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | x + y * z                                             | x + y * z                                                 |
        | (x + y) * z                                           | (x + y) * z                                               |
        | x + (y * z)                                           | x + y * z                                                 |
        | not (x and y)                                         | not (x and y)                                             |
        | not x and y                                           | not x and y                                               |
        | not x.y                                               | not x.y                                                   |
