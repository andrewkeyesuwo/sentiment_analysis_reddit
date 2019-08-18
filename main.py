import praw
import indicoio
import json
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
import re
import time
import numpy as np
import matplotlib.pyplot as plt
import requests

def main():
    indicoio.config.api_key = "150f3aff97a4936f8f0a8cd858345b9e"
    reddit = praw.Reddit(client_id='L92JRMl9lgC4sA',
                        client_secret='fBQszj5hsjw0Ji3nk-UDo5sNZGo',
                        username='hackwestern4team',
                        password='RedditSentiment',
                        user_agent='RedditSentimentV1')

    subreddit = reddit.subreddit('food')

    submission_urls = dict()
    hot_posts = subreddit.hot(limit=70)

    file_name = "text.txt"
    [submissions, submission_urls] = write_submissions(file_name, submission_urls, hot_posts)
    comments_dict = read_submissions(file_name, submissions)
    sentiment_comments = determine_comment_sentiment(submissions, submission_urls, comments_dict)
    

    object_sent = dict()
    object_occur = dict()
    object_ids = dict()
    imageObjects = dict()
    visual_recognition = VisualRecognitionV3('2016-05-20', api_key='8d7aced8efa9ce11cca985d203dce5989cc20148')

    # Determine sentiment per object identified by the watson api
    for key in submission_urls:
        list_of_classes = list()
        wholejson = (visual_recognition.classify(images_url=submission_urls[key]))
        images = (json.dumps(wholejson['images'], indent=2)).splitlines()
        print("Identifying objects in " + submission_urls[key])
        for line in images:
            if "\"class\":" in line:
                line = line.replace(",", "")
                line = line.replace("\"class\": \"", "")
                line = line.replace("\"", "")
                line = line.strip()
                list_of_classes.append(line)
                # print(line)
                if line in object_occur:
                    object_occur[line] = object_occur[line] + 1
                    object_sent[line] = object_sent[line] + sentiment_comments[key]
                    object_ids[line].append(key)
                else:
                    if sentiment_comments[key] > 0:
                        object_occur[line] = 1
                        object_sent[line] = sentiment_comments[key]
                        object_ids[line] = list()
                        object_ids[line].append(key)
        imageObjects[key] = list_of_classes

    for key in object_sent:
        object_sent[key] = object_sent[key] / object_occur[key]
        if object_occur[key] > 6:
            print("key: ", key, object_sent[key])

    # graph input x into x and y into y based on collected data
    x = list()
    y = list()

    for key in object_sent:
        if object_occur[key] > 6:
            x.append(key)
            y.append(object_sent[key])

    x = x[:-1]
    y = y[:-1]

    newx = np.asarray(x)
    newy = np.asarray(y)
    height = newy
    bars = newx
    y_pos = np.arange(len(bars))
    plt.barh(y_pos, height)
    plt.yticks(y_pos, bars)
    plt.show()

    # Suggestion Area
    while True:
        highest_of_m = ""
        while highest_of_m == "":
            print("Please enter image url:")
            marketing_image_url = input()
            wholejson = (visual_recognition.classify(images_url=marketing_image_url))
            images = (json.dumps(wholejson['images'], indent=2)).splitlines()
            list_of_classes = list()
            for line in images:
                if "\"class\":" in line:
                    line = line.replace(",", "")
                    line = line.replace("\"class\": \"", "")
                    line = line.replace("\"", "")
                    line = line.strip()
                    list_of_classes.append(line)

            maxVal = 0
            appeared_in = list()
            highest_of_m = ""
            for classs in list_of_classes:
                if classs in object_occur:
                    if object_sent[classs] > maxVal:
                        maxVal = object_sent[classs]
                        highest_of_m = classs

        appeared_in = object_ids[highest_of_m]

        maxVal = 0
        highest = ""
        for key in appeared_in:
            if sentiment_comments[key] > maxVal:
                maxVal = sentiment_comments[key]
                highest = key

        print("\nYou should add:")
        for key in imageObjects[highest]:
            if object_sent[key] > object_sent[highest_of_m] and object_sent[key]:
                print(key)
        print("\nYou should not add:")
        for key in imageObjects[highest]:
            if object_sent[key] <= object_sent[highest_of_m]:
                print(key)

def write_submissions(filename, submission_urls, hot_posts):
    file = open(filename, "w")
    submissions = list()
    counter = 0
    for submission in hot_posts:
        if not submission.stickied:
            print("Reading from: " + submission.url)
            submission_urls[str(submission)] = submission.url
            submissions.append(str(submission))
            # print("title: ", submission.title)
            comments = submission.comments.list()
            counter = 0
            for comment in comments:
                counter += 1
                if counter > 5:
                    break
                # print(comment.body)
                if hasattr(comment, 'body'):
                    comment = comment.body
                    comment = re.sub(r'[^\x00-\x7F]+', ' ', comment)
                    file.write((comment + " " + "\n"))
            file.write(str(submission))
            file.write("\n")

    file.close()
    return [submissions, submission_urls]

def read_submissions(file_name, submissions):
    f = open(file_name, "r")
    comments_dict = dict()

    for submission in submissions:
        lines = list()
        for line in f:
            line = (line.rstrip())  # for line in f_in)
            if line == submission:
                break
            if line != "":
                lines.append(line)  # list(line #for line in lines if line)
        comments_dict[submission] = lines
        # print(comments_dict[submission])

    f.close()
    return comments_dict

def determine_comment_sentiment(submissions, submission_urls, comments_dict):
    sentiment_comments = dict()
    Scounter = 0
    for submission in submissions:
        # reading the lines
        print("Finding sentiment value of " + submission_urls[submission])
        multiLine = comments_dict[str(submission)]
        total = 0
        Scounter = Scounter + 1
        counter = 0
        for line in multiLine:
            if len(line) > 125:
                line = line[0:125]
            total = total + indicoio.sentiment_hq(line)
            counter = counter + 1
        if counter != 0:
            commentSentiment = total / counter
            sentiment_comments[str(submission)] = commentSentiment
        else:
            sentiment_comments[str(submission)] = 0.5

    for key in sentiment_comments:
        print(key, sentiment_comments[key])
    return sentiment_comments

if __name__ == '__main__':
    main()