import ast
from typing import List, Dict, Any
try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None
from dataclasses import dataclass
import os

@dataclass
class Issue:
    line: int
    col: int
    code: str
    message: str
    severity: str       # 'CRITICAL', 'WARINING', 'INFO'    

class PandasVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[Issue] = []
        self.pandas_alias = 'pandas'
        self.ignored_codes = self._load_config()

    def _load_config(self) -> List[str]:
        """Loads configuration from pyproject.toml"""
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
                        data = toml.load(f.read().decode('utf-8'))
                else: 
                     return []

            return data.get("tool", {}).get("pandas-linter", {}).get("ignore", [])
        except Exception:
            return []

    def add_issue(self, issue: Issue):
        if issue.code not in self.ignored_codes:
            self.issues.append(issue)
    
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "pandas":
                self.pandas_alias = alias.asname or 'pandas'
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module == "pandas":
            pass
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'iterrows':
                self.add_issue(Issue(
                    line=node.lineno,
                    col=node.col_offset,
                    code='PERF001',
                    message="Usage of '.iterrows()' detected. It is extremely slow. Use vectorization or .itertuples().",
                    severity='CRITICAL'
                ))
            elif node.func.attr == 'apply':
                accessor_suggestion = None
                if node.args and isinstance(node.args[0], ast.Lambda):
                    lambda_body = node.args[0].body
                    if isinstance(lambda_body, ast.Call) and isinstance(lambda_body.func, ast.Attribute):
                        if lambda_body.func.attr in ['upper', 'lower', 'strip', 'replace', 'split']:
                             accessor_suggestion = ".str"
                    
                    if isinstance(lambda_body, ast.Attribute):
                        if lambda_body.attr in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                             accessor_suggestion = ".dt"
                
                if accessor_suggestion:
                    self.add_issue(Issue(
                        line=node.lineno,
                        col=node.col_offset,
                        code='PERF003' if accessor_suggestion == '.str' else 'PERF004',
                        message=f"Use the vectorized accessor {accessor_suggestion} (e.g. df['c']{accessor_suggestion}.method) instead of apply.",
                        severity='WARNING'
                    ))
                else:
                    self.add_issue(Issue(
                        line=node.lineno,
                        col=node.col_offset,
                        code='PERF002',
                        message="Usage of '.apply()'. If the operation is simple math, use direct vectorization (native Numpy/Pandas) to be 100x faster.",
                        severity='WARNING'
                    ))
            
            elif node.func.attr == 'to_csv':
                self.add_issue(Issue(
                    line=node.lineno,
                    col=node.col_offset,
                    code='IO001',
                    message="Are you saving intermediate data? 'to_parquet' is much faster and lighter than 'to_csv'.",
                    severity='INFO'
                ))
            
            # Check fr SQL Injection
            elif node.func.attr in ['read_sql', 'read_sql_query']:
                if node.args:
                    sql_arg = node.args[0]
                    is_fstring = isinstance(sql_arg, ast.JoinedStr)
                    is_concat = isinstance(sql_arg, ast.BinOp) and isinstance(sql_arg.op, (ast.Add, ast.Mod))
                    
                    if is_fstring or is_concat:
                         self.add_issue(Issue(
                            line=node.lineno,
                            col=node.col_offset,
                            code='SEC001',
                            message="Potential SQL Injection detected. Use 'params' argument for dynamic queries instead of f-strings or concatenation.",
                            severity='CRITICAL'
                        ))
    
        if any(kw.arg == 'inplace' and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in node.keywords):
             self.add_issue(Issue(
                line=node.lineno,
                col=node.col_offset,
                code='STY001', 
                message="Avoid 'inplace=True'. It breaks method chaining and often doesn't save memory. Assign the result back to the variable.",
                severity='INFO'
            ))

        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == self.pandas_alias and node.func.attr == 'read_csv':
                has_usecols = any(kw.arg == 'usecols' for kw in node.keywords)
                if not has_usecols:
                    self.add_issue(Issue(
                        line=node.lineno,
                        col=node.col_offset,
                        code='MEM001',
                        message="Loading CSV without 'usecols'. If the file is large, you are wasting RAM loading columns you don't use.",
                        severity='WARNING'
                    ))

        self.generic_visit(node)

    def visit_For(self, node):
        """Detects for loops iterating over DataFrames"""
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute):
            if node.iter.func.attr in ['iterrows', 'itertuples']:
                pass
        self.generic_visit(node)
