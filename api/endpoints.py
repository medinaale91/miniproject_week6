from flask import request
from bson import json_util
from api.app import app
from helpers.sql import *


# The URL of our api is http://127.0.0.1:5000/ or localhost:5000/
# Decorators
# To create a new user, we will insert the information as follows:
@app.route("/user/create/<username>")  #where "<username>" will be the name of the user (i.e. alejandro)
def endpoint_create_user(username):
    try:
        user_id = create_user(username)
    except Exception:
        return "User already exists", 400 
    return json_util.dumps({"user_id": user_id})
# if the request has no issues, it will return the user_id of this new user.


# Como en un llamada GET (la que es por defecto) está limitada a poder utilizar strings y query params,
# si queremos pasar una lista de usuarios (ids) en este caso, no va a funcionar.
# Necesitamos especificar que el endpoint es de tipo POST, para poder pasar un JSON
# ese JSON se mete en el body de la request, cosa que tampoco se puede hacer desde Chrome
# como veníamos haciendo hasta ahora. Necesitamos utilizar una herramienta más potente,
# por ejemplo Postman. Allí, marcamos la request de tipo POST y en el body escribimos el
# JSON necesario para hacer la request (lo que hayamos especificado nosotros en nuestra API)

@app.route("/chat/create", methods=['POST'])
def endpoint_chat_create():
    try:
        user_ids = request.json
        chat_id = create_chat(user_ids)
    except Exception:
        return "Some user doesn't exists", 400 
    return json_util.dumps({"chat_id": chat_id})
# if the request has no issues, it will return the chat_id of this new chat.


# We will insert the params as follows: /chat/adduser?chat_id=1&user_id=1
# Para añadir usuarios a chats ya existentes, podemos insertar la query escribiendo los params en la propia url o bien 
# repitiendo el proceso mencionado justo arriba por medio de Postman. En este caso debemos definir el id del chat 
# (en el cual se añadirá el nuevo usuario) y el id del nuevo usuario.

@app.route("/chat/adduser", methods=['GET', 'POST'])
def endpoint_add_user_to_chat():
    try:
        chat_id = request.args.get("chat_id")
        user_id = request.args.get("user_id")
        add_user_to_chat(chat_id, user_id)
    except Exception:
        return "Chat_id or user_id are incorrect, please review the ids", 400 
    return json_util.dumps({"chat_id": chat_id, "user_id_added": user_id})

# We will insert the params as follows: /chat/addmessage?chat_id=1&user_id=1&text=I%20hate%20you
@app.route("/chat/addmessage")
def endpoint_add_message_to_chat():
    try:
        chat_id = request.args.get("chat_id")
        user_id = request.args.get("user_id")
        text = request.args.get("text")
        message_id = add_message_to_chat(chat_id, user_id, text)
    except Exception:
        return "Chat_id or user_id are incorrect, please review the ids", 400 
    return json_util.dumps({"message_id": message_id})

# This route will return all the messages of a chat if we provide a chat_id
@app.route("/chat/list/<chat_id>")
def messages_from_chat(chat_id):
    return json_util.dumps(get_chat_messages(chat_id))

# This route will return all the messages of a chat together with the analysis of its sentiment given a chat_id.
@app.route("/chat/sentiment/<chat_id>")
def sentiment_from_chat(chat_id):
    return json_util.dumps(sentiment(chat_id))
