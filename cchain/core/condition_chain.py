from typing import Any, Sequence
from .conditions import BoolCondition, LoopCondition


class ConditionChain:

    def __init__(self, modules, collect_keys=None):
        if not isinstance(modules, list) or len(modules) == 0:
            raise ValueError("No modules found.")
        self.modules = modules
        self.collect_keys = collect_keys
        self.chain, self.state_transition, self.start_module_name = self.parse_to_chain(modules)

    def __call__(self, context) -> Any:
        current_module_name = self.start_module_name
        while True:
            if current_module_name is None:
                break
            current_module = self.chain[current_module_name]
            if isinstance(current_module, BoolCondition):
                if current_module(context):
                    current_module_name = self.state_transition[current_module_name][0]
                else:
                    current_module_name = self.state_transition[current_module_name][1]
            elif isinstance(current_module, LoopCondition):
                if current_module(context):
                    current_module_name = self.state_transition[current_module_name][0]
                else:
                    current_module_name = self.state_transition[current_module_name][1]
            else:
                context = current_module(context)
                if current_module_name not in self.state_transition:
                    break
                current_module_name = self.state_transition[current_module_name]
        if self.collect_keys is None:
            return context
        else:
            output = {key: context.get(key, None) for key in self.collect_keys}
            return output
        
    def get_all_modules(self, modules):
        if isinstance(modules, Sequence):
            all_modules = []
            for module in modules:
                all_modules.append(self.get_all_modules(module))
            return all_modules
        else:
            return modules
        
    def get_modules_and_tags(self, modules, level=-1):
        if isinstance(modules, Sequence):
            all_modules = []
            for i, module in enumerate(modules):
                if i == 0 and level != -1:
                    all_modules.append((module, level))
                else:
                    all_modules.extend(self.get_modules_and_tags(module, level+1))
            return all_modules
        else:
            return [(modules, level)]

    def parse_to_chain(self, modules):
        chain = {}
        state_transition = {}
        start_module_name = None
        module_tags = self.get_modules_and_tags(modules)
        for i, (module, tag) in enumerate(module_tags):
            # rename duplicate module
            if module.name not in chain:
                chain[module.name] = module
            else:
                index = 1
                module_name = f'{module.name}_{index}'
                while module_name in chain:
                    index += 1
                    module_name = f'{module.name}_{index}'
                module.name = module_name
                chain[module.name] = module
            # add state transition
            if i == 0:
                start_module_name = module.name
                continue
            prev_module = module_tags[i-1][0]
            if prev_module.name in state_transition:
                continue
            if isinstance(prev_module, BoolCondition):
                # find next parent list module
                find_id = i + 1
                while find_id < len(module_tags) and module_tags[find_id][1] >= tag:
                    find_id += 1
                if find_id < len(module_tags):
                    state_transition[prev_module.name] = (module.name, module_tags[find_id][0].name)
                else:
                    state_transition[prev_module.name] = (module.name, None)
            elif isinstance(prev_module, LoopCondition):
                # find next parent list module
                find_id = i + 1
                while find_id < len(module_tags) and module_tags[find_id][1] >= tag:
                    find_id += 1
                if find_id < len(module_tags):
                    state_transition[prev_module.name] = (module.name, module_tags[find_id][0].name)
                else:
                    state_transition[prev_module.name] = (module.name, None)
                # find last module of this loop
                state_transition[module_tags[find_id-1][0].name] = prev_module.name
            else:
                state_transition[prev_module.name] = module.name
            if i == len(module_tags) - 1 and module.name not in state_transition:
                state_transition[module.name] = None
        return chain, state_transition, start_module_name
        
    
