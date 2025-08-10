#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import csv

# ---------------------------------------------------------------------------------------------------
# Helper function to filter valid lines in source TXT files
def valid_line(line):
    line = line.strip()
    # Skip lines that start and end with '+' (borders)
    if line.startswith('+') and line.endswith('+'):
        return False
    # Skip lines that don't contain '|'
    if '|' not in line:
        return False
    return True

# ----------------------------------------------------------------------------------------------------
# Function to convert pipe-delimited text file to CSV after skipping headers/footers
def txt_to_csv(source_file, output_file, skip_first_n_lines, skip_last_n_lines=0):
    with open(source_file, 'r', encoding='utf-8') as src, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        writer = csv.writer(outfile)
        lines = src.readlines()

        # Clean and filter valid lines
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if valid_line(line):
                cleaned_lines.append(line)

        # Skip first N and last N lines
        cleaned_lines = cleaned_lines[skip_first_n_lines:]
        if skip_last_n_lines > 0:
            cleaned_lines = cleaned_lines[:-skip_last_n_lines]

        # Split each valid line by pipe and write to CSV
        for line in cleaned_lines:
            parts = [part.strip() for part in line.strip('|').split('|')]
            writer.writerow(parts)

# --------------------------------------------------------------------------------------------------
# 1) Process MUDC Inv.txt
mudc_source = r'\\inh41fp01\Digital\SAP_Autodownload\MUDC Inv.txt'
mudc_csv = r'C:\Users\te623739\Downloads\pipeline\txt_to_csv\MUDC Inv.csv'
txt_to_csv(mudc_source, mudc_csv, skip_first_n_lines=3, skip_last_n_lines=1)

# -------------------------------------------------------------------------------------------------------
# 2) Process TESOG INV.txt
tesog_source = r'\\inh41fp01\Digital\SAP_Autodownload\TESOG INV.txt'
tesog_csv = r'C:\Users\te623739\Downloads\pipeline\txt_to_csv\TESOG INV.csv'
txt_to_csv(tesog_source, tesog_csv, skip_first_n_lines=3, skip_last_n_lines=1)

# -------------------------------------------------------------------------------------------------------
# 3) Process H41 Scrap.txt
h41_source = r'\\inh41fp01\Digital\SAP_Autodownload\H41 Scrap.txt'
h41_csv = r'C:\Users\te623739\Downloads\pipeline\txt_to_csv\H41 Scrap.csv'
txt_to_csv(h41_source, h41_csv, skip_first_n_lines=3, skip_last_n_lines=1)

# Load and clean H41 Scrap data
df_h41 = pd.read_csv(h41_csv, dtype=str)
df_h41.iloc[:, 0] = df_h41.iloc[:, 0].str.strip()
df_h41 = df_h41[~df_h41.iloc[:, 0].str.startswith('Material', na=False)]

# Clean H41 Scrap fields
df_h41['Inv Value'] = df_h41['Inv Value'].astype(str).str.replace(',', '').str.strip()
df_h41['Inv Value'] = pd.to_numeric(df_h41['Inv Value'], errors='coerce')

df_h41.to_csv(h41_csv, index=False)

  
# ----------------------------------------------------------------------------------------------------
# 4) Process H41 no Scrap.txt
h41_no_scrap_source = r'\\inh41fp01\Digital\SAP_Autodownload\H41 no Scrap.txt'
h41_no_scrap_csv = r'C:\Users\te623739\Downloads\pipeline\txt_to_csv\H41 no Scrap.csv'
excel_path = r'C:\Users\te623739\Downloads\pipeline\main\Stock.xlsx'

txt_to_csv(h41_no_scrap_source, h41_no_scrap_csv, skip_first_n_lines=8, skip_last_n_lines=1)

# Load and clean H41 no Scrap data
df_no_scrap = pd.read_csv(h41_no_scrap_csv, dtype=str)
df_no_scrap.iloc[:, 0] = df_no_scrap.iloc[:, 0].str.strip()
df_no_scrap = df_no_scrap[~df_no_scrap.iloc[:, 0].str.startswith('Plant', na=False)]
df_no_scrap['Total Valu'] = df_no_scrap['Total Valu'].astype(str).str.replace(',', '').str.strip()
df_no_scrap['Total Valu'] = pd.to_numeric(df_no_scrap['Total Valu'], errors='coerce')
df_no_scrap['Material'] = df_no_scrap['Material'].astype(str).str.strip().str.lstrip('0')
df_no_scrap['Storage Bi'] = df_no_scrap['Storage Bi'].astype(str).str.strip()

# --- 1️⃣: PLANT TYPE MAPPING via 'Location Master' Sheet ---
location_df = pd.read_excel(excel_path, sheet_name='Location master', dtype=str)
location_df['Storage bin'] = location_df['Storage bin'].astype(str).str.strip()
location_df['Plant'] = location_df['Plant'].astype(str).str.strip()

# Merge to get 'plant type'
df_no_scrap = df_no_scrap.merge(location_df[['Storage bin', 'Plant']],
                                how='left',
                                left_on='Storage Bi',
                                right_on='Storage bin')

df_no_scrap.rename(columns={'Plant': 'plt type'}, inplace=True)
df_no_scrap.drop(columns=['Storage bin'], inplace=True)

# --- 2️⃣: MATERIAL TYPE MAPPING via 'Classification Master' Sheet ---
df_excel = pd.read_excel(excel_path, sheet_name='Classification Master', header=1, dtype=str)
df_excel['TE PN'] = df_excel['TE PN'].astype(str).str.strip().str.lstrip('0')
df_excel['Classification'] = df_excel['Classification'].astype(str).str.strip()

df_no_scrap = df_no_scrap.merge(df_excel[['TE PN', 'Classification']],
                                how='left',
                                left_on='Material',
                                right_on='TE PN')

df_no_scrap['mat type'] = df_no_scrap['Classification']
df_no_scrap.drop(columns=['TE PN', 'Classification'], inplace=True)

# --- SAVE CLEANED AND MERGED FILE ---
df_no_scrap.to_csv(h41_no_scrap_csv, index=False)

# --- 3️⃣: LOAD FINAL FOR AGGREGATION ---
df_final = pd.read_csv(h41_no_scrap_csv, dtype=str)
df_final['mat type'] = df_final['mat type'].astype(str).str.strip()
df_final['Total Valu'] = df_final['Total Valu'].astype(str).str.replace(',', '').str.strip()
df_final['Total Valu'] = pd.to_numeric(df_final['Total Valu'], errors='coerce')
df_final['Plant_y'] = df_final['Plant_y'].astype(str).str.strip()
###########################################
# Strip only the specified column names (without changing case)
columns_to_process = ['Storage Lo', 'Storage Ty', 'Storage Bi', 'Stock Cat.']

# Strip and lowercase values only in the specified columns
for col in columns_to_process:
    if col in df_final.columns:
        df_final[col] = df_final[col].apply(lambda x: str(x).strip().lower() if pd.notnull(x) else x)

# Apply transformation logic
def update_storage_lo(row):
    storage_ty = row.get('Storage Ty', '')
    storage_bi = row.get('Storage Bi', '')
    stock_cat = row.get('Stock Cat.', '')

    if storage_ty == 'v02' or storage_bi in ['rejn', 'store use'] or stock_cat == 's':
        return None
    elif storage_ty == '151' or storage_ty.startswith('v'):
        return 'shop'
    return 'main'

if all(col in df_final.columns for col in ['Storage Lo', 'Storage Ty', 'Storage Bi', 'Stock Cat.']):
    df_final['Storage Lo'] = df_final.apply(update_storage_lo, axis=1)


df_final.to_csv(h41_no_scrap_csv, index=False)







# ---------------------------------------------------------------------------------------------------

