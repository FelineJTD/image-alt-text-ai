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
    image_src: str
    image_filename: str
    alt_text: str
    role: str
    context: str
    image_attrs: dict
    a_button_parent: str
    previous_text: str
    next_text: str
            