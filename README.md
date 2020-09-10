# 
# Introduction
A music streaming startup, *Sparkify*, has grown their user base and song database and want to move their processes & data onto the cloud. Their data resides in ***S3***, in a directory of ***JSON*** logs on user activity on the app, as well as a directory with ***JSON*** metadata on the songs in their app.
This project builds an ETL pipeline that extracts data from S3 bucket, stages it in Redshift, and finally transforms it into a set of dimensional tables for the analytics team to continue finding insights.

# Infrastructure Setup

Infrastructure as Code (IaC) is used for configuration of the hardware resources for the project using `boto3`. The hardware setup revolves around two main resources which include setting up an IAM Role and spinning a Redshift cluster. An IAM Role is required to delegate permission to an AWS resource which in this case is a Redshift cluster. An IAM Role requires a trust relationship policy(JSON object) that defines which entity can assume this role and a permission policy that defines what the entity is allowed to do. In our case, the service defined in the trust relationship policy is the redshift service (`redshift.amazonaws.com`) while the permission allowed in the permission policy is the read permission from S3 bucket(`arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess`). The following diagram makes the understanding a bit more clear.

<p align="center">
  <img src="https://github.com/anhassan/Data-WareHouse-Design-using-ETL-pipeline-with-AWS-S3-Redshift/blob/master/Images/IAM.png">
</p>

Following setting up the IAM Role, a Redshift cluster needs to get setup to a host a database which would hold both the staging tables and the data warehouse. The specifications of the database and configuration details are red from `dwh.cfg` and the cluster is created.  The configuration details contain information such as the `arn`(amazon role name) for the IAM role which connects to the instance. Once the cluster is active a TCP port is opened(through a EC2 security group) for connecting traffic to the end point of the cluster. Finally the cluster end point is saved in the `dwh.cfg` file in order to connect with the database. Again the pictorial representation below brings in more clarity.

<p align="center">
  <img src="https://github.com/anhassan/Data-WareHouse-Design-using-ETL-pipeline-with-AWS-S3-Redshift/blob/master/Images/RedShift_Config.png">
</p>

The infrastructure describe above is set up running the following command
```bash
python setup_infrastructure.py
```

# Relations Creation
A total of seven tables are created in the database hosted in Redshift. The first two tables `staging_songs` & `staging_events` are the staging grounds for getting raw data dumped into tabular form from the S3 bucket. The remaining five tables form the star schema for the OLAP queries. The `songplays`(***songplay_id**, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent*) table is the fact table which contains its own primary key as `songplay_id` , foreign keys (primary keys of all the dimension tables) `artist_id`,`song_id`,`user_id` & `start_time` and bunch of other important columns. The remaining four dimension tables are `users`(  _**user_id,** first_name, last_name, gender, level_),`artists`( **artist_id**, *name, location, lattitude, longitude*),`songs`(***song_id**, title, artist_id, year, duration*) & `time`(***start_time**, hour, day, week, month, year, weekday*). 	The names of the tables along with their attributes are self explanatory about the information they hold. The primary key of each table is highlighted for clarity.
In order to create these relations the following command is used
```bash
python create_tables.py
``` 

# ETL Design
The extract part begins with extracting both the song data and log data both of which lie as objects in the S3 bucket. This data is dumped intermediately into two different staging tables `staging_songs` & `staging_events`. For copying JSON data from S3 into a Redshift table the following syntax is used
```bash
COPY <Table Name>
FROM '<S3_Bucket_URL>'
IAM_ROLE '<IAM_Role_ARN>' 
JSON 'auto' / '<JSONPATH_URL>' ;
```
There are two options while loading the JSON data into a Redshift table(`auto` or `<JSONPATH_URL>`). The `auto` argument assumes that the JSON data consists of set of objects and the names of key correspond to the column names in the table. If the key names do not match with the the column names or parsing of JSON data is required then a JSONPATH file is essential which maps JSON elements to column names of the table. For our second table `staging_events` we would be using a JSONPATH file for the reason explained above.

The diagram below brings in more clarity with regards to the architecture explained above.

<p align="center">
  <img src="https://github.com/anhassan/Data-WareHouse-Design-using-ETL-pipeline-with-AWS-S3-Redshift/blob/master/Images/S3_Redshift_ETL.png">
</p>


Once the data is loaded in the staging tables, the transform phase begins. The transformation of the data is done according to the Kimball's Bus Architecture. A star schema is used with one fact table(`songplays`) and 4 dimension tables(`users`,`artists`,`songs` & `time`) in order to make the shema is best suited for running Adhoc OLAP queries.

Finally, the data from staging tables is loaded from the staging tables into the fact and dimension tables using the following pseudo-code.
```SQL
INSERT INTO <table_name_star_schema>(<column_names>)
SELECT <column_names> FROM <table_name_staging_table>;
```
The diagram below gives a pictorial view of how this done.

<p align="center">
  <img width="719" height="700" src="https://github.com/anhassan/Data-WareHouse-Design-using-ETL-pipeline-with-AWS-S3-Redshift/blob/master/Images/ETL_Staging_StarSchema_.png">
</p>


The star schema makes sure that the data is denormalized , easy to understand and no complex joins are required to find out insights using analytical queries.

In order to extract, transform and load (ETL) use the following command.
```bash
python etl.py
```

# Resource Termination
Finally, after running the OLAP queries and completing the analysis to find out insights it is essential to free up all the allocated resources so that they might not result in extra costs. In order to do so run the following command
```bash
python delete_infrastructure.py
```
