from pprint import pprint

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from clipscore import get_clip_score
from dotenv import load_dotenv
import numpy as np
load_dotenv()

# from PIL import Image
# import pytesseract
# import requests
from ner import nltk_ner
from nltk.tokenize import sent_tokenize

from states import State

import json

from prompts import role_identifier_prompt, alt_text_prompts, image_description_prompt

memory = SqliteSaver.from_conn_string(":memory:")


# GET IMAGE CONTEXT
# def get_image_context(state: State):
#     # Summarize the whole document text into usable context/intent
#     print("Summarizing the context of the website with GPT-4o Mini...")
#     whole_text = state.input_context

#     context_extractor_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.2)
#     context_extractor_prompt_template = PromptTemplate.from_template(context_extractor_prompt)
#     context_extractor_output_parser = StrOutputParser()

#     role_identifier_chain = context_extractor_prompt_template | context_extractor_llm | context_extractor_output_parser
#     summarized_context = role_identifier_chain.invoke(whole_text)

#     pprint(f"predicted_role: {summarized_context}")

#     return {"ai_summarized_context": summarized_context}

# def get_image_context_llava(state: State):
#     print("Getting image context with LLaVA...")
#     print(f"state.input_context: {state.input_context}")
#     ans = llava_chatbot.start_new_chat(
#         prompt=context_extractor_prompt.format(
#             message=state.input_context
#         )
#     )

#     return {"ai_summarized_context": ans}

def generate_descriptive_alt_text(state: State):
    # Alt text generation based on guidelines from WCAG: https://www.w3.org/WAI/tutorials/images/
    print("Generating descriptive alt text with GPT-4o Mini...")
    try:        
        role_identifier_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.5)
        predicted_alt_text = role_identifier_llm.invoke(
            [
                (
                    "system",
                    image_description_prompt
                ),
                (
                    "human",
                    [
                        {
                            "type": "image_url", "image_url": {"url": state["input_img_src"]}
                        }
                    ]
                )
            ]
        )

        pprint(f"predicted_alt_text: {predicted_alt_text.content}")

        return {"ai_predicted_descriptive_alt_text": predicted_alt_text.content}
    except Exception as e:
        print(e)

    return {"ai_predicted_role": ""}

# DETERMINE IMAGE WCAG ROLE
def determine_image_role(state: State):
    print("Determining image role with GPT-4o Finetuned...")
    try:
        role_identifier_llm = ChatOpenAI(model='ft:gpt-4o-2024-08-06:personal:role-iden-50:AahYYJoD', temperature=0.5)
        predicted_role = role_identifier_llm.invoke(
            [
                (
                    "system",
                    role_identifier_prompt
                ),
                (
                    "human",
                    [
                        {
                            "type": "image_url", "image_url": {"url": state["input_img_src"]}
                        },
                        {
                            "type": "text", "text": f"""
The website's title: {state["input_doc_title"]}\n\n
The website's description: {state["input_doc_description"]}\n\n                            
The image's attributes: {state["input_img_attrs"]}\n\n
The image's <a> or <button> parent: {state["input_img_a_button_parent"]}\n\n
The previous text before the image appears: {state["input_img_header"] + " ... " + state["input_img_prev_text"]}\n\n
The next text after the image appears: {state["input_img_next_text"] + " ... "}\n\n
                            """
                        }
                    ]
                )
            ]
        )

        pprint(f"predicted_role: {predicted_role.content}")

        return {"ai_predicted_role": predicted_role.content}
    except Exception as e:
        print(e)

    return {"ai_predicted_role": ""}

# def determine_image_role_llava(state: State):
#     ans = llava_chatbot.start_new_chat(
#         img_path=state.input_image_src,
#         prompt=role_identifier_prompt.format(
#             message=f"""
#                     The image's source (file name): {state.input_image_src}\n\n
#                     The image's attributes: {state.input_image_attrs}\n\n 
#                     The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
#                     The next text after the image appears: {state.input_next_text}\n\n 
#                     """
#         )
#     )

#     return {"ai_predicted_role": ans}

# OCR
def ocr_image(state: State):
    """
    Perform OCR on the image specified in the state and update the state with the extracted text.
    Args:
        state (State): The state object containing the image path and other relevant information.
    """
    # # Load the image from the path specified in the state
    # image_path = state.input_image_src

    # # Download the image from the URL
    # image = Image.open(requests.get(image_path, stream=True).raw)

    # # Perform OCR on the image
    # extracted_text = pytesseract.image_to_string(image)
    # pprint(f"Extracted text: {extracted_text}")
    
    # # Update the state with the extracted text
    # state.ai_extracted_text = extracted_text

    # return state
    pass

def extract_similar_context(state: State):
    # Extract similar context from the previous and next text
    whole_text = state["input_doc_text"]
    # Split the whole text into sentences
    sentences = sent_tokenize(whole_text.replace("\n", ". "))

    try:
        score, per, candidates = get_clip_score([state["input_img_src"]], sentences)
        # Print the top 5 similar sentences
        top_5_indices = np.argsort(np.array(per))[-5:][::-1]

        top_5_sentences = [sentences[i] for i in top_5_indices]
        pprint(f"Top 5 similar sentences: {top_5_sentences}")
    except Exception as e:
        print(e)
    

# NER
def ner_image(state: State):
    """
    Perform Named Entity Recognition on the extracted text from the image and update the state with the extracted entities.
    Args:
        state (State): The state object containing the extracted text and other relevant information.
    """
    # Perform NER on the extracted text
    print("Performing Named Entity Recognition on the extracted text...")
    extracted_entities = nltk_ner(state["input_doc_text"])

    pprint(f"Extracted entities: {extracted_entities}")

    # Update the state with the extracted entities
    return {"ai_extracted_entities": json.dumps(extracted_entities)}

# GENERATE ALT TEXT
def generate_alt_text(state: State):
    # Alt text generation based on guidelines from WCAG: https://www.w3.org/WAI/tutorials/images/
    print("Generating alt text with GPT-4o Mini...")
    try:
        ai_predicted_role = state["ai_predicted_role"].lower()

        # If the predicted role is decorative, return an empty alt text
        if ai_predicted_role == "decorative":
            return {"ai_predicted_contextual_alt_text": "Decorative image", "ai_predicted_contextual_alt_text_confidence": 1.0}
        
        # If the predicted role is not in the alt text prompts, default to informative
        if ai_predicted_role not in alt_text_prompts:
            ai_predicted_role = "informative"
        
        # For other roles, generate alt text based on the role
        role_identifier_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.5).bind(logprobs=True)
        predicted_alt_text = role_identifier_llm.invoke(
            [
                (
                    "system",
                    alt_text_prompts[ai_predicted_role]
                ),
                (
                    "human",
                    [
                        {
                            "type": "image_url", "image_url": {"url": state["input_img_src"]}
                        },
                        {
                            "type": "text", "text": f"""
The website's title: {state["input_doc_title"]}\n\n
The website's description: {state["input_doc_description"]}\n\n
The image's attributes: {state["input_img_attrs"]}\n\n
The image's <a> or <button> parent: {state["input_img_a_button_parent"]}\n\n
The previous text before the image appears: {state["input_img_header"] + " ... " + state["input_img_prev_text"]}\n\n
The next text after the image appears: {state["input_img_next_text"]}\n\n
Entities found in the whole website text: {state["ai_extracted_entities"]}\n\n
                            """
                        }
                    ]
                )
            ]
        )

        logprobs = predicted_alt_text.response_metadata['logprobs']['content']
        # Calculate response confidence based on logprobs
        response_confidence = sum([10 ** logprob['logprob'] for logprob in logprobs]) / len(logprobs)
        pprint(f"RESPONSE CONFIDENCE: {response_confidence}")

        # pprint(f"LOGPROBS: {predicted_alt_text.response_metadata['logprobs']['content']}")
        pprint(f"predicted_alt_text: {predicted_alt_text.content}")

        return {"ai_predicted_contextual_alt_text": predicted_alt_text.content, "ai_predicted_contextual_alt_text_confidence": response_confidence}
    except Exception as e:
        print(e)

    return {"ai_predicted_role": ""}

# def generate_alt_text_llava(state: State):
#     ans = llava_chatbot.continue_chat(
#         prompt=alt_text_prompts[state.ai_predicted_role].format(
#             message=f"""
#                     Image: {state.input_image_src}\n\n 
#                     The image's attributes: {state.input_image_attrs}\n\n 
#                     The image's <a> or <button> parent: {state.input_a_button_parent}\n\n 
#                     The next text after the image appears: {state.input_next_text}\n\n 
#                     The summarized context of the website: {state.ai_summarized_context}\n\n
#                     """
#         )
#     )

#     return {"ai_predicted_alt_text": ans}

# Define a new graph
workflow = StateGraph(State)

# Add nodes to the graph
workflow.add_node("generate_descriptive_alt_text", generate_descriptive_alt_text)
workflow.add_node("extract_similar_context", extract_similar_context)
workflow.add_node("determine_image_role", determine_image_role)
# workflow.add_node("ocr_image", ocr_image)
workflow.add_node("ner_image", ner_image)
workflow.add_node("generate_alt_text", generate_alt_text)

# Add edges to the graph
workflow.add_edge(START, "generate_descriptive_alt_text")
workflow.add_edge("generate_descriptive_alt_text", END)

# workflow.add_edge(START, "ocr_image")
workflow.add_edge(START, "extract_similar_context")
workflow.add_edge(START, "ner_image")
workflow.add_edge("ner_image", "determine_image_role")
workflow.add_edge("determine_image_role", "generate_alt_text")
workflow.add_edge("generate_alt_text", END)

# Compile the graph
app = workflow.compile(checkpointer=memory)

def run_graph(inputs, thread_id):
  final_state = app.invoke(inputs, config={"configurable": {"thread_id": thread_id}})
  return final_state