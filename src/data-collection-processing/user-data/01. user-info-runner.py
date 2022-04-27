import asyncpraw
import csv
import asyncio
import importlib as imp
import UserScraper as scraper
from pathlib import Path


async def main():

    print("Starting the scraping...")

    #reload scraper in case of changes
    imp.reload(scraper)

    #Instantiate the client
    client = asyncpraw.Reddit('client')

    #Instantiate the class for scraping / storing user info
    collector = scraper.UserInteractionCollector(client=client)

    #Scraping / saving parameters
    params = {
        'batch_size': 20,
        'print_every': 10,
        "save_every": 100,
        "limit": 0,
        "rescrape": False,
        "file_template": "data/users/raw/user_interactions-batch-{}-{}.csv"
    }

    Path("data/users/raw").mkdir(parents=True, exist_ok=True)

    sub_ids_path = "data/ids/all_ids.csv"

    #Do the scraping!
    with open(sub_ids_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader) #skip the header
        id_reader = map(lambda x: x[1], reader) #convert into a reader of ids
        await scraper.scrape(
            collector=collector, 
            reader=id_reader, 
            **params
        )

    await client.close()

if __name__ == '__main__':
    asyncio.run(main())

    

    


