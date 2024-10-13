# from llava import llava_chatbot
import json
from pprint import pprint

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

from PIL import Image
import pytesseract

from states import State

from prompts import role_identifier_prompt, alt_text_prompts, context_extractor_prompt

memory = SqliteSaver.from_conn_string(":memory:")

# GET IMAGE CONTEXT
def get_image_context(state: State):
    # Summarize the whole document text into usable context/intent
    whole_text = state.input_context

    context_extractor_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.2)
    context_extractor_prompt_template = PromptTemplate.from_template(context_extractor_prompt)
    context_extractor_output_parser = StrOutputParser()

    role_identifier_chain = context_extractor_prompt_template | context_extractor_llm | context_extractor_output_parser
    summarized_context = role_identifier_chain.invoke(whole_text)

    pprint(f"predicted_role: {summarized_context}")

    return {"ai_summarized_context": summarized_context}

def get_image_context_llava(state: State):
    ans = llava_chatbot.start_new_chat(
        prompt=context_extractor_prompt.format(
            message=state.input_context
        )
    )

    return {"ai_summarized_context": ans}

# DETERMINE IMAGE WCAG ROLE
def determine_image_role(state: State):
    role_identifier_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.5)
    role_identifier_prompt_template = PromptTemplate.from_template(role_identifier_prompt)
    role_identifier_output_parser = StrOutputParser()

    role_identifier_chain = role_identifier_prompt_template | role_identifier_llm | role_identifier_output_parser
    predicted_role = role_identifier_chain.invoke(
       f"""
        This is the image you need to identify the role of: {state.input_image_src}\n\n 
        The image's attributes: {state.input_image_attrs}\n\n 
        The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
        The next text after the image appears: {state.input_next_text}\n\n 
        """
    )

    pprint(f"predicted_role: {predicted_role}")

    return {"ai_predicted_role": predicted_role}

def determine_image_role_llava(state: State):
    ans = llava_chatbot.continue_chat(
        prompt=role_identifier_prompt.format(
            message=f"""
                    This is the image you need to identify the role of: {state.input_image_src}\n\n 
                    The image's attributes: {state.input_image_attrs}\n\n 
                    The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
                    The next text after the image appears: {state.input_next_text}\n\n 
                    """
        )
    )

    return {"ai_predicted_role": ans}

# OCR
def ocr_image(state: State):
    """
    Perform OCR on the image specified in the state and update the state with the extracted text.
    
    Args:
        state (State): The state object containing the image path and other relevant information.
    """
    # # Load the image from the path specified in the state
    # image_path = state.input_image_src
    # image = Image.open(image_path)
    
    # # Perform OCR on the image
    # extracted_text = pytesseract.image_to_string(image)
    
    # # Update the state with the extracted text
    # state.extracted_text = extracted_text

    # return state
    pass

# NER
def ner_image(state: State):
    pass

# GENERATE ALT TEXT
def generate_alt_text(state: State):
    # Alt text generation based on guidelines from WCAG: https://www.w3.org/WAI/tutorials/images/

    # If the predicted role is decorative, return an empty alt text
    if state.ai_predicted_role == "decorative":
        return {"ai_predicted_alt_text": ""}
    
    # For other roles, generate alt text based on the role
    alt_text_generator_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.5)
    alt_text_generator_prompt_template = PromptTemplate.from_template(alt_text_prompts[state.ai_predicted_role])
    alt_text_generator_output_parser = StrOutputParser()

    alt_text_generator_chain = alt_text_generator_prompt_template | alt_text_generator_llm | alt_text_generator_output_parser
    predicted_alt_text = alt_text_generator_chain.invoke(
       f"""
        Image: {state.input_image_src}\n\n 
        The image's attributes: {state.input_image_attrs}\n\n 
        The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
        The next text after the image appears: {state.input_next_text}\n\n 
        The summarized context of the website: {state.ai_summarized_context}\n\n
        """
    )

    pprint(f"predicted_alt_text: {predicted_alt_text}")
    pprint(f"correct_alt_text: {state.correct_alt_text}")

    return {"ai_predicted_alt_text": predicted_alt_text}

def generate_alt_text_llava(state: State):
    ans = llava_chatbot.continue_chat(
        prompt=alt_text_prompts[state.ai_predicted_role].format(
            message=f"""
                    Image: {state.input_image_src}\n\n 
                    The image's attributes: {state.input_image_attrs}\n\n 
                    The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
                    The next text after the image appears: {state.input_next_text}\n\n 
                    The summarized context of the website: {state.ai_summarized_context}\n\n
                    """
        )
    )

    return {"ai_predicted_alt_text": ans}

# Define a new graph
workflow = StateGraph(State)

# Add the nodes to the graph
workflow.add_node("determine_image_role", determine_image_role)
workflow.add_node("get_image_context", get_image_context)
workflow.add_node("ocr_image", ocr_image)
workflow.add_node("ner_image", ner_image)
workflow.add_node("generate_alt_text", generate_alt_text)

# Add the edges to the graph
workflow.add_edge("get_image_context", "ocr_image")
workflow.add_edge("ocr_image", "ner_image")
workflow.add_edge("ner_image", "determine_image_role")
workflow.add_edge("determine_image_role", "generate_alt_text")

# Set the entry point
workflow.set_entry_point("get_image_context")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile(checkpointer=memory)

def run_graph(inputs, thread_id):
  final_state = app.invoke(inputs, config={"configurable": {"thread_id": thread_id}})
  return final_state