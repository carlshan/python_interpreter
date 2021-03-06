import types
import inspect


class Function(object):
    """
    Create a realistic function object, defining the things the interpreter
    expects.
    """

    __slots__ = [
        'func_code', 'func_name', 'func_defaults', 'func_globals',
        'func_locals', 'func_dict', 'func_closure',
        '__name__', '__dict__', '__doc__',
        '_vm', '_func'
    ]

    def __init__(self, name, code, globs, defaults, closure, vm):
        self._vm = vm
        self.func_code = code
        self.func_name = self.__name__ = name or code.co_name
        self.func_defaults = tuple(defaults)
        self.func_globals = globs
        self.func_locals = self._vm.frame.f_locals
        self.__dict__ = {}
        self.func_closure = closure
        self.__doc__ = code.co_consts[0] if code.co_consts else None

        kw = {
            'argdefs': self.func_defaults,
        }
        if closure:
            # Create a tuple of all the cells in the closure
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code, globs, **kw)

    def __call__(self, *args, **kwargs):
        """When calling a Function, make a new frame and run it."""
        callargs = inspect.getcallargs(self.__func, *args, **kwargs)
        # Use callargs to provide a mapping of arguments: values to pass into
        # the new frame.
        frame = self._vm.make_frame(
            self.func_code, callargs, self.func_globals, {}
        )
        return self._vm.run_frame(frame)


def make_cell(value):
    """
    Functions have a __closure__ attribute which contains information on
    the values accessed in the enclosing scope.

    This returns an actual python cell object with the enclosed values.
    """
    fn = (lambda x: lambda: x)(value)
    """
    The above is similar to the following code:
        def func1(x):
            def func2():
                return x
            return func2

        fn = func1(value)
        Since fn references an enclosed function, it will have a __closure__
        attribute.
    """
    # Returns cell object
    return fn.__closure__[0]
