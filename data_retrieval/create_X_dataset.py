"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Create X dataset
"""
import pandas as pd
from utils import *


def merge_csv_files(file1, file2, m1_m2_data, ppi_data, output_file):
    """
    Merges multiple CSV files, processes missing values, adds composite indicators,
    and saves the final dataset to a new CSV file.

    Parameters:
    file1 (str): Path to the first CSV file.
    file2 (str): Path to the second CSV file.
    m1_m2_data (str): Path to the M1/M2 data CSV file.
    ppi_data (str): Path to the PPI data CSV file.
    output_file (str): Path to save the merged and processed CSV file.

    Returns:
    pd.DataFrame: The merged and processed DataFrame.
    """

    # Load both CSV files
    df1 = pd.read_csv(file1, index_col=0)
    df1.index = pd.to_datetime(df1.index, errors='coerce')
    df2 = pd.read_csv(file2, index_col=0, encoding='gbk')
    df2.index = pd.to_datetime(df2.index, errors='coerce')

    df3 = pd.read_csv(m1_m2_data, index_col=0)
    df3.index = pd.to_datetime(df3.index, errors='coerce')
    df4 = pd.read_csv(ppi_data, index_col=0, encoding='gbk')
    df4.index = pd.to_datetime(df4.index, errors='coerce')

    # Merge dataframes on index
    merged_df = pd.concat([df1, df2, df3, df4])
    merged_df.sort_index(inplace=True)
    merged_df.dropna(how='all', inplace=True)
    # Forward fill, then backward fill to handle missing values
    merged_df.fillna(method='ffill', inplace=True)
    merged_df.fillna(method='bfill', inplace=True)

    merged_df = merged_df.resample('ME').last()

    # Rename the column
    if "贷款市场报价利率(LPR):1年" in merged_df.columns:
        merged_df.rename(columns={"贷款市场报价利率(LPR):1年": "中国:贷款市场报价利率(LPR):1年"}, inplace=True)

    # add composite indicators
    merged_df = add_taylor_indicator(merged_df)
    merged_df = add_short_long_bond_spread(merged_df)
    columns_to_remove = ['China_Unemployment_Rate', 'Potential_GDP']
    merged_df = merged_df.drop(columns=columns_to_remove)

    # Save to new CSV file
    merged_df.to_csv(output_file, encoding='utf-8')
    return merged_df


# Example usage
if __name__ == '__main__':
    df = merge_csv_files('data/X_data_Fred.csv', 'data/X_data_iFind.csv',
                         'data/M1_M2_data.csv', 'data/ppi_data.csv',
                         'data/XY_aug_feat.csv')
    print(f"Data Merged")
    print(df.columns)
