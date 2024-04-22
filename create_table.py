from db import mydb, cursor
def create_table():
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL
    )
    """
    cursor.execute(create_users_table_sql)

    create_model_table_sql = """
    CREATE TABLE IF NOT EXISTS model (
        id INT AUTO_INCREMENT PRIMARY KEY,
        model_name VARCHAR(50) NOT NULL
    )
    """
    cursor.execute(create_model_table_sql)

    create_chat_history_table_sql = """
    CREATE TABLE IF NOT EXISTS chat_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        model_id INT NOT NULL,
        query TEXT NOT NULL,
        answer TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (model_id) REFERENCES model(id)
    )
    """
    cursor.execute(create_chat_history_table_sql)

    mydb.commit()
create_table()