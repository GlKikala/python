import psycopg2
from psycopg2.extras import RealDictCursor
from config import DSN
 
def get_connection():
    return psycopg2.connect(dsn=DSN)
 
def get_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)
