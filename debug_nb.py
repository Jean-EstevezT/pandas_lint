from pandas_lint.notebook import parse_notebook
import ast
from pandas_lint.analyzer import PandasVisitor

def debug():
    filepath = 'tests/test_notebook.ipynb'
    print(f"DEBUG: Parsing {filepath}")
    
    code, mapping = parse_notebook(filepath)
    print(f"DEBUG: Code Content:\n---\n{code}\n---")
    print(f"DEBUG: Mapping: {mapping}")
    
    tree = ast.parse(code)
    visitor = PandasVisitor()
    visitor.visit(tree)
    print(f"DEBUG: Issues found: {len(visitor.issues)}")
    for issue in visitor.issues:
        print(f" - {issue}")

if __name__ == "__main__":
    debug()
