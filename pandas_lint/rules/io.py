import ast
from typing import Optional
from .base import Rule, Issue, RuleRegistry


@RuleRegistry.register
class ToCsvRule(Rule):
    code = "IO001"
    message = "Are you saving intermediate data? 'to_parquet' is much faster and lighter than 'to_csv'."
    severity = "INFO"

    def check(self, node: ast.AST, context: dict) -> Optional[Issue]:
        if not isinstance(node, ast.Call):
            return None
        if not isinstance(node.func, ast.Attribute):
            return None
        if node.func.attr != 'to_csv':
            return None

        return Issue(node.lineno, node.col_offset, self.code, self.message, self.severity)
