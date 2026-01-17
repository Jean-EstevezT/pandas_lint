import ast
from typing import Optional
from .base import Rule, Issue, RuleRegistry


@RuleRegistry.register
class ReadCsvUsecolsRule(Rule):
    code = "MEM001"
    message = "Loading CSV without 'usecols'. If the file is large, you are wasting RAM loading columns you don't use."
    severity = "WARNING"

    def check(self, node: ast.AST, context: dict) -> Optional[Issue]:
        if not isinstance(node, ast.Call):
            return None
        if not isinstance(node.func, ast.Attribute):
            return None
        if not isinstance(node.func.value, ast.Name):
            return None

        pandas_alias = context.get('pandas_alias', 'pd')
        if node.func.value.id != pandas_alias or node.func.attr != 'read_csv':
            return None

        has_usecols = any(kw.arg == 'usecols' for kw in node.keywords)
        if has_usecols:
            return None

        return Issue(node.lineno, node.col_offset, self.code, self.message, self.severity)
