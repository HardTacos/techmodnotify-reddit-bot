# techmodnotify
This is a bot for [reddit](http://www.reddit.com), meant to automatically alert
a user if he / she has not flaired their submission.

This bot was created for [/r/technology](http://www.reddit.com/r/technolog)

Installation
------------

Download this repo.

Start up a mySQL server and create the following table structure:

````
+--------------+-----------------+------+-----+---------------------+-----------------------------+
| Field        | Type            | Null | Key | Default             | Extra                       |
+--------------+-----------------+------+-----+---------------------+-----------------------------+
| id           | int(6) unsigned | NO   | PRI | NULL                | auto_increment              |
| submissionID | varchar(20)     | NO   |     | NULL                |                             |
| currentTime  | timestamp       | NO   |     | CURRENT_TIMESTAMP   | on update CURRENT_TIMESTAMP |
| replyTime    | timestamp       | NO   |     | 0000-00-00 00:00:00 |                             |
| permalink    | varchar(255)    | NO   |     | NULL                |                             |
| author       | varchar(255)    | NO   |     | NULL                |                             |
+--------------+-----------------+------+-----+---------------------+-----------------------------+
````

Be sure to call the table "submissions" - at the moment, it is hard coded.

Basic usage
-----------

Change the config file to your proper credentials

Run: `python techmodnotify.py`

License
-----------
MIT