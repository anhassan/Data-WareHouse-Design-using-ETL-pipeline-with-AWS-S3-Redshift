import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS  staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES


staging_events_table_create= """CREATE TABLE IF NOT EXISTS staging_events ( artist text, auth text, firstName text, gender text, 
                              itemInSession int, lastName text, length numeric, level text , location text,
                              method text, page text, registration numeric , sessionId int,
                              song text, status int, ts text, userAgent text, userId text ) """





staging_songs_table_create = """CREATE TABLE IF NOT EXISTS staging_songs ( artist_id text, artist_latitude numeric ,
artist_location text, artist_longitude numeric, artist_name text, duration numeric, num_songs int ,
song_id text, title text, year int ) """


songplay_table_create = """ CREATE TABLE IF NOT EXISTS songplays ( songplay_id int identity(0,1) , start_time text , user_id text, level text, song_id text , artist_id text , session_id int , location text, user_agent text) """

user_table_create = """ CREATE TABLE IF NOT EXISTS users (user_id text, first_name text, last_name text, gender text, level text) """


song_table_create = """ CREATE TABLE IF NOT EXISTS songs (song_id text, title text, artist_id text,
year int, duration numeric ) """

artist_table_create = """ CREATE TABLE IF NOT EXISTS artists (artist_id text, name text, location text, latitude numeric, longitude numeric) """

time_table_create = """ CREATE TABLE IF NOT EXISTS time ( start_time text, hour int, day int, week int, month int, year int , weekday boolean ) """

# STAGING TABLES

staging_songs_copy = """copy staging_songs
from {} 
iam_role {}  
json 'auto' region 'us-west-2';""".format(config.get('S3','song_data'),config.get('IAM_ROLE','role_arn'))




staging_events_copy = """copy staging_events
from {}
iam_role {} 
json {} region 'us-west-2' ;
""".format(config.get('S3','log_data'),config.get('IAM_ROLE','role_arn'),config.get('S3','log_jsonpath'))

# FINAL TABLES

songplay_table_insert = """ INSERT INTO songplays (start_time,user_id,level,song_id,artist_id,session_id,location,user_agent)
SELECT distinct ts,userId,level,song_id,artist_id,sessionId,location,userAgent FROM 
staging_events JOIN staging_songs ON (staging_events.artist = staging_songs.artist_name AND staging_events.song = staging_songs.title);
"""

user_table_insert = """ INSERT INTO users(user_id,first_name,last_name,gender,level)
SELECT distinct userId,firstName,lastName,gender,level FROM staging_events;
"""
song_table_insert = """ INSERT INTO songs(song_id,title,artist_id,year,duration)
SELECT distinct song_id,title,artist_id,year,duration FROM staging_songs;
"""

artist_table_insert = """INSERT INTO artists(artist_id,name,location,latitude,longitude)
SELECT distinct artist_id,artist_name,artist_location,artist_latitude,artist_longitude FROM staging_songs;
"""

time_table_insert = """ INSERT INTO time (start_time,hour,day,week,month,year,weekday)
SELECT distinct ts , EXTRACT(HOUR FROM time_stamp) as hour,
EXTRACT( DAY FROM time_stamp )as day,
EXTRACT (WEEK FROM time_stamp) as week,
EXTRACT (MONTH FROM time_stamp) as month,
EXTRACT (YEAR FROM time_stamp) as year,
EXTRACT(DOW from time_stamp) in (6,7) as weekend from
(SELECT distinct ts , timestamp 'epoch' + CAST(ts AS BIGINT)/1000 * interval '1 second' AS time_stamp
from staging_events);
"""


# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [ songplay_table_insert,user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
