from dataclasses import dataclass
from typing import Callable, Optional
from .base_module import Module


@dataclass
class BoolCondition(Module):

    key: Optional[Callable] = None

    def __post_init__(self):
        super().__post_init__()
        if self.key is None:
            raise ValueError("key must be set")

    def invoke(self, x) -> bool:
        return self.key(x)  # type: ignore

    def get_input_args(self, state):
        return state


@dataclass
class LoopCondition(Module):

    max_loop: Optional[int] = None
    loop_key: Optional[Callable] = None

    def __post_init__(self):
        super().__post_init__()
        if self.max_loop is None and self.loop_key is None:
            raise ValueError("max_loop or loop_key must be set")
        self.loop_count = 0

    def invoke(self, x) -> bool:
        if self.loop_key is not None:
            if self.max_loop is not None and self.loop_count >= self.max_loop:
                self.loop_count = 0
                return False
            if self.loop_key(x) is True:
                self.loop_count += 1
                return True
            else:
                self.loop_count = 0
                return False
        else:
            if self.loop_count < self.max_loop:  # type: ignore
                self.loop_count += 1
                return True
            else:
                self.loop_count = 0
                return False

    def get_input_args(self, state):
        return state
