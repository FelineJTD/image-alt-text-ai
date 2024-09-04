# from pprint import pprint
from pydantic import BaseModel
# from typing import List, Optional, Union, Annotated
# from operator import add
# from prompts import do_action_promos_prompt
# from action import email_inquiry_action, promos_action, room_action, manage_booking_action, cancel_reservation_action
# import json
# import typing

# class AttributeDetails(BaseModel):
#     type: str
#     desc: str
#     value: typing.Any
#     optional: bool = False

#     def to_dict(self):
#         return {
#             "type": self.type,
#             "desc": self.desc,
#             "previous_value": self.value,
#         }
    
#     @classmethod
#     def from_value(cls, new_type, new_value, desc, optional=False):
#         return cls(
#             type=new_type,
#             desc=desc,
#             value=new_value,
#             optional=optional
#         )
    
#     def get_value(self):
#         return self.value

class State(BaseModel):
    input_image_src: str
    input_image_filename: str
    input_context: str
    input_image_attrs: dict
    input_a_button_parent: str
    input_previous_text: str
    input_next_text: str

    correct_role: str
    correct_alt_text: str

    ai_predicted_role: str
    ai_predicted_alt_text: str
            