from abc import abstractmethod
from dataclasses import dataclass
import inspect
import time
from copy import deepcopy
from typing import Optional, Tuple, Union, Sequence


@dataclass
class Module:
    """这是一个模块基类，所有条件链中的模块都继承于它"""
    name: Optional[str] = None
    input_names: Optional[Union[Tuple[str, ...], str]] = None
    output_names: Optional[Union[Tuple[str, ...], str]] = None
    timing: bool = False
    lazy_initialized: bool = False

    def __post_init__(self):
        self.internal_input_names = list(key for key in inspect.signature(
            self.invoke).parameters.keys() if key != 'self')
        if self.name is None:
            self.name = self.__class__.__name__

    def __call__(self, context: dict):
        if not self.lazy_initialized:
            self.lazy_init()
            self.lazy_initialized = True
        input_args = self.get_input_args(context)
        if self.timing:
            t1 = time.time()
        output = self.invoke(**input_args)
        if self.timing:
            t2 = time.time()
            context.update(f'{self.name}_cost_time',
                           f'{t2 - t1: .6f}s')  # type: ignore
        context.update(self.parse_output_to_dict(output))
        return context

    @abstractmethod
    def invoke(self, **kwargs):
        pass

    def lazy_init(self):
        pass

    @classmethod
    def new(cls, **kwargs):
        # 创建一个装饰器，用于定义新的 node
        def decorator(obj):
            if isinstance(obj, Module):
                module = deepcopy(obj)
                module.update(**kwargs)
                return module
            elif inspect.isfunction(obj):
                if 'name' not in kwargs:
                    kwargs['name'] = obj.__name__
                module = cls(**kwargs)
                module.invoke = obj
                module.internal_input_names = list(
                    key for key in inspect.signature(obj).parameters.keys() if key != 'self')
                return module
            else:
                raise ValueError(
                    f"{obj} must be a function or a subclass of Module")
        return decorator

    def get_input_args(self, context):
        input_args = {}
        if self.input_names:
            if isinstance(self.input_names, str):
                self.input_names = (self.input_names,)
            for i in range(len(self.internal_input_names)):
                if i < len(self.input_names):
                    input_args[self.internal_input_names[i]
                               ] = context[self.input_names[i]]
                elif self.internal_input_names[i] in context:
                    input_args[self.internal_input_names[i]
                               ] = context[self.internal_input_names[i]]
        else:
            for k in self.internal_input_names:
                if k in context:
                    input_args[k] = context[k]
        return input_args

    def parse_output_to_dict(self, output):
        if self.output_names is None:
            output_dict = {f'{self.name}_output': output}
        elif isinstance(self.output_names, str):
            output_dict = {self.output_names: output}
        else:
            if len(output) != len(self.output_names):
                raise ValueError(
                    f'output tuple length must equal to output_names `{self.output_names}`')
            output_dict = {k: v for k, v in zip(
                self.output_names, output)}
        return output_dict

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise ValueError(f"Module {self.name} has no attribute `{k}`")

if __name__ == '__main__':

    class NewModule(Module):

        def invoke(self, **kwargs):
            print("hello world")

    m = NewModule(name='hello')
    print(m({}))
    print(m.input_names)
    print(m.internal_input_names)

    @Module.new()
    def func(hello_output):
        print(hello_output)
        print('hello_func')

    print(func(m({})))
