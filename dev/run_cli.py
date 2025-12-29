import sys
import os


sys.path.insert(0, os.getcwd())

import pandas_lint
print(f"DEBUG: pandas_lint location: {pandas_lint.__file__}")

from pandas_lint.cli import main
if __name__ == '__main__':
    main()
