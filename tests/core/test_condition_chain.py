import unittest
from cchain.core.base_module import Module
from cchain.core.conditions import BoolCondition, LoopCondition
from cchain.core.condition_chain import ConditionChain

class DemoModule(Module):
    
    def invoke(self, x):
        return x

class TestConditionChain(unittest.TestCase):

    def test_init_with_invalid_inputs(self):
        with self.assertRaises(ValueError):
            ConditionChain([], collect_keys=None)

    def test_call_without_collect_keys(self):
        modules = [DemoModule(), DemoModule()]
        condition_chain = ConditionChain(modules, collect_keys=None)
        result = condition_chain({'x': 'x'})
        self.assertEqual(result, {'DemoModule_output': 'x',
                      'DemoModule_1_output': 'x', 'x': 'x'})

    def test_call_with_collect_keys(self):
        modules = [DemoModule(output_names='d1'), DemoModule(output_names='d2')]
        condition_chain = ConditionChain(
            modules, collect_keys=["d1"])
        result = condition_chain({'x': 'x'})
        self.assertEqual(result, {"d1": "x"})

    def test_parse_to_chain(self):
        modules = [DemoModule(output_names='d1'),
                   [BoolCondition(key=lambda x: x['d1']), DemoModule()], [LoopCondition(max_loop=2), DemoModule()]]
        chain, transition, start = ConditionChain(
            modules, collect_keys=None).parse_to_chain(modules)
        print(ConditionChain(
            modules, collect_keys=None))
        print(DemoModule(output_names='d1'))
        self.assertEqual(len(chain), 5)
        self.assertEqual(len(transition), 5)
        self.assertEqual(start, 'DemoModule')


if __name__ == '__main__':
    unittest.main()
