import json
from typing import List, Dict, Tuple, Optional

def parse_notebook(filepath: str) -> Tuple[str, Dict[int, int]]:
    """
    Parses a Jupyter Notebook (.ipynb) and extracts code from code cells.
    
    Args:
        filepath: Path to the .ipynb file.

    Returns:
        A tuple containing:
        - The concatenated code source as a single string.
        - A mapping dictionary where keys are line numbers in the concatenated source
          and values are the original cell indices.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise ValueError(f"Failed to read notebook {filepath}: {e}")

    cell_mapping: Dict[int, int] = {} 
    
    current_line = 1
    final_code_parts = []
    
    for i, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') != 'code':
            continue
            
        source_content = cell.get('source', [])
        if isinstance(source_content, list):
            source = "".join(source_content)
        else:
            source = str(source_content)
            
        if not source.endswith('\n'):
            source += '\n'
            
        final_code_parts.append(source)
        
        line_count = source.count('\n')
        
        for line_offset in range(line_count):
            cell_mapping[current_line + line_offset] = i
            
        current_line += line_count
        
        final_code_parts.append('\n')
        current_line += 1
            
    return "".join(final_code_parts), cell_mapping
