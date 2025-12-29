from click.testing import CliRunner
from pandas_lint.cli import main

def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert "version" in result.output.lower() or "0.1.0" in result.output

def test_lint_file_exists():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('test.py', 'w') as f:
            f.write("import pandas as pd\ndf.apply(lambda x: x)\n")
        
        result = runner.invoke(main, ['test.py'])
        assert result.exit_code in [0, 1]
        assert "Found" in result.output and "issues" in result.output
