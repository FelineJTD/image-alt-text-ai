import json
from pprint import pprint

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

from states import State

from prompts import role_identifier_prompt, alt_text_prompts

memory = SqliteSaver.from_conn_string(":memory:")

# GET IMAGE CONTEXT
def get_image_context(state: State):
    pass

# DETERMINE IMAGE WCAG ROLE
def determine_image_role(state: State):
    role_identifier_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.5)
    role_identifier_prompt_template = PromptTemplate.from_template(role_identifier_prompt)
    role_identifier_output_parser = StrOutputParser()

    role_identifier_chain = role_identifier_prompt_template | role_identifier_llm | role_identifier_output_parser
    predicted_role = role_identifier_chain.invoke(
       f"""
        This is the image you need to identify the role of: {state.input_image_src}\n\n 
        The image's file name: {state.input_image_filename}\n\n 
        The image's attributes: {state.input_image_attrs}\n\n 
        The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
        The previous text before the image appears: {state.input_previous_text}\n\n 
        The next text after the image appears: {state.input_next_text}\n\n 
        """
    )

    pprint(f"predicted_role: {predicted_role}")
    pprint(f"correct_role: {state.correct_role}")

    return {"ai_predicted_role": predicted_role}

# OCR
def ocr_image(state: State):
    pass

# NRE
def nre_image(state: State):
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
        The image's file name: {state.input_image_filename}\n\n 
        The image's attributes: {state.input_image_attrs}\n\n 
        The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
        The previous text before the image appears: {state.input_previous_text}\n\n 
        The next text after the image appears: {state.input_next_text}\n\n 
        """
    )

    pprint(f"predicted_alt_text: {predicted_alt_text}")
    pprint(f"correct_alt_text: {state.correct_alt_text}")

    return {"ai_predicted_alt_text": predicted_alt_text}

# Define a new graph
workflow = StateGraph(State)

# Add the nodes to the graph
workflow.add_node("determine_image_role", determine_image_role)
# workflow.add_node("ocr_image", ocr_image)
# workflow.add_node("nre_image", nre_image)
workflow.add_node("generate_alt_text", generate_alt_text)

# Add the edges to the graph
workflow.add_edge("determine_image_role", "generate_alt_text")

# Set the entry point
workflow.set_entry_point("determine_image_role")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile(checkpointer=memory)

def run_graph(inputs, thread_id):
  final_state = app.invoke(inputs, config={"configurable": {"thread_id": thread_id}})
  return final_state