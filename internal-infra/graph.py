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

from prompts import role_identifier_prompt

memory = SqliteSaver.from_conn_string(":memory:")

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

# Define a new graph
workflow = StateGraph(State)

# Add the nodes to the graph
workflow.add_node("determine_image_role", determine_image_role)
workflow.set_entry_point("determine_image_role")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile(checkpointer=memory)

def run_graph(inputs, thread_id):
  final_state = app.invoke(inputs, config={"configurable": {"thread_id": thread_id}})
  return final_state