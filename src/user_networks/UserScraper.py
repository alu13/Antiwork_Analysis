import asyncio
from collections import defaultdict
from datetime import date
from datetime import datetime
import json
import itertools as itt
import pandas as pd
from pathlib import Path
import re

class UserInteractionCollector:

    def __init__(self, client):
        self.client = client
        self.reset_users()        

    def reset_users(self):
        self.users = defaultdict(lambda: {
            "no_posts": 0, 
            "no_comments": 0, 
            "post_karma": 0,     
            "comment_karma": 0,
            "directs": defaultdict(int),
            "indirects": defaultdict(int),
            "first_date": date(2022,2,20),
            "last_date":  date(1999,1,1),
            "user_name": ""
        })
        self.users['__SKIP__']['user_name'] = "__SKIP__"

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
        
        def update_last_seen(user, date):
            '''Updates user first and last date attributes based on observed activity date'''
            if user['first_date'] > date:
                user['first_date'] = date            

            if user['last_date'] < date:
                user['last_date'] = date

        def parse_op_data(post, thread_participants, parents):
            '''Parses post author information'''
            
            if (post.author is not None) and (hasattr(post.author, 'name')): #happens when the user is deleted/suspended                
            #include post statistics & date attributes for the author    
                op = self.users[post.author.name]
                op['user_name'] = post.author.name
                op['no_posts'] += 1
                op['post_karma'] += post.score
                update_last_seen(op, date.fromtimestamp(post.created_utc))
                
                #add to participant list
                thread_participants.add(post.author.name)
            
                #add op to the parent id list    
                parents[post.id] = post.author.name
            else:
                #record a missing user
                self.users['__SKIP__']['no_posts'] += 1
        
        async def parse_comments(post, thread_participants, parents):
            '''Parses all comments of a post'''
            
            #fetch comments            
            await post.comments.replace_more(limit=None)            

            #iterate through comments
            for comment in post.comments.list():        

                #include comment statistics & date attributes for the author
                if (comment.author is not None) and (hasattr(comment.author, 'name')):
                    user = self.users[comment.author.name]
                    user['user_name'] = comment.author.name
                    user['no_comments'] += 1
                    user['comment_karma'] += comment.score
                    update_last_seen(user, date.fromtimestamp(comment.created_utc))
                
                    #add to participant list
                    thread_participants.add(comment.author.name)
            
                    #add user to the parent id list
                    parents[comment.id] = comment.author.name
                
                    #find who is the author of the parent
                    real_parent_id = comment.parent_id[3:] #first two symbols is an artificial prefix
                    parent_user_name = parents[real_parent_id]                
                    
                    #save evidence of direct iteraction
                    if parent_user_name is not None:
                        self.users[comment.author.name]['directs'][parent_user_name] += 1
                        self.users[parent_user_name]['directs'][comment.author.name] += 1
    
        thread_participants = set() #a set of all thread participants
        parents = defaultdict(lambda: None) #lookup table for author of each parent thread (to track direct interactions)

        parse_op_data(post, thread_participants, parents)
        await parse_comments(post, thread_participants, parents)
            
        #add all indirect interactions
        for person in thread_participants:
            others = thread_participants.difference(set([person]))
            for other_person in others:
                self.users[person]['indirects'][other_person] += 1


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

            #Save current information and reset users array
            if ((i + 1) % save_every == 0):
                
                #diagnostic information
                print("Saving after batch #{}".format(i))
                no_posts = sum([u['no_posts'] for u in collector.users.values()])
                no_users = len(collector.users)
                no_direct_interactions = sum([sum(u['directs'].values()) for u in collector.users.values()])
                print(" -- Number of posts found: {:d}".format(no_posts))
                print(" -- Number of users found: {:d}".format(no_users))
                print(" -- Total direct interactions found: {:d}".format(no_direct_interactions))            

                #save the dataframe
                if (len(collector.users) > 0): 
                    df = pd.DataFrame(list(collector.users.values()))
                    df['directs'] = df['directs'].apply(json.dumps)
                    df['indirects'] = df['indirects'].apply(json.dumps)
                    filename = file_template.format(batch_size, i)
                    df.to_csv(filename, index=False)
                else:
                    print(" ** Not saved - empty dataframe ** ")
                
                print("")

                #reset users
                collector.reset_users()

            
            #Break if limit was reached
            if i == (limit + max_seen_i - 1):
                print("Exiting after batch #{}".format(i))
                break
        
        #for debugging only
        elif i % print_every == 0:
                print("Skipping batch #{}".format(i))

    