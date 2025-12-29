import ast
from typing import List, Dict, Any
from dataclasses import dataclass

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
                self.issues.append(Issue(
                    line=node.lineno,
                    col=node.col_offset,
                    code='PERF001',
                    message="Usage of '.iterrows()' detected. It is extremely slow. Use vectorization or .itertuples().",
                    severity='CRITICAL'
                ))
            elif node.func.attr == 'apply':
                self.issues.append(Issue(
                    line=node.lineno,
                    col=node.col_offset,
                    code='PERF002',
                    message="Usage of '.apply()'. If the operation is simple math, use direct vectorization (native Numpy/Pandas) to be 100x faster.",
                    severity='WARNING'
                ))

        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == self.pandas_alias and node.func.attr == 'read_csv':
                has_usecols = any(kw.arg == 'usecols' for kw in node.keywords)
                if not has_usecols:
                    self.issues.append(Issue(
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
