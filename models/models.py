from pydantic import BaseModel

# Model for registration
class UserRegistration(BaseModel):
    full_name: str
    language_choice: str
    email: str
    password: str

# Model for login
class UserLogin(BaseModel):
    email: str
    password: str
    
# Model for inbox
class ChatRecipient(BaseModel):
    adder_email: str
    adder_name: str
    user_email: str
    
# Model for inbox
class ChatInbox(BaseModel):
    adder_email: str
    adder_name: str
    user_email: str
    user_name: str
    
# Model for getting whom to message
class ChatInfo(BaseModel):
    chat_id: str
    adder_email: str
    
# Model for sending message
class SendMessage(BaseModel):
    chat_id: str
    sender_email: str
    receiver_email: str
    original_text: str
    original_language: str
    
class Message(BaseModel):
    chat_id: str
    sender_email: str
    receiver_email: str
    original_text: str
    original_language: str
    translated_text: str
    translated_language: str
    timestamp : str


class ChatHistory(BaseModel):
    chat_id: str
    email: str
    lang_choice: str