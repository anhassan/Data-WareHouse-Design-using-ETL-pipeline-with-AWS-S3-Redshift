import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    DWH_DB                 = config.get("DWH","DWH_DB")
    DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
    DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
    DWH_PORT               = config.get("DWH","DWH_PORT")
    DWH_ENDPOINT           = config.get("CLUSTER","DWH_ENDPOINT")
    
    try:
        conn = psycopg2.connect("host={} dbname={} user={} password={} port={}"
                                .format(DWH_ENDPOINT,DWH_DB,DWH_DB_USER,DWH_DB_PASSWORD,DWH_PORT))    
    except Exception as e:
        print(e)    
    
    cur = conn.cursor()
    print("cursor = ",cur)

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()
                            
                            


if __name__ == "__main__":
    main()