import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_warn_notices():
    url = "https://dol.ny.gov/warn-notices"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table')
    data = []
    headers = [header.text.strip() for header in table.find_all('th')]
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        data.append([cell.text.strip() for cell in cells])
    
    warn_notices_df = pd.DataFrame(data, columns=headers)
    return warn_notices_df

def save_to_csv(df, filename='/Users/joey/Desktop/Layoffs/warn_notices.csv'):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    df = scrape_warn_notices()
    save_to_csv(df)
