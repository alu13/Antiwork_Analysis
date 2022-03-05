import asyncio
from collections import defaultdict
from datetime import date
from datetime import datetime
import json
import itertools as itt
import pandas as pd
from pathlib import Path
import re

class PostMetaDataCollector:

    def __init__(self, client):
        self.client = client
        self.reset_posts()        

    def reset_posts(self):
        self.posts = defaultdict(lambda: {
            "post_id": "",             
            "post_karma": 0,                 
            "user_name": "",
            "num_comments": 0
        })        

    async def async_process_posts(self, ids):      
      await asyncio.gather(*[self.process_submission(id) for id in ids])    

    async def process_submission(self, id):
        try:
            post = await self.client.submission(id=id)                        
            await self.save_submission_details(post)            
                        
        except:
            print("Submission id {} failed (exception occured)".format(id))

    async def save_submission_details(self, post):
        '''Saves given submission user interaction details into the users dictionary'''
        
        if (post.author is not None) and (hasattr(post.author, 'name')): 
            #happens when the user is deleted/suspended                
            #include post statistics & date attributes for the author    
            p = self.posts[post.id]            
            p['user_name'] = post.author.name            
            p['post_karma'] += post.score
            p['post_id'] = post.id
            p['num_comments'] = post.num_comments


#Function to do the scraping
async def scrape(
        collector, reader, file_template,
        batch_size = 10, 
        print_every = 10, save_every = 100, 
        limit = 0, rescrape=False, 
    ):
    '''Scrapes user information required
    @Collector - UserInteractionCollector object
    @reader - iterable of submission ids
    @params - dictionary defining batch size, print and save frequency
    @file_save_path - template for saving interim results
    @limit - max number of batches to collect
    @overwrite - whether to rescrape data in existing files 
    '''

    def grouper(iterable, n, fillvalue=None):
        '''Helper function that produces batches of size n'''
        args = [iter(iterable)] * n
        return itt.zip_longest(*args, fillvalue=fillvalue)

    max_seen_i = 0   

    #check if there are files saved already and prepare to skip them
    if rescrape is False:
        search_template = file_template.format(batch_size, "*")    
        p = re.compile("([0-9]+)\.csv")
        for path in Path(".").glob(search_template):
            found_id = int(p.findall(path.name)[0])
            max_seen_i = max(found_id, max_seen_i)

        print("MAX ID found: {}".format(max_seen_i))
        
        if max_seen_i > 0:
            max_seen_i += 1
            skip_records = (max_seen_i) * batch_size
            print("Found existing batch files up to batch #{} ({} records)".format(max_seen_i, skip_records))     

    for i, batch in enumerate(grouper(reader, batch_size)):
        
        if i >= max_seen_i: #skip otherwise

            #Print progress             
            if i % print_every == 0:
                print("[{}] Processing batch #{}".format(datetime.now(), i))

            #Do the scraping at batch sizes
            await collector.async_process_posts(batch)

            #Check if there's an issue with rate limits
            if collector.client.auth.limits['remaining'] <= 0:
                    cooldown = datetime.fromtimestamp(collector.client.auth.limits['reset_timestamp']) - datetime.now()
                    print("Rate limit reached; pausing for {:.1f} minutes".format(cooldown.seconds / 60))                    

            #Save current information and reset posts array
            if ((i + 1) % save_every == 0):
                
                #diagnostic information
                print("Saving after batch #{}".format(i))                

                #save the dataframe
                if (len(collector.posts) > 0): 
                    df = pd.DataFrame(list(collector.posts.values()))                    
                    filename = file_template.format(batch_size, i)
                    df.to_csv(filename, index=False)
                    del df
                else:
                    print(" ** Not saved - empty dataframe ** ")
                
                print("")

                #reset users
                collector.reset_posts()
            
            #Break if limit was reached
            if i == (limit + max_seen_i - 1):
                print("Exiting after batch #{}".format(i))
                break
        
        #for debugging only
        elif i % print_every == 0:
                print("Skipping batch #{}".format(i))

    