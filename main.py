import numpy as np
import datetime
import re
today = datetime.date.today()
print("Today's date:", today)
import praw
import pandas as pd
df = pd.DataFrame()
reddit_read_only = praw.Reddit(client_id="",  # your client id
                               client_secret="",  # your client secret
                               user_agent="")  # your user agent

subreddit = reddit_read_only.subreddit("Borrow")

# Display the name of the Subreddit
#print("Display Name:", subreddit.display_name)

# Display the title of the Subreddit
#print("Title:", subreddit.title)

# Display the description of the Subreddit
#print("Description:", subreddit.description)
subreddit = reddit_read_only.subreddit("Borrow")
#7725.574 -> mean comment karma 17744.45 -> SD comment karma
#4768.608 -> mean post karma 16702.797 -> standard deviation of post karma
#1484.892 -> mean account age 1066.547 -> sd account age
mean_unpaid_comment_karma = 17744.45
sd_unpaid_comment_karma = 7725.574
mean_unpaid_post_karma = 16702.797
sd_unpaid_post_karma = 4768.608
mean_unpaid_account_age = 1066.547
sd_unpaid_account_age = 1484.892
for post in subreddit.new(limit=50):
    print(post.title)
    #title will be in format [REQ] ($200)-(#Navotas, Manila, Philippines), (Repay 220), (11/15/2022), (Paypal)
    #[REQ] ($150) - (#Providence, RI, USA) (repay $170 by 8/6/21) (PayPal, Venmo, Cashapp, Apple Pay)
    #[REQ] ($50) (#Laurinburg, NC, USA) (Repay $60 on 11/10) (Cashapp)
    #we want to extract the loan amount, repay amount, date, and see if it's paypal
    #we also want to skip posts that are marked as [paid]
    #first, we want to split the title into a list, split into items which are encased by parentheses
    title = post.title
    if "[PAID]" in post.title:
        continue

    #split title into list by encased in parentheses
    title_list = re.split(r'\(|\)', title)
    print(title_list)
    #search for paypal in list
    paypal = False
    for item in title_list:
        if "paypal" in item.lower():
            paypal = True
            break
    if paypal == False:
        continue
    #loan amount is the first item containing a dollar sign
    loan_amount = 0
    for item in title_list:
        if "$" in item:
            loan_amount = item
            break
    #repay amount is the first item containing a dollar sign after the loan amount, or the second number in the title, or any number after the word "repay"
    repay_amount = 0
    for item in title_list:
        if "$" in item and item != loan_amount:
            repay_amount = item
            repay_amount_list = re.split(r'\D+', repay_amount)
            for number in repay_amount_list:
                try:
                    if int(number) > int(loan_amount.strip("$")):
                        repay_amount = number
                        break
                except:
                    continue
            break
    #check if repay amount is 0, if so, it should contain the word "repay"
    if repay_amount == 0:
        for item in title_list:
            if "repay" in item.lower():
                repay_amount = item
                #split item into list of numbers and take first number greater than loan amount
                repay_amount_list = re.split(r'\D+', repay_amount)
                for number in repay_amount_list:
                    try:
                        if int(number) > int(loan_amount.strip("$")):
                            repay_amount = number
                            break
                    except:
                        continue
                break

    print(loan_amount)
    print(repay_amount)
    #calculate percentage of loan amount
    try:
        percentage = int(repay_amount) / int(loan_amount.strip("$"))
    except:
        continue
    print(loan_amount)
    print(repay_amount)
    print(percentage)
    #gather info about reddit account
    #get username
    username = post.author
    #get account age
    account_age = post.author.created_utc
    #in a unix timestamp, so we need to convert to datetime
    account_age = datetime.datetime.fromtimestamp(account_age)
    #find the difference between today and account age
    account_age = today - account_age.date()
    #save it as number of days
    account_age = account_age.days
    #get karma
    karma = post.author.link_karma + post.author.comment_karma
    #post title
    post_title = post.title
    #calculate statistical likelihood of loan being repaid
    #we want to calculate the probability of the loan being repaid based on the account age, karma, and percentage of loan amount
    #we will use a normal distribution to calculate the probability of the account age, karma, and percentage of loan amount
    #we will then multiply the probabilities together to get the overall probability of the loan being repaid
    #we will then compare this probability to the probability of the loan being repaid for paid loans
    #we will then use this to determine if the loan is likely to be repaid

    #calculate probability of account age
    #we will use the mean and standard deviation of account age for unpaid loans. note we are only interested in the right side
    #calculate what percent of the distribution is to the right of the comment karma
    #we will use the cumulative distribution function

    commentkarmapercentile = 1 - (1 / (1 + np.exp(-((post.author.comment_karma - mean_unpaid_comment_karma) / sd_unpaid_comment_karma))))
    print("comment karma percentile:", commentkarmapercentile)
    #calculate probability of post karma
    #we will use the mean and standard deviation of post karma for unpaid loans. note we are only interested in the right side
    #calculate what percent of the distribution is to the right of the comment karma
    #we will use the cumulative distribution function
    postkarmapercentile = 1 - (1 / (1 + np.exp(-((post.author.link_karma - mean_unpaid_post_karma) / sd_unpaid_post_karma))))
    print("post karma percentile:", postkarmapercentile)
    #calculate probability of account age
    #we will use the mean and standard deviation of account age for unpaid loans. note we are only interested in the right side
    #calculate what percent of the distribution is to the right of the account's age
    #we will use the cumulative distribution function
    accountagepercentile = 1 - (1 / (1 + np.exp(-((account_age - mean_unpaid_account_age) / sd_unpaid_account_age))))
    print("account age percentile:", accountagepercentile)
    #calculate what percentile of unpaid
    compositepercentile = (commentkarmapercentile + postkarmapercentile + accountagepercentile) / 3
    #save to dataframe with concat
    df = pd.concat([df, pd.DataFrame({'username': username, 'account_age': account_age, 'karma': karma, 'loan_amount': loan_amount, 'repay_amount': repay_amount, 'percentage': percentage, 'composite_percentile': compositepercentile, 'post_title': post_title}, index=[0])], ignore_index=True)
#save to csv
df.to_csv("interest_rates.csv")



