import ast
from typing import Optional
from .base import Rule, Issue, RuleRegistry


@RuleRegistry.register
class InplaceTrueRule(Rule):
    code = "STY001"
    message = "Avoid 'inplace=True'. It breaks method chaining and often doesn't save memory. Assign the result back to the variable."
    severity = "INFO"

    def check(self, node: ast.AST, context: dict) -> Optional[Issue]:
        if not isinstance(node, ast.Call):
            return None

        for kw in node.keywords:
            if kw.arg == 'inplace':
                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    return Issue(node.lineno, node.col_offset, self.code, self.message, self.severity)

        return None
