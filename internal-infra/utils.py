from typing import List
import json
def get_last_message(messages: List[str]):
    """
    Get the last message
    """
    return messages[-1:]
  
def get_history(messages: List[str]):
    """
    Get the history of messages for last 3 messages
    """
    return messages[-3:-1]
  
def parse_messages(messages: List[str]) -> List[str]:
    """
    Get only the text message and map it into an array of only the text
    """
    message_flattened = []
    message_roles = []
    message_filtered = []

    for message_raw in messages:
        message_parsed = message_raw
        try:
            message_parsed = json.loads(message_raw)
        except Exception:
            message_flattened.append(message_parsed)
            message_roles.append("User")
            continue
        if isinstance(message_parsed, list):
            for message_parsed_member in message_parsed:
                message_flattened.append(message_parsed_member)
                message_roles.append(message_parsed_member.get("role", "Assistant"))
        elif isinstance(message_parsed, dict):
            message_flattened.append(message_parsed)
            message_roles.append(message_parsed.get("role", "Assistant"))

    for i, message in enumerate(message_flattened):
        role = message_roles[i]
        if (isinstance(message, str)):
            message_filtered.append(f"{role}: {message}")
        elif (isinstance(message, dict)):
            converted_object = parse_special_object(message, role)
            message_filtered.append(f"{role}: {converted_object}")

    return message_filtered

def parse_special_object(message: dict, role: str) -> str:
    special_object_type = message.get("request_type", "")
    match special_object_type:
        case "text":
            return parse_text(message, role)
        case "manageBooking":
            return parse_manage_booking(message, role)
        case "roomCards":
            return parse_room_cards(message, role)
        case "promoCards":
            return parse_promo_cards(message, role)
        case "emailInquiry":
            return parse_email_inquiry(message, role)
        case "stayDetails":
            return parse_stay_details(message, role)

def parse_text(message: dict, role: str) -> str:
    return message.get('text', {}).get('body', '')

def parse_manage_booking(message: dict, role: str) -> str:
    manage_booking_object = message.get("manageBooking", {})
    return f"{manage_booking_object.get('text', '')}. {manage_booking_object.get('url', '')}."

def parse_room_cards(message: dict, role: str) -> str:
    rooms = message.get("roomCards", [])
    room_names = map(lambda x : f"- {x.get('name', '')}", rooms)
    result = "\n".join(room_names)
    return result

def parse_promo_cards(message: dict, role: str) -> str:
    rooms = message.get("promoCards", [])
    room_names = map(lambda x : f"- {x.get('title', '')}", rooms)
    result = "\n".join(room_names)
    return result

def parse_email_inquiry(message: dict, role: str) -> str:
    email_inquiry_object = message.get("emailInquiry", {}) if role == "Assistant" else message
    if role == "User":
        result = f"My honorific is {email_inquiry_object.get('honorific', '')}, my name is {email_inquiry_object.get('name', '')}, and my email is {email_inquiry_object.get('email', '')}."
        return result
    if role == "Assistant":
        none_keys = [key for key, value in email_inquiry_object.items() if value is None]
        query = email_inquiry_object.get("query", "")
        team_name = email_inquiry_object.get("type", "")
        none_keys_string = ", ".join((map(lambda x : f"{x}", none_keys)))
        result = f"We will send the {team_name} team an email with the question \"{query}\". What is your {none_keys_string}?"
        return result

def parse_stay_details(message: dict, role: str) -> str:
    stay_detail_object = message.get("stayDetails", {}) if role == "Assistant" else message
    if role == "User":
        start_date = stay_detail_object.get("startDate", None)
        end_date = stay_detail_object.get("endDate", None)
        num_rooms = stay_detail_object.get("numRooms", None)
        num_adults = stay_detail_object.get("numAdults", None)
        num_children = stay_detail_object.get("numChildren", None)
        result = f"I would like to stay from {start_date} to {end_date}. I need {num_rooms} room(s). There will be {num_adults} adults and {num_children} children."
        return result
    if role == "Assistant":
        # Make date question
        date_question : str = ""
        start_date = stay_detail_object.get("startDate", None)
        end_date = stay_detail_object.get("endDate", None)
        if (start_date is None and end_date is None):
            date_question = "From what date to what date is your stay?"
        elif (start_date is None):
            date_question = f"I assume you're staying until {end_date}. From what date is your stay?"
        elif (end_date is None):
            date_question = f"I assume you're staying from {end_date}. Until what date is your stay?"

        # Make quantity question
        quantity_keys = ["numChildren","numAdults","numRooms"]
        quantity_keys_none = filter(lambda x: stay_detail_object.get(x, None) is None, quantity_keys)

        quantity_keys_parsed = map(lambda x : x[3:].lower(),quantity_keys_none)

        quantity_question = f"What number of {', '.join(quantity_keys_parsed)} do you need for your stay?"

        result = f"{quantity_question} {date_question}".strip()
        return result
