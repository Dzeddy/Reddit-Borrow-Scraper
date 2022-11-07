import datetime
import re
today = datetime.date.today()
print("Today's date:", today)
import praw
import pandas as pd
df = pd.DataFrame()
#set up reddit instance
reddit_read_only = praw.Reddit(client_id="Rk0kHiGTmTd5V5ZUWXevYw",  # your client id
                               client_secret="U4XF9TCluMiT0RCSjJBkHDFv_PGOjw",  # your client secret
                               user_agent="DzedScraper")  # your user agent
subreddit = reddit_read_only.subreddit("Borrow")
#search subreddit with [UNPAID] tag
for post in subreddit.search("[UNPAID]", sort="new", limit=50):
    #post format will most likely be in this format:
    #[UNPAID] (/u/aw337123) (#Lake Charles, LA, USA),) - ($145), (33 Days Late)
    #[UNPAID] (u/brenden481) (#Minneapolis, Minnesota, USA) - ($150), (2 Days Late)
    #[UNPAID] (/u/DonnieBalls) (#Warner, OK, USA),) - ($60), (3 Days Late)
    #[UNPAID] (/u/trevorvalentine) (#Portland, OR, USA)) - ($1200), (293 Days Late)
    #filter out posts that do not have [UNPAID] tag
    if "[UNPAID]" not in post.title:
        continue
    #split title into list by encased in parentheses
    title_list = re.split(r'\(|\)', post.title)
    try:
        #get username
        username = title_list[1]
        #process username to remove /u/ and any other characters
        username = username.replace("/u/", "")
        username = username.replace("u/", "")
        #information about the user
        user = reddit_read_only.redditor(username)
        #get user's comment karma
        comment_karma = user.comment_karma
        #get user's post karma
        post_karma = user.link_karma
        #get user's account age
        account_age = user.created_utc
        #get user's account age in days
        account_age = datetime.datetime.fromtimestamp(account_age)
        #we want to get the difference between the post creation date and account creation date
        #we can get the post creation date from the post object
        post_date = post.created_utc
        post_date = datetime.datetime.fromtimestamp(post_date)
        #get the difference between the post date and account creation date
        account_age = post_date - account_age
        account_age = account_age.days
        #concat user's information to dataframe using concat
        df = pd.concat([df, pd.DataFrame({'username': username, 'comment_karma': comment_karma, 'post_karma': post_karma, 'account_age_days': account_age}, index=[0])], ignore_index=True)
    except:
        continue
#save to csv
df.to_csv("UnpaidAnalysis.csv", index=False)
