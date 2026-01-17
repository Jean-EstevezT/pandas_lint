import ast
import pytest
from pandas_lint.rules.base import RuleRegistry
from pandas_lint.rules.performance import IterrowsRule, ApplyRule
from pandas_lint.rules.memory import ReadCsvUsecolsRule
from pandas_lint.rules.security import SqlInjectionRule
from pandas_lint.rules.style import InplaceTrueRule
from pandas_lint.rules.io import ToCsvRule


def parse_and_get_calls(code):
    tree = ast.parse(code)
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            calls.append(node)
    return calls


class TestIterrowsRule:
    def setup_method(self):
        self.rule = IterrowsRule()
        self.ctx = {}

    def test_detects_iterrows(self):
        code = "for i, row in df.iterrows(): pass"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "PERF001"
        assert issues[0].severity == "CRITICAL"

    def test_ignores_other_methods(self):
        code = "df.itertuples()"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 0


class TestApplyRule:
    def setup_method(self):
        self.rule = ApplyRule()
        self.ctx = {}

    def test_detects_apply(self):
        code = "df['col'].apply(lambda x: x + 1)"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "PERF002"

    def test_detects_str_accessor_opportunity(self):
        code = "df['col'].apply(lambda x: x.upper())"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "PERF003"
        assert ".str" in issues[0].message

    def test_detects_dt_accessor_opportunity(self):
        code = "df['date'].apply(lambda x: x.year)"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "PERF004"
        assert ".dt" in issues[0].message


class TestReadCsvUsecolsRule:
    def setup_method(self):
        self.rule = ReadCsvUsecolsRule()

    def test_detects_read_csv_without_usecols(self):
        code = "pd.read_csv('file.csv')"
        calls = parse_and_get_calls(code)
        ctx = {'pandas_alias': 'pd'}
        
        issues = [self.rule.check(c, ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "MEM001"

    def test_ignores_read_csv_with_usecols(self):
        code = "pd.read_csv('file.csv', usecols=['a', 'b'])"
        calls = parse_and_get_calls(code)
        ctx = {'pandas_alias': 'pd'}
        
        issues = [self.rule.check(c, ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 0

    def test_respects_pandas_alias(self):
        code = "pandas.read_csv('file.csv')"
        calls = parse_and_get_calls(code)
        ctx = {'pandas_alias': 'pandas'}
        
        issues = [self.rule.check(c, ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1


class TestSqlInjectionRule:
    def setup_method(self):
        self.rule = SqlInjectionRule()
        self.ctx = {}

    def test_detects_fstring_in_read_sql(self):
        code = 'pd.read_sql(f"SELECT * FROM {table}", conn)'
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "SEC001"
        assert issues[0].severity == "CRITICAL"

    def test_detects_concat_in_read_sql(self):
        code = 'pd.read_sql("SELECT * FROM " + table, conn)'
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "SEC001"

    def test_ignores_safe_read_sql(self):
        code = 'pd.read_sql("SELECT * FROM users", conn)'
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 0


class TestInplaceTrueRule:
    def setup_method(self):
        self.rule = InplaceTrueRule()
        self.ctx = {}

    def test_detects_inplace_true(self):
        code = "df.drop('col', inplace=True)"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "STY001"

    def test_ignores_inplace_false(self):
        code = "df.drop('col', inplace=False)"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 0


class TestToCsvRule:
    def setup_method(self):
        self.rule = ToCsvRule()
        self.ctx = {}

    def test_detects_to_csv(self):
        code = "df.to_csv('output.csv')"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 1
        assert issues[0].code == "IO001"

    def test_ignores_to_parquet(self):
        code = "df.to_parquet('output.parquet')"
        calls = parse_and_get_calls(code)
        
        issues = [self.rule.check(c, self.ctx) for c in calls]
        issues = [i for i in issues if i]
        
        assert len(issues) == 0


class TestRuleRegistry:
    def test_all_rules_registered(self):
        rules = RuleRegistry.get_all()
        codes = [r.code for r in rules]
        
        assert "PERF001" in codes
        assert "PERF002" in codes
        assert "MEM001" in codes
        assert "SEC001" in codes
        assert "STY001" in codes
        assert "IO001" in codes

    def test_rules_have_required_attributes(self):
        for rule in RuleRegistry.get_all():
            assert hasattr(rule, 'code')
            assert hasattr(rule, 'message')
            assert hasattr(rule, 'severity')
            assert hasattr(rule, 'check')
