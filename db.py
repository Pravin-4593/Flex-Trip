import os
import mysql.connector
from mysql.connector import pooling

db_pool = pooling.MySQLConnectionPool(
    pool_name="flex_trip_pool",
    pool_size=5,
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_ca="ca.pem",
    ssl_verify_cert=True
)