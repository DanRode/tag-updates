import pandas as pd

def main():
    # Load Catalog.xlsx
    catalog_df = pd.read_excel('Catalog.xlsx', engine='openpyxl')
    print('Catalog.xlsx columns:', catalog_df.columns.tolist())
    # Ensure columns: 'SalesForce Id', 'CatalogName' (case-insensitive)
    catalog_df.columns = [col.strip().lower() for col in catalog_df.columns]
    catalog_map = dict(zip(catalog_df['salesforce id'].astype(str).str.lower(), catalog_df['catalog name'].astype(str)))

    # Load Flexera.csv
    flexera_df = pd.read_csv('Flexera.csv')
    flexera_df.columns = [col.strip().lower() for col in flexera_df.columns]

    # Prepare output rows
    output_rows = []
    for _, row in flexera_df.iterrows():
        sfid = str(row['catalogid']).lower()
        flexera_name = str(row['catalogname'])
        correct_name = catalog_map.get(sfid)
        if correct_name and flexera_name.lower() != correct_name.lower():
            output_rows.append({
                'Cloud Vendor': row.get('cloud vendor', ''),
                'Cloud Vendor Account Name': row.get('cloud vendor account name', ''),
                'Salesforce Id': row['catalogid'],
                'CatalogName': flexera_name,
                'Correct CatalogName': correct_name
            })

    # Write output CSV
    out_df = pd.DataFrame(output_rows)
    out_df.to_csv('CatalogName_Mismatches.csv', index=False)
    print(f"Done. {len(output_rows)} mismatches written to CatalogName_Mismatches.csv")

if __name__ == "__main__":
    main()
