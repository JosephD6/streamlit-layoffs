import pandas as pd
from scraper import scrape_warn_notices, save_to_csv

def check_for_new_notices():
    existing_df = pd.read_csv('/Users/joey/Desktop/Layoffs/warn_notices.csv')
    new_df = scrape_warn_notices()
    
    combined_df = pd.concat([existing_df, new_df]).drop_duplicates(keep=False)
    
    if not combined_df.empty:
        updated_df = pd.concat([existing_df, combined_df])
        save_to_csv(updated_df, 'warn_notices.csv')
        print("New WARN notices found and added to the dataset.")
    else:
        print("No new WARN notices found.")

if __name__ == "__main__":
    check_for_new_notices()
