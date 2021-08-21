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


class Plugin:

    def __init_subclass__(cls) -> None:
        _commands = {}
        for base in reversed(cls.__mro__):
            for attr_name, value in base.__dict__.items():
                if isinstance(value, Command):
                    value.plugin = cls
                    _commands[value.name] = value
        cls._commands = _commands

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def command(**attrs):
    def decorator(func):
        name = attrs.get('name', func.__name__)
        new_c = Command(func, name = name, **attrs)
        return new_c 
    return decorator

def group(**attrs):
    raise NotImplementedError