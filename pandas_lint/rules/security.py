import ast
from typing import Optional
from .base import Rule, Issue, RuleRegistry


@RuleRegistry.register
class SqlInjectionRule(Rule):
    code = "SEC001"
    message = "Potential SQL Injection detected. Use 'params' argument for dynamic queries instead of f-strings or concatenation."
    severity = "CRITICAL"

    def check(self, node: ast.AST, context: dict) -> Optional[Issue]:
        if not isinstance(node, ast.Call):
            return None
        if not isinstance(node.func, ast.Attribute):
            return None
        if node.func.attr not in ['read_sql', 'read_sql_query']:
            return None
        if not node.args:
            return None

        sql_arg = node.args[0]
        is_fstring = isinstance(sql_arg, ast.JoinedStr)
        is_concat = isinstance(sql_arg, ast.BinOp) and isinstance(sql_arg.op, (ast.Add, ast.Mod))

        if is_fstring or is_concat:
            return Issue(node.lineno, node.col_offset, self.code, self.message, self.severity)

        return None
