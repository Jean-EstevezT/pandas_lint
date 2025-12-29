import libcst as cst
from libcst import matchers as m
from typing import Optional, Union

class PandasAutoFixer(cst.CSTTransformer):
    """
    Transforms Pandas code to use more efficient accessors
    Ref: https://github.com/Instagram/LibCST
    """

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        if m.matches(updated_node, m.Call(func=m.Attribute(attr=m.Name("apply")))):
            if len(updated_node.args) == 1 and m.matches(updated_node.args[0].value, m.Lambda()):
                lambda_node = updated_node.args[0].value
                if m.matches(lambda_node.body, m.Call(func=m.Attribute(attr=m.Name("upper")))):
                    return self._transform_to_accessor(updated_node.func.value, "str", "upper")
                
                if m.matches(lambda_node.body, m.Call(func=m.Attribute(attr=m.Name("lower")))):
                    return self._transform_to_accessor(updated_node.func.value, "str", "lower")
                     
                if m.matches(lambda_node.body, m.Call(func=m.Attribute(attr=m.Name("strip")))):
                    return self._transform_to_accessor(updated_node.func.value, "str", "strip")

                if m.matches(lambda_node.body, m.Attribute()):
                    attr_name = lambda_node.body.attr.value
                    if attr_name in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                        return self._transform_to_accessor(updated_node.func.value, "dt", attr_name, is_method=False)
                        
        return updated_node

    def _transform_to_accessor(self, df_node: cst.BaseExpression, accessor: str, method: str, is_method: bool = True) -> cst.BaseExpression:
        acc = cst.Attribute(
            value=df_node,
            attr=cst.Name(accessor)
        )
        final_attr = cst.Attribute(
            value=acc,
            attr=cst.Name(method)
        )
        
        if is_method:
            return cst.Call(func=final_attr)
        else:
            return final_attr

def fix_code(code: str) -> str:
    tree = cst.parse_module(code)
    transformer = PandasAutoFixer()
    modified_tree = tree.visit(transformer)
    return modified_tree.code
