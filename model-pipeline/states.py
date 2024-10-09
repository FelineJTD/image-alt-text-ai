from pydantic import BaseModel

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
    ai_summarized_context: str
    ai_extracted_text: str
    ai_extracted_entities: dict
    ai_predicted_alt_text: str
            