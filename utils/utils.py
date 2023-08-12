import secrets
from pymongo.collection import Collection
from typing import List, Dict
from models.models import ChatInbox
from translate import Translator

def translate_message(message, source_lang, target_lang):
    translator = Translator(from_lang=source_lang, to_lang=target_lang)
    translated_text = translator.translate(message)
    return translated_text


def generate_unique_chat_id(inbox_collection):
    while True:
        chat_id = secrets.token_hex(16)
        existing_user = inbox_collection.find_one({"chat_id": chat_id})
        if not existing_user:
            return chat_id

def get_or_create_chat_id(adder_email, adder_name, user_email, user_name, inbox_collection):
    existing_user = inbox_collection.find_one({
        "$or": [{"adder_email": adder_email, "user_email": user_email},
                {"adder_email": user_email, "user_email": adder_email}]
    })

    if existing_user:
        return existing_user["chat_id"]
    else:
        chat_id = generate_unique_chat_id(inbox_collection)
        inbox_collection.insert_one({
            "adder_email": adder_email,
            "adder_name": adder_name,
            "user_email": user_email,
            "user_name": user_name,
            "chat_id": chat_id
        })
        return chat_id

    
    
def get_chat_id_info(inbox_collection: Collection[ChatInbox], adder_email: str) -> List[Dict[str, str]]:
    chat_info_list = []

    for user in inbox_collection.find({"$or": [{"adder_email": adder_email}, {"user_email": adder_email}]}):
        if user["adder_email"] == adder_email:
            chat_info = {
                "email": user["user_email"],
                "name": user["user_name"],
                "chat_id": user["chat_id"]
            }
        else:
            chat_info = {
                "email": user["adder_email"],
                "name": user["adder_name"],
                "chat_id": user["chat_id"]
            }
        chat_info_list.append(chat_info)

    return chat_info_list


    
