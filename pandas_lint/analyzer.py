import ast
import os
from typing import List

try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None

from .rules import RuleRegistry, Issue


class PandasVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[Issue] = []
        self.pandas_alias = 'pd'
        self.ignored_codes = self._load_config()
        self.rules = RuleRegistry.get_all()

    def _load_config(self) -> List[str]:
        config_path = "pyproject.toml"
        if not os.path.exists(config_path) or tomllib is None:
            return []

        try:
            with open(config_path, "rb") as f:
                if hasattr(tomllib, 'load'):
                    try:
                        data = tomllib.load(f)
                    except TypeError:
                        f.seek(0)
                        import toml
                        data = toml.loads(f.read().decode('utf-8'))
                else:
                    return []

            return data.get("tool", {}).get("pandas-linter", {}).get("ignore", [])
        except Exception:
            return []

    @property
    def context(self) -> dict:
        return {'pandas_alias': self.pandas_alias}

    def _run_rules(self, node: ast.AST):
        for rule in self.rules:
            if rule.code in self.ignored_codes:
                continue
            issue = rule.check(node, self.context)
            if issue and issue.code not in self.ignored_codes:
                self.issues.append(issue)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "pandas":
                self.pandas_alias = alias.asname or 'pandas'
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.generic_visit(node)

    def visit_Call(self, node):
        self._run_rules(node)
        self.generic_visit(node)

    def visit_For(self, node):
        self._run_rules(node)
        self.generic_visit(node)
