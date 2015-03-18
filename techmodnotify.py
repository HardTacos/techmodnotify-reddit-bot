#!/usr/bin/env python2.7

# =============================================================================
# IMPORTS
# =============================================================================
import praw
import MySQLdb
import ConfigParser
import time
import parsedatetime.parsedatetime as pdt
import pprint
import logging
from datetime import datetime, timedelta
from requests.exceptions import HTTPError, ConnectionError, Timeout
from praw.errors import ExceptionList, APIException, InvalidCaptcha, InvalidUser, RateLimitExceeded
from socket import timeout
from pytz import timezone
from multiprocessing import Process

# =============================================================================
# GLOBALS
# =============================================================================

# Reads the config file
config = ConfigParser.ConfigParser()
config.read("techmodnotify.cfg")

# Reddit info
user_agent = ("TechModNotify bot by /u/zathegfx")
reddit = praw.Reddit(user_agent = user_agent)
USER = config.get("Reddit", "username")
PASS = config.get("Reddit", "password")

DB_HOST = config.get("SQL", "host")
DB_NAME = config.get("SQL", "db")
DB_USER = config.get("SQL", "user")
DB_PASS = config.get("SQL", "pass")
DB_TABLE = config.get("SQL", "table")

# =============================================================================
# Functions
# =============================================================================

def save_to_db(db, submissionID, permalink, author):
    """
    Saves the permalink submission, the time, and the author to the DB
    """
    cursor = db.cursor()
    
    currentTime1 = datetime.now(timezone('UTC'))
    currentTime  = format(currentTime1, '%Y-%m-%d %H:%M:%S')
    replyTime1   = currentTime1 + timedelta(0,300)
    replyTime    = format(replyTime1, '%Y-%m-%d %H:%M:%S')
    
    cmd = "SELECT * FROM " + DB_TABLE + " WHERE submissionID = %s"
    cursor.execute(cmd, [submissionID])
    results = cursor.fetchall()
    
    if (len(results) > 0):
        return True;
    else:
        cmd = "INSERT INTO " + DB_TABLE + " (submissionID, currentTime, replyTime, permalink, author) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(cmd, [submissionID, currentTime, replyTime, permalink, author])
        print currentTime + ' - Inserted new record into table: ' + submissionID

    db.commit()
    
def search_db():
    """
    Search the database for any records that are over 10 minutes
    """
    
    while True:
        
        db = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME )
        cursor = db.cursor()
    
        currentTime1 = datetime.now(timezone('UTC'))
        currentTime  = format(currentTime1, '%Y-%m-%d %H:%M:%S')
        
        cmd = "SELECT * FROM " + DB_TABLE + " WHERE replyTime < %s"
        cursor.execute(cmd, [currentTime])
        results = cursor.fetchall()
        
        alreadySent = []
        if ( len(results) > 0 ):
            for row in results:
                
                if row[0] not in alreadySent:
                    submission = reddit.get_submission(submission_id=row[1])
                    hasFlair = submission.link_flair_css_class
                    k = str(hasFlair)
                    if (k == "None"):
                        flagDelete = False
                        flagDelete = new_reply(row[4], row[5])
                        if flagDelete:
                            cmd = "DELETE FROM " + DB_TABLE + " WHERE id = %s" 
                            cursor.execute(cmd, [row[0]])
                            db.commit()
                            print currentTime + ' - No flair detected - send message - deleting record - ' + row[1]
                    else:
                        cmd = "DELETE FROM " + DB_TABLE + " WHERE id = %s" 
                        cursor.execute(cmd, [row[0]])
                        db.commit()
                        print currentTime + ' - Flair deteced - deleting record - ' + row[1]
                    alreadySent.append(row[0])
                
        time.sleep(5)

def new_reply(permalink, author):
        
        reddit.login(USER, PASS)
        try:
            
            reddit.send_message(author, 'Message from /r/technology',
            
                "Hello " + author + ","
                
                "\n\nWe appreciate your contribution to /r/technology! We noticed "
                "that you haven't flaired your [post](" + permalink + ") yet. In order to keep this sub " 
                "organized, every post is required to be flaired with respect to "
                "the articles main focus. This allows the readers of /r/technology "
                "to easily find the articles that most interest them. "
                
                "\n\n If you could take a moment out of your time to properly flair "
                "your post, we would gladly apprieciate it. Instruction on properly "
                "flairing your post can be found [here](http://www.reddit.com/r/technology/wiki/flair). "
                
                "\n\n Thank you!"
                "\n\n Techonology Mod Team"
                
                "\n\n_____\n\n"
                
                "\n\n *This is a bot - if you have any questions or need to report an issue regarding "
                "this bot, please [message the mods](https://www.reddit.com/message/compose?to=%2Fr%2Ftechnology) immediately*"
                
                "\n\n**Your Post:** " + permalink + "")
            
            print "Message Sent!"
            return True
        except InvalidUser as err:
            print "InvalidUser", err
            return True
        except APIException as err:
            print "APIException", err
            return False
        except IndexError as err:
            print "IndexError", err
            return False
        except (HTTPError, ConnectionError, Timeout, timeout) as err:
            print "HTTPError", err
            return False
        except RateLimitExceeded as err:
            print "RateLimitExceeded", err
            time.sleep(10)

def main():
    reddit.login(USER, PASS)
    db = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME )
    
    print "start"
    while True:
        try:
            for submission in praw.helpers.submission_stream(reddit, 'technology', limit=5, verbosity=0):
                
                submissionID = submission.id
                author       = submission.author
                permalink    = submission.permalink
                
                save_to_db(db, submissionID, permalink, author)
        except Exception as err:
           print  'There was an error in main(): '
           print err
# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    Process(target=main).start()
    Process(target=search_db).start()
