from db import mydb, cursor
# Function to seed model names into the model table
def seed_model_names(model_names):
    insert_model_sql = "INSERT INTO model (model_name) VALUES (%s)"
    for model_name in model_names:
        cursor.execute(insert_model_sql, (model_name,))
    mydb.commit()
def insert_dummy_data():
    # Dummy data for user 1 and model 1
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (1, 1, "How are you?", "I'm fine, thank you."))
    
    # Dummy data for user 1 and model 2
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (1, 2, "What's the weather like today?", "It's sunny with a chance of clouds."))
    
    # Dummy data for user 1 and model 3
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (1, 3, "Tell me a joke.", "Why don't scientists trust atoms? Because they make up everything."))

    # Dummy data for user 2 and model 1
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (2, 1, "What's your favorite color?", "My favorite color is blue."))

    # Dummy data for user 2 and model 2
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (2, 2, "Can you sing?", "I can't sing, but I can hum a tune."))

    # Dummy data for user 2 and model 3
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (2, 3, "What's the capital of France?", "The capital of France is Paris."))

    mydb.commit()



def insert_additional_dummy_data():
    # Dummy data for user 1 and model 1
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (1, 1, "What's your favorite food?", "I love pizza, especially with extra cheese."))
    
    # Dummy data for user 1 and model 2
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (1, 2, "How far is the moon?", "The average distance to the moon is about 238,855 miles."))

    # Dummy data for user 1 and model 3
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (1, 3, "What's the square root of 16?", "The square root of 16 is 4."))

    # Dummy data for user 2 and model 1
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (2, 1, "Do you like to travel?", "I would love to travel, but I'm just a virtual assistant."))

    # Dummy data for user 2 and model 2
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (2, 2, "Tell me about the solar system.", "The solar system consists of the Sun and the celestial objects that orbit it."))

    # Dummy data for user 2 and model 3
    cursor.execute("INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)",
                   (2, 3, "What's the largest mammal?", "The blue whale is the largest mammal on Earth."))

    mydb.commit()



if __name__ == "__main__":
    # Model names to insert into the model table
    model_names = ["openai", "palm2", "llama2"]

    # Seed model names into the model table
    seed_model_names(model_names)
    insert_additional_dummy_data()
    

    print("Model names seeded successfully.")
