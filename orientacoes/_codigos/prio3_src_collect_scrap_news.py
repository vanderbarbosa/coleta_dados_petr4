import pandas as pd
from gnews import GNews
import time
from datetime import datetime

SEARCH_TERM = 'PetroRio OR PRIO3'
# The publisher to filter by (using Google's 'site:' operator).
#PUBLISHER = 'bloomberg.com'
# Define the historical date range.
START_DATE_STR = '2015-01-01'
END_DATE_STR = '2024-12-31'
OUTPUT_CSV_FILE = 'data/raw/news_prio3_2015_2024.csv'


def create_gnews_dataset(search_query, start_date, end_date):
    """
    Fetches news articles from GNews by iterating through a date range
    month by month and saves them to a CSV file.

    Args:
        search_query (str): The search term and site filter.
        start_date (datetime): The start date of the period.
        end_date (datetime): The end date of the period.
    """
    print("Initializing GNews scraper...")

    google_news = GNews(language='pt', country='BR')

    all_results = []
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='MS')

    print(f"Starting to fetch news for query: '{search_query}'")
    print(f"Total months to process: {len(date_range)}")
    print("-" * 30)

    for i, month_start in enumerate(date_range):
        month_end = month_start + pd.offsets.MonthEnd(1)
        
        if month_end > end_date:
            month_end = end_date

        print(f"[{i+1}/{len(date_range)}] Fetching for: {month_start.strftime('%Y-%m-%d')} to {month_end.strftime('%Y-%m-%d')}")

        google_news.start_date = (month_start.year, month_start.month, month_start.day)
        google_news.end_date = (month_end.year, month_end.month, month_end.day)

        try:
            results = google_news.get_news(search_query)
            
            if results:
                print(f"  > Found {len(results)} articles this month.")
                all_results.extend(results)
            else:
                print("  > No articles found for this period.")

        except Exception as e:
            print(f"  > An error occurred: {e}")
            print("  > Skipping this month.")

        # IMPORTANT: I added a delay between requests to avoid being blocked by Google.
        time.sleep(2)

    print("-" * 30)
    print(f"Finished fetching. Total articles collected: {len(all_results)}")

    if not all_results:
        print("No data was collected. Exiting.")
        return

    # Convert the list of dictionaries to a pandas DataFrame for easy handling.
    print("Converting data to DataFrame...")
    df = pd.DataFrame(all_results)
    
    if 'publisher' in df.columns:
        df['publisher_title'] = df['publisher'].apply(lambda p: p.get('title') if isinstance(p, dict) else None)
        df['publisher_href'] = df['publisher'].apply(lambda p: p.get('href') if isinstance(p, dict) else None)
        df = df.drop(columns=['publisher'])

    print(f"Saving dataset to '{OUTPUT_CSV_FILE}'...")
    df.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8-sig')
    print("Done!")


if __name__ == '__main__':
    #full_query = f"{SEARCH_TERM} site:{PUBLISHER}"
    full_query = f"{SEARCH_TERM}"
    
    # Convert string dates to datetime objects.
    start_datetime = datetime.strptime(START_DATE_STR, '%Y-%m-%d')
    end_datetime = datetime.strptime(END_DATE_STR, '%Y-%m-%d')
    
    create_gnews_dataset(full_query, start_datetime, end_datetime)
