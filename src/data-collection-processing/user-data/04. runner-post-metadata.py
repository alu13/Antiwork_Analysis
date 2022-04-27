import asyncpraw
import csv
import asyncio
import importlib as imp
import GetUserNames as scraper
import datetime
import polars as pl


async def main():

    print("Finding relevant IDs...")
    start_timestamp = datetime.date(2022,1,10).strftime("%s")
    end_timestamp = datetime.date(2022,1,17).strftime("%s")

    all_ids = "../../data/ids/all_ids.csv"
    sub_ids_path = "../../data/users/recent-post-ids.csv"


    cut_offs = pl.read_csv(all_ids).filter(
        (pl.col("created_utc") >= start_timestamp) & 
        (pl.col("created_utc") <= end_timestamp)
    )

    cut_offs.to_csv(sub_ids_path)


    print("Starting the scraping...")

    #reload scraper in case of changes
    imp.reload(scraper)

    #Instantiate the client
    client = asyncpraw.Reddit('aurimas')

    #Instantiate the class for scraping / storing user info
    collector = scraper.PostMetaDataCollector(client=client)

    #Scraping / saving parameters
    params = {
        'batch_size': 100,
        'print_every': 10,
        "save_every": 10,
        "limit": 0,
        "rescrape": False,
        "file_template": "../../data/users/recent/recent-posts-batch-{}-{}.csv"
    }

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

    

    


