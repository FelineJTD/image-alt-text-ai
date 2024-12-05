# from pydantic import BaseModel

import operator
from typing import Annotated

from typing_extensions import TypedDict

class State(TypedDict):
    # Th reducer fn makes this append-only
    input_doc_url: Annotated[str, operator.add]
    input_doc_title: Annotated[str, operator.add]
    input_doc_description: Annotated[str, operator.add]
    input_doc_text: Annotated[str, operator.add]
    input_img_src: Annotated[str, operator.add]
    input_img_attrs: Annotated[str, operator.add]
    input_img_a_button_parent: Annotated[str, operator.add]
    input_img_prev_text: Annotated[str, operator.add]
    input_img_next_text: Annotated[str, operator.add]

    correct_role: Annotated[str, operator.add]
    correct_alt_text: Annotated[str, operator.add]

    ai_predicted_role: Annotated[str, operator.add]
    ai_summarized_context: Annotated[str, operator.add]
    ai_extracted_text: Annotated[str, operator.add]
    ai_extracted_entities: Annotated[str, operator.add]
    ai_predicted_contextual_alt_text: Annotated[str, operator.add]
    ai_predicted_contextual_alt_text_confidence: Annotated[float, operator.add]
    ai_predicted_descriptive_alt_text: Annotated[str, operator.add]


# class State(TypedDict):
#     input_doc_url: str
#     input_doc_title: str
#     input_doc_description: str
#     input_doc_text: str
#     input_img_src: str
#     input_img_attrs: dict
#     input_img_a_button_parent: str
#     input_img_prev_text: str
#     input_img_next_text: str

#     correct_role: str
#     correct_alt_text: str

#     ai_predicted_role: str
#     ai_summarized_context: str
#     ai_extracted_text: str
#     ai_extracted_entities: dict
#     ai_predicted_contextual_alt_text: str
#     ai_predicted_descriptive_alt_text: str