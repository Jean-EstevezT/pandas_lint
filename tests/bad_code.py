import pandas as pd
import numpy as np

def process_data():
    # MEM001: Massive load without filtering columns
    df = pd.read_csv("big_data.csv") 
    
    # PERF001: Iterrows is the devil
    for index, row in df.iterrows():
        print(row['column_a'] * 2)

    # PERF002: Apply when you could vectorize
    df['new_col'] = df['col_b'].apply(lambda x: x + 10)

    return df