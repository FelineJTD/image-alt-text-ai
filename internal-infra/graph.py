import json
from pprint import pprint

from langchain_fireworks import ChatFireworks
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# from rag_graph import answer, escalate_to_email, retrieve, check_user_type_entry, check_user_type_cond, infer_user_type, check_is_asking
from states import State

# from utils import get_last_message, parse_messages
# from prompts import language_identifier_prompt, parse_intent_prompt, parse_input_prompt, refill_schema_prompt, actionable_message_identifier_prompt, answer_greetings_prompt
from prompts import role_identifier_prompt

# from locales import cancel_reservation_refill_schema

# from langdetect import detect

memory = SqliteSaver.from_conn_string(":memory:")

# def language_identifier(state: State):
#     try:
#         # If message is a special object, return the previously determined language
#         if state.request_type != "text":
#             return {"language": state.language}
        
#         # It message is a text, determine the language
#         message = get_last_message(state.messages)

#         language = detect(message[0])
#         if language == "zh-cn" or language == "zh-tw":
#             language = "zh"
#         elif language != "en" and language != "ja" and language != "ko":
#             language = "en"
#         parsed_result = {"language" : language}

#         print("Language identifier result:")
#         print(parsed_result)

#         return parsed_result
#     except Exception as e:
#         print("Error in language_identifier", e)
#         return {"language": "en"}

# def is_language_supported_cond(state: State):
#     supported_languages = ["en", "ja", "ko", "zh"]
#     if state.language in supported_languages:
#         return "actionable_message_identifier"
#     else:
#         return "reject_language"
    
# def reject_language(state: State):
#     # TODO: Language not supported message
#     result_raw = [
# 		{"type": "text", "text": {"body": "Sorry, we currently only support English, Japanese, Korean, and Chinese."}}
#     ]
#     result = json.dumps(result_raw)
#     return {"messages": [result]}
# from dataclasses import asdict
# from prompts import parse_intent_prompt, parse_input_prompt, check_completeness_prompt, refill_schema_prompt, actionable_message_identifier_prompt, answer_greetings_prompt
# from utils import get_last_message, parse_messages, get_history

# memory = SqliteSaver.from_conn_string(":memory:")

# def entry_point(state: State):
#     state_to_return = {
#         **state.dict(),
#     }

#     del state_to_return["messages"]

#     return state_to_return

# def is_asking_entry_point(state: State):
#     if state.schemas.general_qna is not None and state.schemas.general_qna.isAsking == True:
#         return "check_user_type_entry"
#     else:
#         return "language_identifier"

# def actionable_message_identifier(state: State):
#     message = get_last_message(state.messages)
#     history = get_history(state.messages)
#     llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.3)
#     prompt = PromptTemplate.from_template(actionable_message_identifier_prompt)
#     output_parser = JsonOutputParser()

#     chain = prompt | llm | output_parser
#     result = chain.invoke({"message" : message, "history": history})
#     message_type = result.get("message_type", "actionable")
#     parsed_result = {"message_type" : message_type}

#     return parsed_result

# def is_actionable_cond(state: State):
#     if state.message_type == "actionable":
#         return "parse_intent"
#     else:
#         return "answer_greetings"

# def answer_greetings(state: State):
#     greetings = get_last_message(state.messages)

#     chatbot_greetings_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.6)
#     chatbot_greetings_prompt = PromptTemplate.from_template(answer_greetings_prompt)
#     output_parser = StrOutputParser()

#     chatbot_greetings_chain = chatbot_greetings_prompt | chatbot_greetings_llm | output_parser
#     chatbot_greetings = chatbot_greetings_chain.invoke({"greetings" : greetings, "is_closing_message" : "Yes" if state.message_type == "closing" else "No", "language": state.language})

#     result_raw = [
# 		{"type": "text", "text": {"body": chatbot_greetings}, "role" : "Assistant"}
#     ]

#     result = json.dumps(result_raw)
#     return {"messages": [result]}

def determine_image_role(state: State):
    role_identifier_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.6)
    role_identifier_prompt_template = PromptTemplate.from_template(role_identifier_prompt)
    role_identifier_output_parser = StrOutputParser()

    role_identifier_chain = role_identifier_prompt_template | role_identifier_llm | role_identifier_output_parser
    predicted_role = role_identifier_chain.invoke(state)

    pprint(f"predicted_role: {predicted_role}")

    return {"ai_predicted_role": predicted_role}

# def parse_intent(state: State):
#     llm = ChatOpenAI(model='gpt-4o',temperature=0)
#     prompt = PromptTemplate.from_template(parse_intent_prompt)
#     output_parser = StrOutputParser()

#     chain = prompt | llm | output_parser

#     if state.request_type != "text":
#         for schema_name, schema_instance in state.schemas.__dict__.items():
#             if schema_instance and hasattr(schema_instance, "specialObjectType") and schema_instance.specialObjectType == state.request_type:
#                 print("Request type not text. Assigning schema based on the special object from the user: ", schema_name)
#                 state.current_schema = schema_name
#                 break
#     else:      
#         parsed_history = parse_messages(state.messages)
#         readable_history_str = "\n".join(parsed_history)

#         # Assuming you are passing this to a function named chain.invoke
#         response = chain.invoke({"question": state.messages[-1], "chat_history": readable_history_str})

#         state.current_schema = response

#     if state.schemas is None or state.schemas.dict().get(state.current_schema.lower()) is None:
#         state.assign_schema()
#     pprint(f"in parse_intent 2: {state}")
#     state_to_return = {
#         **state.dict(),
#     }

#     del state_to_return["messages"]
    
#     return state_to_return

# def update_commons(state: State):
#     if state.current_schema == "room_recommendation" or state.current_schema == "promos":
#         state.schemas.commons.update_from_dict({
#             "userType": "non_staying_guest"
#         })
#         if state.schemas.email_inquiry is not None:
#             state.schemas.email_inquiry.update_from_dict({
#                 "reservationId": None
#             })
#     elif state.current_schema == "manage_booking":
#         state.schemas.commons.update_from_dict({
#             "userType": "staying_guest"
#         })
#     state_to_return = {
#         **state.dict(),
#     }

#     del state_to_return["messages"]

#     pprint(f"state_to_return: {state_to_return}")
    
#     return state_to_return
    

# def schema_caller_cond(state: State):
#     print("in schema_caller_cond", state)
#     if state.current_schema == "general_qna":
#         if state.schemas.general_qna is not None and state.schemas.general_qna.isAsking == True:
#             return "check_user_type_entry"
#         else:
#             return "infer_user_type"
#     else:
#         return "update_commons"

# def parse_input(state: State):
#     if state.current_schema == "manage_booking":
#         schema_data = {
#             "complete": True
#         }
#     else:
#         llm = ChatOpenAI(model='gpt-4o', temperature=0)
#         prompt = PromptTemplate.from_template(parse_input_prompt)
#         # output_parser = StrOutputParser()
#         output_parser = JsonOutputParser()

#         chain = prompt | llm | output_parser

#         pprint(f"state: {state}")
#         parsed_response = chain.invoke({
#             "input": state.messages[-1],
#             "schema": state.schemas_to_str()
#         })

#         # pprint(f"response: {json.loads(getattr(response, state.current_schema.lower(), None))}")
#         pprint(f"response: {parsed_response}")

#         # Parse the entire response as JSON
#         # parsed_response = json.loads(response)

#         # Access the appropriate key using state.current_schema
#         schema_data = parsed_response.get(state.current_schema.lower(), {})

#     pprint(f"new_schema_data: {schema_data}")

#     state.update_schema(schema_data)

#     state_to_return = {
#         **state.dict(),
#     }

#     del state_to_return["messages"]

#     pprint(f"state_to_return_input: {state_to_return}")
    
#     return state_to_return

# def is_complete_node(state: State):
#     # llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
#     # prompt = PromptTemplate.from_template(check_completeness_prompt)
#     # output_parser = StrOutputParser()

#     # # TO-DO - add JSON output parser, an array of 2 objects, one for the schema and one for the message

#     # chain = prompt | llm | output_parser

#     # response = chain.invoke({
#     #     "schema": state.schemas_to_str()
#     # })

#     # current_schema = getattr(state.schemas, state.current_schema.lower(), None)

#     # print("this is current schema", current_schema)

#     # # state.messages.append(response)

#     # if response.lower() == "complete":
#     #     state.is_complete = True

#     current_schema = getattr(state.schemas, state.current_schema.lower(), None).__dict__

#     pprint(f"current_schema: {current_schema}")

#     pprint(f"state: {state}")

#     pprint(f"state.request_type and state.current_schema: {state.request_type}, {state.current_schema}")

#     if state.current_schema == "email_inquiry" and state.request_type != "emailInquiry":
#         state.is_complete = False
#     if state.current_schema == "email_inquiry" and state.request_type == "emailInquiry":
#         state.is_complete = True
#     elif isinstance(current_schema, dict):
#         state.is_complete = True
#         for key, value in current_schema.items():
#             # if value is not object just continue
#             if key == 'specialObject' or key == 'specialObjectType' or key == 'complete' or value.optional == True:
#                 continue
#             elif value.value == None:
#                 print("here")
#                 state.is_complete = False
#                 break

#     state_to_return = {
#         **state.dict(),
#     }

#     del state_to_return["messages"]

#     pprint(f"state_to_return: {state_to_return}")
    
#     return state_to_return

# def check_completeness(state: State):
#     # TO-DO: add a node to check if the schema is filled or not
#     # last_message = state.messages[-1]
#     if state.is_complete:
#         # if state.current_schema == "Room_Reservation":
#         #     return "do_action_room_reservation"
#         # elif state.current_schema == "Promos":
#         #     return "do_action_promos"
#         # else:
#         #     return "do_action_other"
#         return "do_action"
#     else:
#         return "refill_schema"

# def do_action(state: State):
#     if state.schemas is not None and state.current_schema:
#         schema = getattr(state.schemas, state.current_schema.lower(), None)
#         print("this is schema", schema)
#         if schema and hasattr(schema, 'action'):
#             action_result = schema.action(state.messages, state.language)
#             pprint(f"action_result: {action_result}")

#             state.messages = [action_result]
            
#             # state.messages.append(action_result)
    
#     if state.current_schema == "cancel_reservation":
#         state.schemas.cancel_reservation = None
#     return state

# def refill_schema(state: State):
#     # TO-DO: add a node to check if the schema is filled or not
#     print("In refill schema")
    
#     question = state.messages[-1:]
#     schema_name = state.current_schema.lower()
#     schema_object = getattr(state.schemas, schema_name, None)

#     llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.6)
#     prompt = PromptTemplate.from_template(refill_schema_prompt)
#     output_parser = StrOutputParser()

#     chain = prompt | llm | output_parser

#     pprint({"action" : " ".join(schema_name.split("_")), "question" : question, "language": state.language})
#     response = chain.invoke({"action" : schema_name.split("_"), "question" : question, "language": state.language})
    
#     if (state.current_schema == "cancel_reservation"):
#         object_result = [{
#             "type": "text",
#             "text": {"body": response + " " + cancel_reservation_refill_schema[state.language]},
#             "role": "Assistant"
#         }]
#     else:
#         schema_object = getattr(state.schemas, state.current_schema.lower(), None)
#         dict_object = schema_object.to_value_dict() if schema_object is not None else None
#         object_type = schema_object.specialObjectType if dict_object is not None else None

#         pprint(f"dict_object: {dict_object}")
#         object_result = [{
#             "type": "text",
#             "text": {"body": response},
#             "role" : "Assistant"
#         }, 
#         {
#             "type": object_type,
#             object_type: dict_object,
#             "role" : "Assistant"
#         }]

#     pprint(f"object_result: {object_result}")

#     stringified_result = json.dumps(object_result)

#     state.messages.append(stringified_result)
#     return state

# Define a new graph
workflow = StateGraph(State)

# Define the two nodes we will cycle between
# workflow.add_node("entry_point", entry_point) # this is the entry point
# workflow.add_node("is_asking_entry_point", is_asking_entry_point)
# workflow.add_node("language_identifier", language_identifier) # this classifies the language of the message
# workflow.add_node("actionable_message_identifier", actionable_message_identifier) # this classifies whether the message is actionable or not
# workflow.add_node("answer_greetings", answer_greetings) # this answer greetings
# workflow.add_node("parse_intent", parse_intent) # this points to the correct schema
# workflow.add_node("update_commons", update_commons) # this updates the commons schema
# workflow.add_node("parse_input", parse_input) # this parse the user input fill the schema
# workflow.add_node("is_complete_node", is_complete_node)
# # workflow.add_node("do_action_promos", do_action_promos)
# # workflow.add_node("do_action_room_reservation", do_action_room_reservation)
# workflow.add_node("do_action", do_action)
# workflow.add_node("refill_schema", refill_schema)
# #TO-DO: add a node to check if the schema is filled or not 
# #another node to check if the schema is filled or not

# # This is for RAG flow
# workflow.add_node("infer_user_type", infer_user_type)
# workflow.add_node("check_user_type_entry", check_user_type_entry)
# workflow.add_node("check_user_type_cond", check_user_type_cond)
# workflow.add_node("retrieve", retrieve)
# workflow.add_node("reject_language", reject_language)
# workflow.add_node("answer", answer)
# workflow.add_node("escalate_to_email", escalate_to_email)

# # workflow.add_edge("infer_user_type", "retrieve")
# # workflow.add_edge("check_user_type", "retrieve")
# workflow.add_conditional_edges("infer_user_type", check_is_asking)
# workflow.add_conditional_edges("check_user_type_entry", check_user_type_cond)
# workflow.add_edge("retrieve", "answer")
# workflow.add_edge("answer", END)
# workflow.add_edge("answer_greetings", END)
# workflow.add_edge("escalate_to_email", END)

# # Set the entrypoint as `agent`
# # This means that this node is the first one called
# # workflow.set_entry_point("actionable_message_identifier")
# workflow.set_entry_point("entry_point")
# workflow.add_conditional_edges("entry_point", is_asking_entry_point)
# workflow.add_conditional_edges("language_identifier", is_language_supported_cond)
# workflow.add_conditional_edges("actionable_message_identifier", is_actionable_cond)
# workflow.add_conditional_edges("parse_intent", schema_caller_cond)
# workflow.add_edge("update_commons", "parse_input")
# workflow.add_edge("parse_input", "is_complete_node")
# workflow.add_conditional_edges("is_complete_node", check_completeness)
# # workflow.add_edge("do_action_promos", END)
# # workflow.add_edge("do_action_room_reservation", END)
# workflow.add_edge("do_action", END)
# workflow.add_edge("refill_schema", END)
# #TO-DO: add conditional edge to check the completeness of the schema 
# #TO-DO: if action is success go to last node to prepare something
workflow.add_node("determine_image_role", determine_image_role)
workflow.set_entry_point("determine_image_role")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile(checkpointer=memory)


def run_graph(inputs, thread_id):
  final_state = app.invoke(inputs, config={"configurable": {"thread_id": thread_id}})
#   pprint(f"FINAL STATE: {final_state}")
  return final_state