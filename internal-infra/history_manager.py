import uuid
import os
import json
from pprint import pprint
from supabase import create_client, Client

class HistoryManager:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def save_message(self, conversation_id : str, message_data: dict, role : str) -> str:
        message_id = str(uuid.uuid4())
        
        data = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "content": json.dumps(message_data),
            "role" : role
        }

        response = self.supabase.table("conversation_history").insert(data).execute()
        
        if response.data:
            return message_id
        else:
            print(response.error)
            raise Exception("Failed to save message")

    def get_message(self, message_id : str) -> dict:
        response = self.supabase.table("conversation_history").select("*").eq("message_id", message_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            return None

    def get_history(self, conversation_id : str) -> dict:
        try:
            response = self.supabase.table("conversation_history").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
            if response.data:
                return response.data
            else:
                return None
        except Exception as e:
            print(e)

    def update_message_feedback(self, conversation_id : str, message_id: str, feedback: dict) -> bool:
        rating = feedback.get("rating", None)
        reason = None if rating == "positive" else feedback.get("reason", None)
        comment = None if rating == "positive" else feedback.get("comment", None)

        new_feedback_data = {
            "feedback_rating": rating,
            "feedback_reason": reason,
            "feedback_comment": comment,
        }

        response = self.supabase.table("conversation_history").update(new_feedback_data).eq("conversation_id", conversation_id).eq("message_id", message_id).execute()
        
        if response.data and len(response.data) > 0:
            new_message_data = response.data[0]
            persisted_feedback = {
                "reason": new_message_data.get("feedback_reason", None),
                "comment": new_message_data.get("feedback_comment", None),
                "rating": new_message_data.get("feedback_rating", None),
            }
            return persisted_feedback
        elif len(response.data) == 0:
            raise Exception("Feedback not sent, message with the given message_id does not exist!")
        else:
            raise Exception(response.error)