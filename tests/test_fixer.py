import pytest
from pandas_lint.fixer import fix_code


class TestAutoFixer:
    def test_fixes_str_upper(self):
        code = "df['col'].apply(lambda x: x.upper())"
        fixed = fix_code(code)
        
        assert "apply" not in fixed
        assert ".str.upper()" in fixed

    def test_fixes_str_lower(self):
        code = "df['col'].apply(lambda x: x.lower())"
        fixed = fix_code(code)
        
        assert ".str.lower()" in fixed

    def test_fixes_str_strip(self):
        code = "df['col'].apply(lambda x: x.strip())"
        fixed = fix_code(code)
        
        assert ".str.strip()" in fixed

    def test_fixes_dt_year(self):
        code = "df['date'].apply(lambda x: x.year)"
        fixed = fix_code(code)
        
        assert "apply" not in fixed
        assert ".dt.year" in fixed

    def test_fixes_dt_month(self):
        code = "df['date'].apply(lambda x: x.month)"
        fixed = fix_code(code)
        
        assert ".dt.month" in fixed

    def test_preserves_non_fixable_apply(self):
        code = "df['col'].apply(lambda x: custom_func(x))"
        fixed = fix_code(code)
        
        assert "apply" in fixed

    def test_handles_complex_code(self):
        code = """
import pandas as pd

df = pd.read_csv('data.csv')
df['upper'] = df['name'].apply(lambda x: x.upper())
df['year'] = df['date'].apply(lambda x: x.year)
result = df.groupby('cat').sum()
"""
        fixed = fix_code(code)
        
        assert ".str.upper()" in fixed
        assert ".dt.year" in fixed
        assert "groupby" in fixed
