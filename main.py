from datetime import datetime
from fastapi import FastAPI, HTTPException
import os
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv
from bson import ObjectId

from models.models import ChatHistory, ChatInbox, ChatRecipient, Message, SendMessage, UserLogin, UserRegistration, ChatInfo
from utils.utils import get_chat_id_info, get_or_create_chat_id, translate_message

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv('MONGO_URI')

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['chat_lingo']

authentication_collection: Collection = db['chat_authentication']
inbox_collection = db['chat_inbox']
messages_collection = db['chat_messages']



@app.get("/")
async def read_root():
    return {"Status": "API is running"}


# Register a new user
@app.post("/register")
def register_user(user: UserRegistration):
    existing_user = authentication_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user.model_dump()
    authentication_collection.insert_one(user_data)
    return {
        "full_name": user_data["full_name"],
        "language_choice": user_data["language_choice"],
        "email": user_data["email"]
    }

# User login
@app.post("/login")
def login_user(user: UserLogin):
    existing_user = authentication_collection.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Please register first")

    if existing_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {
        "full_name": existing_user["full_name"],
        "language_choice": existing_user["language_choice"],
        "email": existing_user["email"]
    }
    
    
@app.post("/add_user")
async def add_user(chat_inbox: ChatRecipient):
    email_exist = authentication_collection.find_one({"email": chat_inbox.user_email})
    if not email_exist :
        raise HTTPException(status_code=401, detail="User not found!")
    
    user_name = authentication_collection.find_one({"email": chat_inbox.user_email})
    chat_id = get_or_create_chat_id(chat_inbox.adder_email, chat_inbox.adder_name, chat_inbox.user_email, user_name["full_name"], inbox_collection)
    return {
        "chat_id": chat_id,
        "name": user_name["full_name"]
    }

@app.get("/get_chat_info")
async def get_chat_info(adder_email: str):
    chat_info = get_chat_id_info(inbox_collection, adder_email)
    return {"chat_info": chat_info}

@app.post('/chat')
async def get_chat_recipient(chat_info: ChatInfo):
    chat = inbox_collection.find_one({"chat_id": chat_info.chat_id})
    
    if chat["adder_email"] == chat_info.adder_email:
        return {
            "user_name": chat["user_name"],
            "user_email": chat["user_email"]
        }
    else:
        return {
            "user_name": chat["adder_name"],
            "user_email": chat["adder_email"]
        }
    


@app.post("/send_message")
async def send_message(msg: SendMessage):
    user = authentication_collection.find_one({"email": msg.receiver_email})
    translated_language = user["language_choice"]
    translated_text = translate_message(msg.original_text, msg.original_language, translated_language)
    
    new_message = Message(
        chat_id=msg.chat_id,
        sender_email=msg.sender_email,
        receiver_email=msg.receiver_email,
        original_text=msg.original_text,
        original_language=msg.original_language,
        translated_text=translated_text,
        translated_language=translated_language,
        timestamp=datetime.now().isoformat()
    )

    messages_collection.insert_one(new_message.model_dump())
    
    return {
        "message": "Message sent successfully"
    }


@app.get('/chat_history')
async def get_chat_history(chat_id: str, email: str, lang_choice: str):
    messages = messages_collection.find({'chat_id': chat_id})
    
    chat_history = []
    for message in messages:
        
        if lang_choice == message['original_language']:
            text = message['original_text']
        else:
            text = message['translated_text']

        selective_message = {
            'chat_id': message['chat_id'],
            'sender_email': message['sender_email'],
            'receiver_email': message['receiver_email'],
            'text': text,
            'timestamp': message['timestamp']
        }
        
        chat_history.append(selective_message)
    
    return chat_history