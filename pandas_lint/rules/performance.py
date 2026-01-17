import ast
from typing import Optional
from .base import Rule, Issue, RuleRegistry


@RuleRegistry.register
class IterrowsRule(Rule):
    code = "PERF001"
    message = "Usage of '.iterrows()' detected. It is extremely slow. Use vectorization or .itertuples()."
    severity = "CRITICAL"

    def check(self, node: ast.AST, context: dict) -> Optional[Issue]:
        if not isinstance(node, ast.Call):
            return None
        if not isinstance(node.func, ast.Attribute):
            return None
        if node.func.attr != 'iterrows':
            return None

        return Issue(node.lineno, node.col_offset, self.code, self.message, self.severity)


@RuleRegistry.register
class ApplyRule(Rule):
    code = "PERF002"
    message = "Usage of '.apply()'. If the operation is simple math, use direct vectorization to be 100x faster."
    severity = "WARNING"

    def check(self, node: ast.AST, context: dict) -> Optional[Issue]:
        if not isinstance(node, ast.Call):
            return None
        if not isinstance(node.func, ast.Attribute):
            return None
        if node.func.attr != 'apply':
            return None

        if node.args and isinstance(node.args[0], ast.Lambda):
            lambda_body = node.args[0].body

            if isinstance(lambda_body, ast.Call) and isinstance(lambda_body.func, ast.Attribute):
                if lambda_body.func.attr in ['upper', 'lower', 'strip', 'replace', 'split']:
                    return Issue(
                        node.lineno, node.col_offset,
                        "PERF003",
                        "Use the vectorized accessor .str (e.g. df['col'].str.method()) instead of apply.",
                        "WARNING"
                    )

            if isinstance(lambda_body, ast.Attribute):
                if lambda_body.attr in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                    return Issue(
                        node.lineno, node.col_offset,
                        "PERF004",
                        "Use the vectorized accessor .dt (e.g. df['col'].dt.year) instead of apply.",
                        "WARNING"
                    )

        return Issue(node.lineno, node.col_offset, self.code, self.message, self.severity)
