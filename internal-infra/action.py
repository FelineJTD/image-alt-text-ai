from datetime import datetime
from typing import List
import json
from pprint import pprint
import requests
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import do_action_promos_prompt, do_action_room_recommendation_prompt, rephrase_booking_request_prompt, infer_stay_reason_prompt
from utils import get_last_message, parse_messages
import pandas as pd
from urllib.parse import urlencode
from locales import cancel_reservation, promo_chat_bubble

def promos_action(category: str, chat_history: List[str], language: str):
	with open('offers.gql', 'r') as file:
		query = file.read()
	url = "https://cms4.ayana.com/graphql"
	variables = {"id": 80}

	headers = {
		"Content-Type": "application/json",
	}

	api_response = requests.post(
		url, 
		json={'query': query, 'variables': variables}, 
		headers=headers
	).json()

	components = api_response['data']['page']['data']['attributes']['blocks']
	offers_component = next(comp for comp in components if comp['__typename'] == 'ComponentPageOffers')

	promo_cards = []
	
	for item in offers_component['list']:
		offer = item['offer']['data']['attributes']
		lang_slug = "" if language == "en" else f"/{language}"

		if category.lower() == "general" or offer["web_tags_en"].lower() == category.lower():		
			promo_cards.append({
				"title": offer[f'title_{language}'],
				"description": offer[f'description_{language}'],
				"image": offer['desktop']['data']['attributes']['cdnURL'],
				"link": f"https://www.ayana.com{lang_slug}{offer['slug']}"
			})
	question = get_last_message(chat_history)
	llm = ChatOpenAI(model='gpt-4o-mini',temperature=0.2)

	is_promos_available = len(promo_cards) > 0
	promos_availability = "Yes" if is_promos_available else "No"

	prompt = PromptTemplate.from_template(do_action_promos_prompt)
	output_parser = StrOutputParser()

	chain = prompt | llm | output_parser

	response = chain.invoke({
		"category" : category,
		"question": question,
		"promos_availability": promos_availability,
		"language": language
	})

	result_array = [
		{"type": "text", "text": {"body": response}},
	]

	if is_promos_available:
		result_array.append({"type": "promoCards", "promoCards": promo_cards})

	result_array.append({"type": "text", "text": {"body": promo_chat_bubble[language]}})

	stringified_result = json.dumps(result_array)
	
	return stringified_result

def room_action(start_date: str, end_date: str, num_children: int, num_adults: int, num_rooms: int, chat_history: List[str], views: str, features: str, category: str, connectingRooms: bool, language: str):
	# Ayana Room Avail API endpoint
	base_url = "https://be.dev.ayana.com/api/v2/room_availabilities"
	
	# Convert dates to required format (assuming input is in ISO format: YYYY-MM-DD)
	date_from = datetime.fromisoformat(start_date).strftime("%Y-%m-%d")
	date_to = datetime.fromisoformat(end_date).strftime("%Y-%m-%d")
	
	params = {
		"date_from": date_from,
		"date_to": date_to,
		"adults": num_adults,
		"children": num_children,
		"location_code": "Bali",  # Assuming Bali is always the location
		"quantity": num_rooms
	}

	print("this is schema action", params)
	
	api_response = requests.get(base_url, params=params).json()
	room_cards = []

	link_params = {
				"location_code": "Bali",
				"start_date": start_date,
				"end_date": end_date,
				"adults_count": num_adults,
				"childs_count": num_children,
				"rooms": num_rooms,
	}
	default_link = "https://bookings.ayana.com/bookings/rooms"

	file_path = 'room_estate.csv'
	rooms_df = pd.read_csv(file_path)
	room_ids = []

	for room in api_response.get('data', []):
		room_ids.append((room.get('id')))

	rooms_df = rooms_df[rooms_df['Room ID'].isin(room_ids)]
	if views != None:
		rooms_df = rooms_df[rooms_df[views] == "V"]

	if category != None:
		rooms_df = rooms_df[rooms_df[category] == "V"]

	if connectingRooms:
		rooms_df = rooms_df[rooms_df['Connecting Room'] == "Y"]

	if features != None:
		formatted_features = [feature.strip() for feature in features.split(",")]
		for f in formatted_features:
			rooms_df = rooms_df[rooms_df[f] == "V"]

	room_info_dict = {
		row['Room ID']: {
				'Room Category': row['Room Category'],
				'Room Description': row['Room Description'],
				'Room Image': row['Room Image']
		}
		for _, row in rooms_df.iterrows()
	}

	recommended_room_ids = [room.get('id') for room in api_response.get('data', [])]

	for room in api_response.get('data', []):
		room_id = (room.get('id'))
		pprint(room_id)
		if room_id in room_info_dict:
			ordered_room_ids = [str(room_id)] + [str(id) for id in recommended_room_ids if id != room_id]
			query_params = urlencode({'room_ids': ','.join(ordered_room_ids)})
			full_url = f"{default_link}?{urlencode(link_params)}&{query_params}"
			formatted_room = {
				"name": room_info_dict[room_id]['Room Category'],
				"description": room_info_dict[room_id]['Room Description'],
				"price": (room.get('min_price', {}).get('formatted', '0')),
				"image": room_info_dict[room_id]['Room Image'],
				"link": full_url
			}
			room_cards.append(formatted_room)

	pprint(room_cards)
	try:
		history = parse_messages(chat_history)
	except Exception as e:
		print("Error in filtering text message")
		print(e)
	history_processed = "\n".join(history) 
	
	is_room_available = len(room_cards) > 0
	room_availability = "Yes" if is_room_available else "No"
	stay_reason_llm = ChatOpenAI(model='gpt-4o-mini',temperature=0.4)
	stay_reason_prompt = PromptTemplate.from_template(infer_stay_reason_prompt)
	output_parser = StrOutputParser()
	stay_reason_inference_chain = stay_reason_prompt | stay_reason_llm | output_parser
	stay_reason = stay_reason_inference_chain.invoke({
		"history" : history_processed
	})

	print("Stay reason:", stay_reason)
	
	llm = ChatOpenAI(model='gpt-4o-mini',temperature=0.2)
	prompt = PromptTemplate.from_template(do_action_room_recommendation_prompt)

	chain = prompt | llm | output_parser

	response = chain.invoke({
		"stay_reason" : stay_reason,
		"room_availability": room_availability,
		"language": language
	})

	result_array = [
		{"type": "text", "text": {"body": response}, "role" : "Assistant"},
		{"type": "roomCards", "roomCards": room_cards, "role" : "Assistant"}
	]

	stringified_result = json.dumps(result_array)
	
	return stringified_result

def email_inquiry_action(email: str, honorific: str, name: str, query: str, type: str, language: str):
	pprint(f"this is the type, type: {type}")
	type_to_recipient = {
		"wedding": "events.bali@ayana.com",
		"room_reservation": "reservation.bali@ayana.com",
		"restaurant": "fb.reservation@ayanaresort.com",
		"spa": "info-spa.bali@ayana.com",
		"general_information": "info.bali@ayana.com",
		"rewards": "info@ayanarewards.com"
	}
	default_recipient = "info.bali@ayana.com"

	recipient = type_to_recipient.get(type.lower(), default_recipient)

	formatted_type = ' '.join(word.capitalize() for word in type.split('_'))

	support_info = {
				"subject": "WebAI ChatBot Inquiry",
				"recipient": recipient,
				"name": f"{honorific} {name}",
				"email": email,
				"phone": "",
				"contact_me": "email",
				"general_inquiry_subject": formatted_type,
				"inquiry": query,
				"promotional": f"Sent from WebAI ChatBot",
				"wechat": None
		}
	
	url = "https://be1.ayana.com/api/v1/support/mail_to_ayana"
	headers = {"Content-Type": "application/json"}
	response = requests.post(url, json={"support_info": support_info}, headers=headers)

	pprint("this is email response")
	pprint(response.json())

	# Confirmation messages in different languages
	confirmation_messages = {
		"en": [
			"Your inquiry has been sent. Please wait for a reply from our team.",
			"Anything else we can help with?"
		],
		"zh": [
			"您的询问已发送。请等待我们团队的回复。",
			"还有什么我们可以帮忙的吗？"
		],
		"ja": [
			"お問い合わせを送信しました。チームからの返信をお待ちください。",
			"他に何かお手伝いできることはありますか？"
		],
		"ko": [
			"문의가 전송되었습니다. 답변을 기다려주세요.",
			"다른 도움이 필요하신가요?"
		]
	}

	return json.dumps([
		{"type": "text", "text": {"body": confirmation_messages[language][0]}, "role" : "Assistant"},
		{"type": "text", "text": {"body": confirmation_messages[language][1]}, "role" : "Assistant"}
	])

def manage_booking_action(chat_history: List[str], language: str):
	request = get_last_message(chat_history)
	llm = ChatOpenAI(model='gpt-4o-mini',temperature=0.6)
	prompt = PromptTemplate.from_template(rephrase_booking_request_prompt)
	output_parser = StrOutputParser()

	chain = prompt | llm | output_parser

	response = chain.invoke({
		"request": request,
		"language": language
	})
	return json.dumps([
		{"type": "manageBooking", "manageBooking": {"url": "https://bookings.ayana.com/bookings/find-reservation/", "text": response}, "role" : "Assistant"}
	])

def cancel_reservation_action(last_name: str, reservation_id: str, language: str):

		is_found = int(reservation_id) % 2 != 0
		
		# Mock cancellation process
		if is_found:
				is_refundable = int(reservation_id) % 3 == 0
				if is_refundable:
						return json.dumps([
							{"type": "manageBooking", "manageBooking": {"url": "https://bookings.ayana.com/bookings/find-reservation/", "text": cancel_reservation["refundable"][language]}, "role" : "Assistant"}
						])
				else:
						return json.dumps([
						{"type": "text", "text": {"body": cancel_reservation["not_refundable"][language]}, "role" : "Assistant"},
						{"type": "emailInquiry", "emailInquiry": {"email": None, "name": last_name, "query": cancel_reservation["not_refundable_query"][language], "type": "room_reservation", "honorific": None, "reservationId": reservation_id}, "role" : "Assistant"}
				])
		else:
				return json.dumps([
								{"type": "text", "text": {"body": cancel_reservation["not_found"][language]}, "role" : "Assistant"},
								{"type": "emailInquiry", "emailInquiry": {"email": None, "name": last_name, "query": cancel_reservation["not_found_query"][language], "type": "room_reservation", "honorific": None, "reservationId": reservation_id}, "role" : "Assistant"}
						])
				
