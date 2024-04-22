import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
# Load environment variables
mysql_production_database_host = os.getenv('mysql_production_database_host')
mysql_production_database_user = os.getenv('mysql_production_database_user')
mysql_production_database_password = os.getenv('mysql_production_database_password')
mysql_production_database_name = os.getenv('mysql_production_database_name')
mysql_database_host = os.getenv('mysql_database_host')
mysql_database_user = os.getenv('mysql_database_user')
mysql_database_password = os.getenv('mysql_database_password')
mysql_database_name = os.getenv('mysql_database_name')
is_production = os.getenv('is_production')
# Establish connection to the MySQL database
if is_production=="true":
    mydb = mysql.connector.connect(
        host=mysql_production_database_host,
        user=mysql_production_database_user,
        password=mysql_production_database_password,
        database=mysql_production_database_name
    )
else:
    mydb = mysql.connector.connect(
        host=mysql_database_host,
        user=mysql_database_user,
        password=mysql_database_password,
        database=mysql_database_name
    )

# Create cursor object
cursor = mydb.cursor()