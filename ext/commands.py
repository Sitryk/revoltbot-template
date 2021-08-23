import asyncio
import inspect


class Command:

    def __init__(self, func, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Function must be a coroutine.')
        self._callback = func
        self.aliases = kwargs.get('aliases', [])
        self.name = kwargs.get('name', func.__name__)
        self.plugin = kwargs.get('plugin', None)
        self.__doc__ = kwargs.get('docstring', func.__doc__)
        self.signature = inspect.signature(func)
        self.parent = kwargs.get('parent', None)

    async def __call__(self, *args, **kwargs):
        if not self.plugin is None:
            return await self._callback(self.plugin, *args, **kwargs)
        else:
            return await self._callback(*args, **kwargs)

    @property
    def full_name(self):
        """Full name for a subcommand"""
        if self.parent is None:
            return self.name
        return self.parent.full_name + ' ' + self.name

class Group(Command):

    def __init__(self, *args, **kwargs):
        self._commands = {}
        super().__init__(*args, **kwargs)

    def command(self, cls=None, *args, **kwargs):
        if cls is None:
            cls = Command
        return command(cls=cls, parent=self, *args, **kwargs)

    def group(self, *args, **kwargs):
        return self.command(cls=Group)

        

class Plugin:

    def __init_subclass__(cls) -> None:
        _commands = {}
        for base in reversed(cls.__mro__):
            for attr_name, value in base.__dict__.items():
                if isinstance(value, Command):
                    value.plugin = cls
                    print(value.full_name)
                    _commands[value.full_name] = value
        cls._commands = _commands

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def command(cls=None, **attrs):
    """
    Register a command
    """
    if cls is None:
        cls = Command

    def decorator(func):
        name = attrs.get('name', func.__name__)
        new_c = cls(func, name=name, **attrs)
        return new_c
    return decorator

def group(**attrs):
    """
    Decorator for registering a command group
    """
    return command(cls=Group)