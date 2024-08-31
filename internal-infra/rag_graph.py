import json
from pprint import pprint

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter
import hashlib

from states import General_QnA, State, Email_Inquiry, Commons

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import time

import boto3

from prompts import check_relevancy_prompt, answer_prompt, rephrase_subject_prompt, select_email_inquiry_type_prompt, select_user_type_prompt, select_user_type_specific_prompt, answer_prompt_unknown_user_type
from locales import existing_reservation

from dotenv import load_dotenv
load_dotenv()
import os

index_name = os.getenv('PINECONE_INDEX_NAME', '')
pprint(f"INDEX NAME: {index_name}")
embedding = OpenAIEmbeddings(model = "text-embedding-3-large")

### LOAD VECTORSTORE
pprint(f"Loading Vectorstore {index_name} ...")
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embedding)
# TODO: Change this into k:3
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.5},
)

# AWS S3 configuration
s3 = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
bucket = os.getenv('AMPLIFY_BUCKET')

def update_email_inquiry(state: State, type: str):
    current_query = state.schemas.general_qna.question
    current_type = type
    state.current_schema = "email_inquiry"
    if state.schemas is not None:
        if state.schemas.email_inquiry is not None:
            current_email = state.schemas.email_inquiry.email.value
            current_name = state.schemas.email_inquiry.name.value
            current_honorific = state.schemas.email_inquiry.honorific.value
            current_reservationId = state.schemas.email_inquiry.reservationId.value
        else:
            state.assign_schema()
            current_email = None
            current_name = None
            current_honorific = None
            current_reservationId = None
    else:
        state.assign_schema()
        current_email = None
        current_name = None
        current_honorific = None
        current_reservationId = None

    if state.schemas.commons.userType.value == "staying_guest":
        email_inquiry_schema = {"email": current_email, "name": current_name, "query": current_query, "type": current_type, "honorific": current_honorific, "reservationId": current_reservationId}
    else:
        email_inquiry_schema = {"email": current_email, "name": current_name, "query": current_query, "type": current_type, "honorific": current_honorific}
    state.update_schema(email_inquiry_schema)
    return email_inquiry_schema

def generate_vectorstore_id(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def create_vectorstore():
    # read markdown string from file
    markdown_document = read_markdown_file("knowledge.txt")

    pprint(f"markdown_document: {markdown_document[:2000]}")

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(markdown_document)

    pprint(f"md_header_splits: {md_header_splits}")
    
    vectorstore.from_documents(md_header_splits, embedding, index_name=index_name, ids=[generate_vectorstore_id(doc.page_content) for doc in md_header_splits])


# Function to update the vectorstore with the new knowledge base
# Input: old_knowledge_key: the key of the old knowledge base in AWS S3, if there is no old knowledge base, set this to ""
#        new_knowledge_key: the key of the new knowledge base in AWS S3
# Output: True if the update is successful, False otherwise
def update_vectorstore(old_knowledge_key, new_knowledge_key):
    try:
        # Split config
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        # Process the old knowledge base
        if (old_knowledge_key != ""):
            print("There is an old knowledge base")
            # There is an old knowledge base, download old knowledge base from AWS S3
            old_knowledge_obj = s3.get_object(Bucket=bucket, Key=old_knowledge_key)
            old_knowledge = old_knowledge_obj['Body'].read().decode('utf-8')
            # Split the old knowledge base
            old_knowledge_split = markdown_splitter.split_text(old_knowledge)
        else:
            print("There is no old knowledge base")
            # No old knowledge base
            old_knowledge_split = []

        # Process the new knowledge base
        # Download the new knowledge base from AWS S3
        retries = 0
        while retries < 3:
            try:
                new_knowledge_obj = s3.get_object(Bucket=bucket, Key=new_knowledge_key)
                new_knowledge = new_knowledge_obj['Body'].read().decode('utf-8')
                break
            except Exception as e:
                # wait 0.1 seconds before retrying
                print(f"An error occurred: {e}")
                retries += 1
                time.sleep(0.1)

        # Split the new knowledge base
        new_knowledge_split = markdown_splitter.split_text(new_knowledge)

        print(f"Old knowledge split: {old_knowledge_split}")
        print(f"New knowledge split: {new_knowledge_split}")

        # Compare the new knowledge with the current knowledge
        deleted_knowledge_ids = [generate_vectorstore_id(doc.page_content) for doc in old_knowledge_split if doc not in new_knowledge_split]
        new_knowledge_docs = [doc for doc in new_knowledge_split if doc not in old_knowledge_split]
        new_knowledge_ids = [generate_vectorstore_id(doc.page_content) for doc in new_knowledge_docs]

        # Update the Pinecone index
        # TODO: Check contents to see if they are the same, since id doesn't guarantee the same content
        vectorstore.delete(deleted_knowledge_ids)
        vectorstore.from_documents(new_knowledge_docs, embedding, index_name=index_name, ids=new_knowledge_ids)

        # Delete the old knowledge base from AWS S3
        if (old_knowledge_key != ""):
            s3.delete_object(Bucket=bucket, Key=old_knowledge_key)

        return True
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def check_user_type_entry(state: State):
    return {"schemas": state.schemas}

def check_user_type_cond(state: State):
    print("in check_user_type", state)

    if state.schemas.commons is None:
        state.schemas.commons = Commons()

    if state.schemas.commons.userType.value == "unknown":
        llm = ChatOpenAI(model='gpt-4o',temperature=0)
        prompt = PromptTemplate.from_template(select_user_type_specific_prompt)
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        user_type = chain.invoke({"response": state.messages[-1]})

        state.schemas.commons.update_from_dict({"userType": user_type})

        pprint(f"user_type: {user_type}")

    if user_type == "others":
        state.schemas.general_qna.isAsking = False
        return "actionable_message_identifier"
    else:
        return "answer"

def infer_user_type(state: State):
    print("in infer_user_type", state)

    if state.schemas.commons is None:
        state.schemas.commons = Commons()

    if state.schemas.commons.userType.value == "unknown":
        llm = ChatOpenAI(model='gpt-4o',temperature=0)
        prompt = PromptTemplate.from_template(select_user_type_prompt)
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        user_type = chain.invoke({"chat_history": state.messages})

        state.schemas.commons.update_from_dict({"userType": user_type})

        pprint(f"user_type: {user_type}")

    return {"schemas": state.schemas}

def check_is_asking(state: State):
    print("in check_is_asking", state)

    if state.schemas.general_qna.isAsking:
        return "answer"
    else:
        return "retrieve"

def retrieve(state: State):
    print("in retrieve", state)

    question = state.messages[-1]
    context_data = retriever.invoke(question)

    pprint(f"context_data: {context_data}")

    context_answers = [data.page_content for data in context_data]

    # state.schemas.general_qna = {"question": question, "context_answers": context_answers}
    state.schemas.general_qna = General_QnA(context_answers=context_answers, question=question)
    
    pprint(f"context_answers: {context_answers}")
    return {"schemas": state.schemas}

def answer(state: State):
    print("in answer", state)

    context_answers = state.schemas.general_qna.context_answers
    question = state.schemas.general_qna.question

    state.schemas.general_qna.isAsking = False


    if state.schemas.commons.userType.value != "unknown":
        if state.schemas.commons.userType.value == "staying_guest":
            appended_question = question + " I have an upcoming reservation"
        elif state.schemas.commons.userType.value == "non_staying_guest":
            appended_question = question + " I don't have an upcoming reservation"
        llm = ChatOpenAI(model='gpt-4o',temperature=0)
        prompt = PromptTemplate.from_template(answer_prompt)
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        response = chain.invoke({"question": appended_question, "context_answers": context_answers, "language": state.language})
        is_different = "no"
    else:
        llm = ChatOpenAI(model='gpt-4o',temperature=0)
        prompt = PromptTemplate.from_template(answer_prompt_unknown_user_type)
        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        raw_response = chain.invoke({"question": question, "context_answers": context_answers, "language": state.language})

        response = raw_response.get("answer", {})
        is_different = raw_response.get("is_different", False)

    if is_different == "yes":
        result = json.dumps([{"type": "text", "text": {"body": existing_reservation[state.language]}}])

        state.schemas.general_qna.isAsking = True
    elif response == "unclear":
        llm = ChatOpenAI(model='gpt-4o',temperature=0.3)
        prompt = PromptTemplate.from_template(rephrase_subject_prompt)
        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser
        
        apology = chain.invoke({"question": question, "language": state.language})

        llm_type = ChatOpenAI(model='gpt-4o-mini',temperature=0)
        prompt_type = PromptTemplate.from_template(select_email_inquiry_type_prompt)
        output_parser_type = StrOutputParser()

        chain_type = prompt_type | llm_type | output_parser_type

        inquiry_type = chain_type.invoke({"question": question, "language": state.language})
        email_inquiry_schema = update_email_inquiry(state, inquiry_type)

        result = json.dumps([
            {"type": "text", "text": {"body": apology}, "role" : "Assistant"},
            {"type": "emailInquiry", "emailInquiry": email_inquiry_schema, "role" : "Assistant"},
        ])
    else:
        possible_email = {
            "wedding": "events.bali@ayana.com",
            "room_reservation": "reservation.bali@ayana.com",
            "restaurant": "fb.reservation@ayanaresort.com",
            "spa": "info-spa.bali@ayana.com",
            "general_information": "info.bali@ayana.com",
            "rewards": "info@ayanarewards.com"
        }

        raw_result = [{"type": "text", "text": {"body": response}, "role" : "Assistant"}]

        for key, email in possible_email.items():
            if email in response:                
                email_inquiry_schema = update_email_inquiry(state, key)
                email_inquiry_response = {"type": "emailInquiry", "emailInquiry": email_inquiry_schema, "role" : "Assistant"}
                raw_result.append(email_inquiry_response)
                break
        result = json.dumps(raw_result)

    return {"messages": [result]}

def escalate_to_email(state: State):
    print("in escalate_to_email", state)

    question = state.schemas.general_qna.question

    llm = ChatOpenAI(model='gpt-4o',temperature=0.3)
    prompt = PromptTemplate.from_template(rephrase_subject_prompt)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    apology = chain.invoke({"question": question, "language": state.language})

    llm_type = ChatOpenAI(model='gpt-4o-mini',temperature=0)
    prompt_type = PromptTemplate.from_template(select_email_inquiry_type_prompt)
    output_parser_type = StrOutputParser()

    chain_type = prompt_type | llm_type | output_parser_type

    inquiry_type = chain_type.invoke({"question": question, "language": state.language})
    email_inquiry_schema = update_email_inquiry(state, inquiry_type)

    result = json.dumps([
        {"type": "text", "text": {"body": apology}, "role" : "Assistant"},
        {"type": "emailInquiry", "emailInquiry": email_inquiry_schema, "role" : "Assistant"},
    ])
    return {"messages": [result]}

def is_relevant_cond(state: State):
    print("in is_relevant", state)
    if len(state.schemas.general_qna.context_answers) > 0:
        return "answer"
    else:
        return "escalate_to_email"
