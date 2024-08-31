from pprint import pprint
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional, Union, Annotated
from operator import add
# from prompts import do_action_promos_prompt
# from action import email_inquiry_action, promos_action, room_action, manage_booking_action, cancel_reservation_action
import json
import typing

class AttributeDetails(BaseModel):
    type: str
    desc: str
    value: typing.Any
    optional: bool = False

    def to_dict(self):
        return {
            "type": self.type,
            "desc": self.desc,
            "previous_value": self.value,
        }
    
    @classmethod
    def from_value(cls, new_type, new_value, desc, optional=False):
        return cls(
            type=new_type,
            desc=desc,
            value=new_value,
            optional=optional
        )
    
    def get_value(self):
        return self.value

class State(BaseModel):
    # images: List[str] = []
    context: str = ""
    # TO-DO: refactor messages to object of message and special object
    # messages: Annotated[List[str], add]
    # schemas: Optional[Schemas]
    # current_schema: str
    # is_complete: bool
    # request_type: str
    # message_type : str
    # language: str = "en"

    # def schemas_to_str(self) -> str:
    #     if self.schemas is None:
    #         return "None"
        
    #     schema_instance = getattr(self.schemas, self.current_schema.lower(), None)
    #     if schema_instance is None:
    #         return "None"

    #     return json.dumps({self.current_schema: schema_instance.to_dict()})

    # def assign_schema(self):
    #     if self.schemas is None:
    #         self.schemas = Schemas(commons = Commons(), room_recommendation = None, promos = None, general_qna = None, email_inquiry = None, manage_booking = None)
    #     if self.schemas.commons is None:
    #         self.schemas.commons = Commons()
    #     if self.current_schema.lower() == "room_recommendation":
    #         self.schemas.room_recommendation = Room_Recommendation()
    #     elif self.current_schema.lower() == "promos":
    #         self.schemas.promos = Promos()
    #     elif self.current_schema.lower() == "general_qna":
    #         self.schemas.general_qna = General_QnA(context_answers=[], question="", isUserTypeNeeded=False, isAsking=False)
    #     elif self.current_schema.lower() == "email_inquiry":
    #         self.schemas.email_inquiry = Email_Inquiry()
    #     elif self.current_schema.lower() == "manage_booking":
    #         self.schemas.manage_booking = Manage_Booking()
    #     elif self.current_schema.lower() == "cancel_reservation":
    #         self.schemas.cancel_reservation = Cancel_Reservation()

    #     # return schemas

    # def update_schema(self, newSchema):
    #     if self.current_schema.lower() == "room_recommendation":
    #         self.schemas.room_recommendation.update_from_dict(newSchema)
    #     elif self.current_schema.lower() == "promos":
    #         self.schemas.promos.update_from_dict(newSchema)
    #     elif self.current_schema.lower() == "email_inquiry":
    #         self.schemas.email_inquiry.update_from_dict(newSchema)
    #     elif self.current_schema.lower() == "cancel_reservation":
    #         self.schemas.cancel_reservation.update_from_dict(newSchema)
            