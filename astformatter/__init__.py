import ast
import re

__all__ = ('ASTFormatter',)

import sys
# for sys.version

########################################################################
# The ASTFormatter class walks an AST and produces properly formatted
# python code for that AST.

class ASTFormatter(ast.NodeVisitor):
    '''
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
    
    `0.6.4 <'https://pypi.python.org/pypi?:action=display&name=ASTFormatter&version=0.6.4'>`_ (2017-06-25)
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
    '''

    __version__ = '0.6.4'

    def __init__(self):
        """Return a new ASTFormatter object."""
        # initialize the context to empty; every call to format()
        # will introduce a new context for that call, and every
        # node visited will have that node pushed to the top of the
        # stack and popped after the visitor returns.
        self.context = []

    def format(self, AST, mode='exec'):
        """Accept an AST tree and return a properly formatted Python
        expression or code block that compiles into that AST tree.
        If mode is 'exec', treat the tree as if it were rooted at a
        module; otherwise, for 'eval', treat it as if it were rooted
        at an expr node.
        """
        if not isinstance(AST, ast.AST):
            raise TypeError("ASTFormatter.format() expected AST got " + type(AST).__name__)
        if mode == 'exec':
            self.context.insert(0, ast.Module)
        elif mode == 'eval':
            self.context.insert(0, ast.expr)
        else:
            raise ValueError("ASTFormatter.format() expected either 'eval' or 'exec' for mode, got " + repr(mode))
        formatted = "".join(self.visit(AST))
        self.context.pop(0)
        return formatted

    ####################################################################
    # helper methods

    def visit(self, node):
        """Return the representation of the python source for `node`.
        If `node` is an expression node, return a single string;
        otherwise, return either a single newline-terminated string
        or a list of newline-terminated strings.

        FIXME: Only return lists of strings from non-expression nodes.
        """
        self.context.insert(0, node.__class__)
        retval = super(ASTFormatter, self).visit(node)
        self.context.pop(0)
        return retval

    def __process_body(self, stmtlist, indent=""):
        """Process a body block consisting of a list of statements
        by visiting all the statements in the list, prepending an
        optional indent to each statement, and returning the indented
        block.
        """
        self.indent = len(indent)
        content = []
        for stmt in stmtlist:
            stmts = self.visit(stmt)
            if not isinstance(stmts, list):
                stmts = [stmts]
            content += ["%s%s" % (indent, stmt) for stmt in stmts]
        return content

    def generic_visit(self, node):
        assert False, "ASTFormatter found an unknown node type " + type(node).__name__

    ####################################################################
    # precedence of expression operators/nodes.
    # each precedence is an integer, with higher values for
    # higher precedence operators.

    # the __precedence_list is a list of tuples of node types, in order
    # lowest priority to highest.  It is used to build the _precedence map.
    __precedence_list = (
        (ast.Lambda,),
        (ast.IfExp,),
        (ast.Or,),
        (ast.And,),
        (ast.Not,),
        (ast.In, ast.NotIn, ast.Is, ast.IsNot, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.NotEq, ast.Eq, ast.Compare,),
        (ast.BitOr,),
        (ast.BitXor,),
        (ast.BitAnd,),
        (ast.LShift, ast.RShift,),
        (ast.Add, ast.Sub,),
        (ast.Mult, ast.Div, ast.Mod, ast.FloorDiv,),
        (ast.UAdd, ast.USub, ast.Invert,),
        (ast.Pow,),
        (ast.Subscript, ast.Slice, ast.Call, ast.Attribute,),
        (ast.Tuple, ast.List, ast.Dict,) + (((sys.version_info[0] < 3) and (ast.Repr,)) or ()) ,
    )

    # _precedence maps node types to a precedence number; higher values
    # mean higher precedence.  For example, ast.Mult and ast.Div will
    # have higher precedence values thatn ast.Add and ast.Sub.
    _precedence = {}
    for __precedence_value in range(len(__precedence_list)):
      for __token in __precedence_list[__precedence_value]:
        _precedence[__token] = __precedence_value

    # the __parens method accepts an operand and the operator which is
    # operating on the operand.  if the operand's type has a lower
    # precedence than the operator's type, the operand's formatted value
    # will be returned in (parentheses); otherwise, the operand's value
    # will be returned as is.  If operand is a BinOp or BoolOp node, the
    # comparison is instead made against he operator encapsulted by the
    # BinOp or BoolOp node.
    def __parens(self, operand, operator):
        operand_str = self.visit(operand)
        if isinstance(operand, ast.BinOp):
            operand = operand.op
        elif isinstance(operand, ast.BoolOp):
            operand = operand.op
        operand = type(operand)
        operator = type(operator)
        if operand in self._precedence and operator in self._precedence:
            if self._precedence[operand] < self._precedence[operator]:
                operand_str = "(%s)" % (operand_str,)
        return operand_str

    ####################################################################
    # expression methods - these return a single string with no newline

    def visit_Add(self, node):
        return "+"

    def visit_alias(self, node):
        if getattr(node, 'asname', None) is None:
            return node.name
        else:
            return "%s as %s" % (node.name, node.asname)

    def visit_And(self, node):
        return "and"

    def visit_arg(self, node):
        if getattr(node, 'annotation', None):
          return "%s: %s" % (node.arg, self.visit(node.annotation))
        return node.arg

    def visit_arguments(self, node):
        args = [self.visit(arg) for arg in node.args[:len(node.args) - len(node.defaults)]]
        defargs = ["%s=%s" % (self.visit(arg), self.visit(default)) for (arg, default) in zip(node.args[-len(node.defaults):], node.defaults)]
        if getattr(node, 'vararg', None):
            vararg = ["*" + self.visit(node.vararg)]
        elif getattr(node, 'kwonlyargs', None):
            vararg = ["*"]
        else:
            vararg = []
        if getattr(node, 'kwonlyargs', None):
            kwonlyargs = [self.visit(arg) for arg in node.kwonlyargs[:len(node.kwonlyargs) - len(node.kw_defaults)]]
            kwdefs = ["%s=%s" % (self.visit(arg), self.visit(default)) for (arg, default) in zip(node.kwonlyargs[-len(node.defaults):], node.defaults)]
        else:
            kwonlyargs = []
            kwdefs = []
        if getattr(node, 'kwarg', None):
            kwarg = ["**" + self.visit(node.kwarg)]
        else:
            kwarg = []
        return "(%s)" % (",".join(args + defargs + vararg + kwonlyargs + kwdefs + kwarg),)

    def visit_Attribute(self, node):
        return "%s.%s" % (self.__parens(node.value, node), node.attr)

    def visit_BinOp(self, node):
        return (" %s " % (self.visit(node.op),)).join([self.__parens(operand, node.op) for operand in (node.left, node.right)])

    def visit_BitAnd(self, node):
        return "&"

    def visit_BitOr(self, node):
        return "|"

    def visit_BitXor(self, node):
        return "^"

    def visit_BoolOp(self, node):
        return (" %s " % (self.visit(node.op),)).join([self.__parens(operand, node.op) for operand in node.values])

    def visit_Bytes(self, node):
        return repr(node.s)

    def visit_Call(self, node):
        args = [self.visit(arg) for arg in node.args]
        keywords = [self.visit(keyword) for keyword in node.keywords]
        if getattr(node, 'starargs', None):
            starargs = ["*%s" % (self.visit(node.starargs),)]
        else:
            starargs = []
        if getattr(node, 'kwargs', None):
            kwargs = ["**%s" % (self.visit(node.kwargs),)]
        else:
            kwargs = []
        return "%s(%s)" % (self.visit(node.func), ", ".join(args + keywords + starargs + kwargs))

    def visit_Compare(self, node):
        return "%s %s" % (self.visit(node.left), " ".join(["%s %s" % (self.visit(op), self.visit(right)) for (op, right) in zip(node.ops, node.comparators)]))

    def visit_comprehension(self, node):
        ifs = "".join([" if %s" % (self.visit(ifpart),) for ifpart in node.ifs])
        return "for %s in %s%s" % (self.visit(node.target), self.visit(node.iter), ifs)

    def visit_Dict(self, node):
        return "{%s}" % (", ".join(["%s:%s" % (self.visit(key), self.visit(value)) for (key, value) in zip(node.keys, node.values)]),)

    def visit_DictComp(self, node):
        if getattr(node, 'generators', None):
            return "{%s:%s %s}" % (self.visit(node.key), self.visit(node.value)," ".join(self.visit(generator) for generator in node.generators),)
        return "{%s:%s}" % (self.visit(node.key), self.visit(node.value))

    def visit_Div(self, node):
        return "/"

    re_docstr_escape = re.compile(r'([\\"])')
    re_docstr_remove_blank_front = re.compile(r'^[ \n]*')
    re_docstr_remove_blank_back = re.compile(r'[ \n]*$')
    re_docstr_indent = re.compile(r'^( *).*')
    def visit_DocStr(self, node):
        """an artificial visitor method, called by visit_Expr if its value is a string."""
        docstring = self.re_docstr_remove_blank_front.sub('',
                self.re_docstr_remove_blank_back.sub('',
                        self.re_docstr_escape.sub(r'\\\1', node.s))).split('\n')
        if len(docstring) > 1:
            docstr_indents = [
                len(self.re_docstr_indent.sub(r'\1', ds)) for ds in [
                    ds.rstrip() for ds in docstring[1:]
                ] if ds
            ]
            docstr_indent = min(docstr_indents)
            docstring = ['"""%s\n' % (docstring[0],)] + ["%s\n" % (ds[docstr_indent:],) for ds in docstring[1:]] + ['"""\n']
        else:
            docstring = ['"""%s"""\n' % (docstring[0],)]
        return docstring

    def visit_Ellipsis(self, node):
        return "..."

    def visit_Eq(self, node):
        return "=="

    def visit_ExtSlice(self, node):
        return ", ".join([self.visit(dim) for dim in node.dims])

    def visit_FloorDiv(self, node):
        return "//"

    def visit_GeneratorExp(self, node):
        if getattr(node, 'generators', None):
            return "(%s %s)" % (self.visit(node.elt), " ".join(self.visit(generator) for generator in node.generators),)
        return "(%s)" % (self.visit(node.elt),)

    def visit_Gt(self, node):
        return ">"

    def visit_GtE(self, node):
        return ">="

    def visit_IfExp(self, node):
        return "%s if %s else %s" % (self.visit(node.body), self.visit(node.test), self.visit(node.orelse))

    def visit_In(self, node):
        return "in"

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_Invert(self, node):
        return "~"

    def visit_Is(self, node):
        return "is"

    def visit_IsNot(self, node):
        return "is not"

    def visit_keyword(self, node):
        if getattr(node, 'arg', None):
            return "%s=%s" % (node.arg, self.visit(node.value))
        else:
            return "**%s" % (self.visit(node.value),)

    def visit_Lambda(self, node):
        return "lambda %s: %s" % (self.visit(node.args)[1:-1], self.visit(node.body))

    def visit_List(self, node):
        return "[%s]" % (", ".join([self.visit(elt) for elt in node.elts]),)

    def visit_ListComp(self, node):
        if getattr(node, 'generators', None):
            return "[%s %s]" % (self.visit(node.elt), " ".join(self.visit(generator) for generator in node.generators),)
        return "[%s]" % (self.visit(node.elt),)

    def visit_Lt(self, node):
        return "<"

    def visit_LtE(self, node):
        return "<="

    def visit_LShift(self, node):
        return "<<"

    def visit_Mod(self, node):
        return "%"

    def visit_Mult(self, node):
        return "*"

    def visit_Name(self, node):
        return node.id

    def visit_NameConstant(self, node):
        return repr(node.value)

    def visit_Not(self, node):
        return "not"

    def visit_NotEq(self, node):
        return "!="

    def visit_NotIn(self, node):
        return "not in"

    def visit_Num(self, node):
        return repr(node.n)

    def visit_Or(self, node):
        return "or"

    def visit_Pow(self, node):
        return "**"

    def visit_Repr(self, node):
        return "`%s`" % (self.visit(node.value),)

    def visit_RShift(self, node):
        return ">>"

    def visit_Set(self, node):
        return "{%s}" % (", ".join(["%s" % (self.visit(elt),) for elt in node.elts]),)

    def visit_SetComp(self, node):
        if getattr(node, 'generators', None):
            return "{%s %s}" % (self.visit(node.elt), " ".join(self.visit(generator) for generator in node.generators),)
        return "{%s}" % (self.visit(node.elt),)

    def visit_Slice(self, node):
        if getattr(node, 'lower', None):
            lower = self.visit(node.lower)
        else:
            lower = ""
        if getattr(node, 'upper', None):
            upper = self.visit(node.upper)
        else:
            upper = ""
        if getattr(node, 'step', None):
            return ":".join([lower, upper, self.visit(node.step)])
        else:
            return ":".join([lower, upper])

    def visit_Starred(self, node):
        return "*" + self.visit(node.value)

    def visit_Str(self, node):
        return repr(node.s)

    def visit_Sub(self, node):
        return "-"

    def visit_Subscript(self, node):
        return "%s[%s]" % (self.visit(node.value), self.visit(node.slice))

    def visit_Tuple(self, node):
        if len(node.elts) == 1:
            return "(%s,)" % (self.visit(node.elts[0]),)
        return "(%s)" % (", ".join([self.visit(elt) for elt in node.elts]),)

    def visit_UAdd(self, node):
        return "+"

    def visit_USub(self, node):
        return "-"

    def visit_UnaryOp(self, node):
        return "%s %s" % (self.visit(node.op), self.__parens(node.operand, node.op))

    def visit_withitem(self, node):
        if getattr(node, 'optional_vars', None) is None:
            return self.visit(node.context_expr)
        else:
            return "%s as %s" % (self.visit(node.context_expr), self.visit(node.optional_vars),)

    def visit_Yield(self, node):
        if getattr(node, 'value', None):
            return "yield %s" % (self.visit(node.value),)
        return "yield"

    def visit_YieldFrom(self, node):
        return "yield from %s" % (self.visit(node.value),)

    ####################################################################
    # statement methods - these return either a single string or a list
    # of strings, all terminated with a `\n` newline.

    def visit_Assert(self, node):
        if getattr(node, 'msg', None) is None:
            msg = ""
        else:
            msg = "," + self.visit(node.msg)
        return "assert %s%s\n" % (self.visit(node.test), msg)

    def visit_Assign(self, node):
        return "%s = %s\n" % (",".join([self.visit(target) for target in node.targets]), self.visit(node.value))

    def visit_AugAssign(self, node):
        return "%s %s= %s\n" % (self.visit(node.target), self.visit(node.op), self.visit(node.value))

    def visit_Break(self, node):
        return "break\n"

    def visit_ClassDef(self, node):
        decorators = [self.visit(dec) for dec in node.decorator_list]
        supers = []
        if getattr(node, 'bases', None) is not None:
            supers.extend([self.visit(base) for base in node.bases])
        if getattr(node, 'keywords', None) is not None:
            supers.extend([self.visit(kw) for kw in node.keywords])
        if getattr(node, 'starargs', None) is not None:
            supers.append("*" + self.visit(node.starargs))
        if getattr(node, 'kwargs', None) is not None:
            supers.append("**" + self.visit(node.kwargs))
        if len(supers):
            supers = "(%s)" % (", ".join(supers))
        else:
            supers = ""
        classdef = ["class %s%s:\n" % (node.name, supers)]
        try:
            if node.docstring is not None:
                body = [ast.Expr(ast.Str(node.docstring))] + node.body
            else:
                body = node.body
        except AttributeError:
            body = node.body
        classbody = self.__process_body(body, "    ")
        return decorators + classdef + classbody

    def visit_Continue(self, node):
        return "continue\n"

    def visit_Delete(self, node):
        return "del %s\n" % (",".join([self.visit(target) for target in node.targets]),)

    if sys.version_info[0] == 2:
        def visit_ExceptHandler(self, node):
            if not node.type:
                return ["except:\n"] + self.__process_body(node.body, "    ")
            if getattr(node, 'name', None):
                return ["except %s,%s:\n" % (self.visit(node.type), self.visit(node.name))] + self.__process_body(node.body, "    ")
            return ["except %s:\n" % (self.visit(node.type),)] + self.__process_body(node.body, "    ")
    else:
        def visit_ExceptHandler(self, node):
            if not node.type:
                return ["except:\n"] + self.__process_body(node.body, "    ")
            if getattr(node, 'name', None):
                return ["except %s as %s:\n" % (self.visit(node.type), node.name)] + self.__process_body(node.body, "    ")
            return ["except %s:\n" % (self.visit(node.type),)] + self.__process_body(node.body, "    ")

    def visit_Exec(self, node):
        inglobals, inlocals = "", ""
        if getattr(node, 'globals', None) is not None:
            inglobals = " in %s" % (self.visit(node.globals),)
            if getattr(node, 'locals', None) is not None:
                inlocals = ", %s" % (self.visit(node.locals),)
        return "exec %s%s%s\n" % (self.visit(node.body), inglobals, inlocals)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Str):
            return self.visit_DocStr(node.value)
        return [ self.visit(node.value) + '\n' ]

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_For(self, node):
        if getattr(node, 'orelse', None) is None or len(node.orelse) == 0:
            orelse = []
        else:
            orelse = ["else:\n"] + self.__process_body(node.orelse, "    ")
        return [
            "for %s in %s:\n" % (
                self.visit(node.target),
                self.visit(node.iter),
            )
        ] + self.__process_body(node.body, "    ") + orelse

    def visit_FunctionDef(self, node):
        decorators = [self.visit(dec) for dec in node.decorator_list]
        funcdef = ["def %s%s:\n" % (node.name, self.visit(node.args))]
        try:
            if node.docstring is not None:
                body = [ast.Expr(ast.Str(node.docstring))] + node.body
            else:
                body = node.body
        except AttributeError:
            body = node.body
        funcbody = self.__process_body(body, "    ")
        return decorators + funcdef + funcbody

    def visit_Global(self, node):
        return "global %s\n" % (",".join(node.names),)

    def visit_If(self, node):
        content = ["if %s:\n" % (self.visit(node.test),)] + self.__process_body(node.body, "    ")
        if getattr(node, 'orelse', None) is not None and len(node.orelse) > 0:
            if isinstance(node.orelse[0], ast.If):
                orelse = self.__process_body(node.orelse, "")
                orelse[0] = "el" + orelse[0]
            else:
                orelse = ["else:\n"] + self.__process_body(node.orelse, "    ")
            content.extend(orelse)
        return content

    def visit_Import(self, node):
        return [ "import %s\n" % (self.visit(name),) for name in node.names ]

    def visit_ImportFrom(self, node):
        return "from %s%s import %s\n" % ("." * node.level, node.module, ", ".join([self.visit(name) for name in node.names]),)

    def visit_Module(self, node):
        try:
            if node.docstring is not None:
                body = [ast.Expr(ast.Str(node.docstring))] + node.body
            else:
                body = node.body
        except AttributeError:
            body = node.body
        return self.__process_body(body)

    def visit_Nonlocal(self, node):
        return "nonlocal %s\n" % (",".join(node.names),)

    def visit_Pass(self, node):
        return "pass\n"

    def visit_Print(self, node):
        if getattr(node, 'dest', None) is None:
            dest = ""
        else:
            dest = ">> %s, " % (self.visit(node.dest),)
        if getattr(node, 'nl', None):
            nl = ""
        else:
            nl = ","
        return "print %s%s%s\n" % (dest, ", ".join([self.visit(value) for value in node.values]), nl)

    def visit_Raise(self, node):
        if getattr(node, 'clause', None) is not None:
            return "raise %s from %s\n" % (self.visit(node.exc), self.visit(node.clause))
        elif getattr(node, 'exc', None) is not None:
            return "raise %s\n" % (self.visit(node.exc),)
        elif getattr(node, 'tback', None) is not None:
            params = (node.type, node.inst, node.tback)
        elif getattr(node, 'inst', None) is not None:
            params = (node.type, node.inst)
        elif getattr(node, 'type', None) is not None:
            params = (node.type,)
        else:
            params = ""
        if len(params):
            params = " " + ",".join([self.visit(param) for param in params])
        return "raise%s\n" % (params,)

    def visit_Return(self, node):
        if getattr(node, 'value', None) is not None:
            return "return %s\n" % (self.visit(node.value),)
        return "return\n"

    def visit_Try(self, node):
        retval = ["try:\n"] + self.__process_body(node.body, "    ")
        handlers = getattr(node, 'handlers', None)
        if handlers is not None and len(handlers) > 0:
            for handler in handlers:
                retval.extend(self.visit(handler))
        orelse = getattr(node, 'orelse', None)
        if orelse is not None and len(orelse) > 0:
            retval.extend(["else:\n"] + self.__process_body(orelse, "    "))
        final = getattr(node, 'finalbody', None)
        if final is not None:
            retval.extend( ["finally:\n"] + self.__process_body(node.finalbody, "    ") )
        return retval

    visit_TryExcept = visit_Try
    visit_TryFinally = visit_Try

    def visit_While(self, node):
        if getattr(node, 'orelse', None) is None or len(node.orelse) == 0:
            orelse = []
        else:
            orelse = ["else:\n"] + self.__process_body(node.orelse, "    ")
        return [
            "while %s:\n" % (
                self.visit(node.test),
            )
        ] + self.__process_body(node.body, "    ") + orelse

    def visit_With(self, node):
        if getattr(node, 'items',None) is not None:
            asvars = ", ".join([self.visit(item) for item in node.items])
        else:
            if getattr(node, 'optional_vars', None) is None:
                asvars = self.visit(node.context_expr)
            else:
                asvars = "%s as %s" % (self.visit(node.context_expr), self.visit(node.optional_vars),)
        if len(node.body) == 1 and isinstance(node.body[0], ast.With):
            subwith = self.visit(node.body[0])
            return [ "with %s, %s" % (asvars, subwith[0][5:]) ] + subwith[1:]
        else:
            return [
                "with %s:\n" % (asvars,)
            ] + self.__process_body(node.body, "    ")

########################################################################
# simple tests

if __name__ == '__main__':
    fmt = ASTFormatter()
    import inspect
    my_module = inspect.getfile(inspect.currentframe())
    sys.out.write(fmt.format(ast.parse(open(my_module, 'rU').read(), my_module, mode='exec')))
