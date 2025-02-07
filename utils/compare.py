import pandas as pd

# compare differences      -----------------------------------------------------------------
def compare_backend_dfs(updated_df: pd.DataFrame, original_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare two backend DataFrames (updated and original) and return a DataFrame listing differences.
    
    For each row (keyed by index) and each column in the original DataFrame,
    the function outputs:
      - the index (key),
      - the column name,
      - the original value,
      - and the updated value.
      
    An outer merge on the index is performed to handle cases where indices differ between the two DataFrames.
    
    Args:
        updated_df (pd.DataFrame): The DataFrame with updated records.
        original_df (pd.DataFrame): The original DataFrame.
    
    Returns:
        pd.DataFrame: A DataFrame with columns: 'index', 'column', 'original', 'updated'
                    for each difference found.
    """
    
    # Merge the two DataFrames on the index using an outer join.
    # Suffixes will help differentiate values coming from each DataFrame.
    merged = original_df.merge(
        updated_df,
        left_index=True,
        right_index=True,
        how='outer',
        suffixes=('_original', '_updated')
    )
    
    diff_records = []
    # Iterate over each row in the merged DataFrame.
    for idx, row in merged.iterrows():
        # Iterate over each column from the original DataFrame.
        for col in original_df.columns:
            original_val = row.get(col + "_original")
            updated_val  = row.get(col + "_updated")
            # Treat two NaN values as equal.
            if pd.isna(original_val) and pd.isna(updated_val):
                continue
            # If one value is NaN or the values differ, record the difference.
            if (pd.isna(original_val) and not pd.isna(updated_val)) or \
               (not pd.isna(original_val) and pd.isna(updated_val)) or \
               (original_val != updated_val):
                diff_records.append({
                    "uuid": idx,
                    "column": col,
                    "original": original_val,
                    "updated": updated_val
                })
    
    # Convert the list of difference records into a DataFrame.
    diff_df = pd.DataFrame(diff_records)
    diff_df = diff_df[diff_df['column'].isin(['next_payment_day', 'payment_date'])]
    return diff_df
