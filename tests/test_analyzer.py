import ast
import pytest
from pandas_lint.analyzer import PandasVisitor


def analyze_code(code):
    tree = ast.parse(code)
    visitor = PandasVisitor()
    visitor.visit(tree)
    return visitor.issues


class TestAnalyzerIntegration:
    def test_detects_multiple_issues(self):
        code = """
import pandas as pd

df = pd.read_csv('data.csv')
for i, row in df.iterrows():
    print(row)
df['col'].apply(lambda x: x + 1)
df.to_csv('out.csv')
"""
        issues = analyze_code(code)
        codes = [i.code for i in issues]
        
        assert "MEM001" in codes
        assert "PERF001" in codes
        assert "PERF002" in codes
        assert "IO001" in codes

    def test_respects_pandas_alias(self):
        code = """
import pandas as datos

datos.read_csv('file.csv')
"""
        issues = analyze_code(code)
        codes = [i.code for i in issues]
        
        assert "MEM001" in codes

    def test_empty_file_no_issues(self):
        code = ""
        issues = analyze_code(code)
        
        assert len(issues) == 0

    def test_clean_code_no_issues(self):
        code = """
import pandas as pd

df = pd.read_csv('data.csv', usecols=['a', 'b'])
df['col'] = df['col'] + 1
df.to_parquet('out.parquet')
"""
        issues = analyze_code(code)
        
        assert len(issues) == 0

    def test_sql_injection_detected(self):
        code = """
import pandas as pd

table = "users"
df = pd.read_sql(f"SELECT * FROM {table}", conn)
"""
        issues = analyze_code(code)
        codes = [i.code for i in issues]
        
        assert "SEC001" in codes

    def test_inplace_detected(self):
        # Note: STY001 is ignored in pyproject.toml, so we test the rule directly
        from pandas_lint.rules.style import InplaceTrueRule
        rule = InplaceTrueRule()
        
        code = "df.drop('col', axis=1, inplace=True)"
        tree = ast.parse(code)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        
        issues = [rule.check(c, {}) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "STY001"


class TestAnalyzerEdgeCases:
    def test_nested_apply(self):
        code = "df.groupby('a').apply(lambda g: g.apply(lambda x: x + 1))"
        issues = analyze_code(code)
        
        assert len(issues) >= 2

    def test_chained_operations(self):
        code = "df.drop('a', axis=1).apply(lambda x: x).to_csv('out.csv')"
        issues = analyze_code(code)
        codes = [i.code for i in issues]
        
        assert "PERF002" in codes
        assert "IO001" in codes

    def test_str_accessor_suggestion(self):
        code = "df['name'].apply(lambda x: x.lower())"
        issues = analyze_code(code)
        
        assert len(issues) == 1
        assert issues[0].code == "PERF003"

    def test_dt_accessor_suggestion(self):
        code = "df['date'].apply(lambda x: x.month)"
        issues = analyze_code(code)
        
        assert len(issues) == 1
        assert issues[0].code == "PERF004"
