def process_data(df):
    df['col'].str.upper()
    df['date'].dt.year

def unsafe_query(user_input):
    import pandas as pd
    
    # SEC001: F-string
    pd.read_sql(f"SELECT * FROM table WHERE id = {user_input}", "conn")
    
    # SEC001: Concatenation
    pd.read_sql("SELECT * FROM table WHERE id = " + user_input, "conn")

    # Safe usage (should not be flagged)
    pd.read_sql("SELECT * FROM table WHERE id = %s", "conn", params=[user_input])
