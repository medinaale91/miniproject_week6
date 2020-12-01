import mysql.connector as mysqlconn
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
nltk.download("vader_lexicon")
from dotenv import load_dotenv
import os
load_dotenv()

# We create a connection to the database "chat_project". If the database wouldn't exist, 
# we would get an error.

chat_db = mysqlconn.connect(
    host="localhost",
    user= os.getenv("SQLUSER"),
    password= os.getenv("SQLPASS"),
    database="chat_project"
)

# Inserting or updating data can be done using the handler structure known as a cursor. 
# It is importan to commit the data by using "chat_db.commit()" after a sequence of INSERT, 
# DELETE, and UPDATE statements, otherwise, no changes will be made to the table.

# We define a function named create_user() that accepts one argument: username. Inside the create_user() function,
# we construct an insert statement (sql) and execute the statement together with the data 
# (cursor.execute(sql, (username,))) for inserting it into the User table.
# We then commit the change in the try-except block. We have to explicity call the commit() method in order to make
# changes to the database. In case a new row is inserted succesfully, you can retrieve (recuperar) the last insert 
# id of the Auto_Increment column by using the lastrowid property of the MySQLCursor object. Ese id lo guardamos 
# como variable ya que es lo que devolverá la función.
# After that, we close the cursor at the end of the create_user() function.
# Finally, we call the create_user() function to insert a new row into the user table.
def create_user(username):
    try:
        cursor = chat_db.cursor()
        sql = "INSERT INTO User (username) VALUES (%s)"
        cursor.execute(sql, (username,))
        user_id = cursor.lastrowid
        chat_db.commit()
    except Exception as error:
        return error
    finally:
        cursor.close()
    return user_id

create_user("mara")

#Funcion para crear el chat y meter todos los usuarios que le pasemos. Como el chat solo tiene una propiedad que es 
# autoincrement, no necesitamos decirle ningun valor para crear un chat. Una vez creado el chat, y como la relacion 
# entre usuario y chat es N:N, tenemos una tabla intermedia llamada userchat cuya primary key es la tupla 
# Chat_id,user_id, lo cual significa que un chat puede tener varios usuarios y un usuario puede estar en más de 
# un chat. Las relaciones N:N en una base de datos relacional siempre se resuelven mediante este tipo de tabla 
# intermedia (es lo que nos genera automaticamente el diagrama al relacionar las dos tablas (User y Chat) con 
# relación N:N. 
# Una vez creado el chat, tenemos que iterar sobre la lista de users_id que nos han pasado y crear 
# la fila correspondiente en la tabla Userchat mencionada anteriormente. En caso de que alguno de los id no existiera,
# la ejecucion de la sentencia sql lanzaria una excepción porque no es capaz de satisfacer las foreign key y PK.
# De ahi que hagamos try except en este codigo.
def create_chat(list_user_id):
    try:
        cursor = chat_db.cursor()
        insert_chat_sql = "INSERT INTO Chat VALUES ()"
        cursor.execute(insert_chat_sql)
        chat_id = cursor.lastrowid
        for user_id in list_user_id:
            __add_user_to_chat_with_cursor(cursor, chat_id, user_id)
        chat_db.commit()
    except Exception as error:
        return error
    finally:
        cursor.close()
    return chat_id

# create_chat([14, 15])

# Esta funcion añade un usuario a un chat ya existente.
def add_user_to_chat(chat_id, user_id): 
    try:
        cursor = chat_db.cursor()
        __add_user_to_chat_with_cursor(cursor, chat_id, user_id)
        chat_db.commit()
    except Exception as error:
        return error
    finally:
        cursor.close()
    return chat_id

add_user_to_chat(1, 5)

# en python, las funciones privadas empiezan por __ (doble _)
# esto quiere decir que solo este fichero (sql.py) puede llamar a esta función, si intentas llamarla desde otro
# fichero que importa a este, no será visible y por tanto no se podrá utilizar desde allí
# el objetivo de estas funciones privadas es reutilizar código dentro del propio fichero
def __add_user_to_chat_with_cursor(cursor, chat_id, user_id):
    insert_user_chat_sql = "INSERT INTO UserChat (user_id, chat_id) VALUES (%s, %s)"
    cursor.execute(insert_user_chat_sql, (user_id, chat_id,))


# We define a function named add_message_to_chat() that requires 3 argument: chat_id, user_id, text.
# This function will add messages written by a user within a specific chat.
# Inserting or updating data can be done using the handler structure known as a cursor. 

# Inside this function, we construct an insert statement (insert_message_to_chat_sql) and execute the 
# statement together with the data (cursor.execute(insert_message_to_chat_sql, (chat_id, user_id, text,))) 
# for inserting it into the Message table.
# We then commit the change in the try-except block. We have to explicity call the commit() method in order to make
# changes to the database. When a new row is inserted succesfully, we retrieve (recuperamos) the last insert id of the 
# Auto_Increment column by using the lastrowid property of the MySQLCursor object.
# After that, we close the cursor at the end of the create_user() function.
# Finally, we call the add_message_to_chat() function to insert a new row into the Message table.
def add_message_to_chat(chat_id, user_id, text): 
    try: 
        cursor = chat_db.cursor()
        insert_message_to_chat_sql = "INSERT INTO Message (chat_id, user_id, text) VALUES (%s, %s, %s)"
        cursor.execute(insert_message_to_chat_sql, (chat_id, user_id, text,))
        message_id = cursor.lastrowid
        chat_db.commit()
    except Exception as error:
        return error
    finally:
        cursor.close()
    return message_id

# We create "get_chat_messages" function to gather all the messages in a chat. 
# As we need to return a json array/list of strings, we need to transform the list of tuples (i.e fetchall()) 
# into a list of strings. We do this by selecting the first element of the tuple (x[0] for x in messages)
# as we have filtered the SELECT query with just only one element (text)

def get_chat_messages(chat_id):
    cursor = chat_db.cursor()
    select_messages_from_chat = f"SELECT text FROM Message WHERE chat_id = {chat_id}"
    cursor.execute(select_messages_from_chat)
    messages = cursor.fetchall()
    return [x[0] for x in messages]


# We create sentiment function to analyze the the sentiment of each message written in a chat.
# We get all the messages by using the function "get_chat_messages" and we iterate through these messages 
# We show a list of dictionaries, each dictionary would show the text and its sentiment by using the module NLTK.
def sentiment(chat_id):
    sia = SIA()
    messages = get_chat_messages(chat_id)
    sentiments = []
    for message in messages:
        message_dict = {
            "text": message,
            "sentiment": sia.polarity_scores(message)
        }
        sentiments.append(message_dict)
    return sentiments

# We would close the connection to the database whenever we decide noone else can make any more requests 
# to post into the database or get info from the database.
#chat_db.close()



