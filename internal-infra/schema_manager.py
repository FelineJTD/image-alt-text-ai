import uuid
from supabase import create_client, Client
import os

class SchemaManager:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def save_schema(self, schema_data: dict) -> str:
        conversation_id = str(uuid.uuid4())
        
        data = {
            "conversation_id": conversation_id,
            "commons": schema_data.get("commons"),
            "other": schema_data.get("other"),
            "room_recommendation": schema_data.get("room_recommendation"),
            "manage_booking": schema_data.get("manage_booking"),
            "promos": schema_data.get("promos"),
            "email_inquiry": schema_data.get("email_inquiry"),
            "general_qna": schema_data.get("general_qna"),
            "cancel_reservation": schema_data.get("cancel_reservation"),
        }

        response = self.supabase.table("conversation_schema").insert(data).execute()
        
        if response.data:
            return conversation_id
        else:
            print(response.error)
            raise Exception("Failed to save schema")

    def get_schema(self, conversation_id: str) -> dict:
        response = self.supabase.table("conversation_schema").select("*").eq("conversation_id", conversation_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            return None

    def update_schema(self, conversation_id: str, schema_data: dict) -> bool:
        data = {
            "commons": schema_data.get("commons"),
            "other": schema_data.get("other"),
            "room_recommendation": schema_data.get("room_recommendation"),
            "manage_booking": schema_data.get("manage_booking"),
            "promos": schema_data.get("promos"),
            "email_inquiry": schema_data.get("email_inquiry"),
            "general_qna": schema_data.get("general_qna"),
            "cancel_reservation": schema_data.get("cancel_reservation"),
        }

        response = self.supabase.table("conversation_schema").update(data).eq("conversation_id", conversation_id).execute()
        
        if response.data:
            return True
        else:
            print(response.error)
            return False