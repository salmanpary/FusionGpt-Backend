from db import mydb, cursor
# Function to seed model names into the model table
def seed_model_names(model_names):
    insert_model_sql = "INSERT INTO model (model_name) VALUES (%s)"
    for model_name in model_names:
        cursor.execute(insert_model_sql, (model_name,))
    mydb.commit()

if __name__ == "__main__":
    # Model names to insert into the model table
    model_names = ["openai", "palm2", "llama2"]

    # Seed model names into the model table
    seed_model_names(model_names)

    print("Model names seeded successfully.")
