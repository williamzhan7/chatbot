# Example request:
# curl -X POST -H "Content-Type: application/json" -d '{"query": "{your_query}"}' http://127.0.0.1:5000/query

import argparse
from flask import Flask, request, jsonify
import requests
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
import getpass
import os
from langchain_openai import ChatOpenAI
import json

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory



@tool
def create_booking(api_key, event_type_id: int, start: str, name: str, email: str, location_value: str, location_option_value: str, metadata: object, time_zone: str, language: str, 
                 end: str=None, title: str=None, recurring_event_id: int=None, description: str=None, status: str=None, seats_per_time_slot: int=None,
                 seats_show_attendees: bool=None, seats_show_availability_count: bool=None, sms_reminder_number: int=None):
    """
    books a meeting
    api key, event_type_id, start, name, email, location_value, location_option_value, metadata, time_zone, language are required.
    end, title, recurring_event_id, description, status, seats_per_time_slot, seats_show_attendees, seats_show_availability_count, sms_reminder_number are optional.
    """
    url = f"https://api.cal.com/v1/bookings"
    params = {
        "apiKey": api_key
    }
    data = {
        "eventTypeId": event_type_id,
        "start": start,
        "responses": {
            "name": name,
            "email": email,
            "location": {
                "value": location_value,
                "optionValue": location_option_value
            }
        },
        "end": end,
        "metadata": metadata,
        "timeZone": time_zone,
        "language": language,
        "title": title,
        "recurringEventId": recurring_event_id,
        "description": description,
        "status": status,
        "seatsPerTimeSlot": seats_per_time_slot,
        "seatsShowAttendees": seats_show_attendees,
        "seatsShowAvailabilityCount": seats_show_availability_count,
        "smsReminderNumber": sms_reminder_number
    
    }

    #remove optional arguments that have not been provided
    data = {k: v for k, v in data.items() if v is not None}
    
    response = requests.post(url, params=params, json=data)

    return response.json()

@tool
def find_all_bookings(api_key, user_id=None, take=None, page=None, attendee_email=None):
    """
    finds all bookings
    api_key is required. 
    user_id, take, page, attendee_email are optional.
    """
    url = f"https://api.cal.com/v1/bookings"
    params = {
        "apiKey": api_key,
        "user_id": user_id,
        "take": take,
        "page": page,
        "attendee_email": attendee_email
    }

    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, params=params)

    return response.json()

@tool
def get_all_bookable_slots(api_key, start, end, time_zone=None, event_type_id=None, username_list=None, event_type_slug=None):
    """
    gets all bookable slots
    api_key, start, end are required parameters.
    Either event_type_id must be provided, or both username_list and event_type_slug must be provided.
    time_zone is optional.
    """
    url = f"https://api.cal.com/v1/slots"
    params = {
        "apiKey": api_key,
        "startTime": start,
        "endTime": end,
        "eventTypeId": event_type_id,
        "timeZone": time_zone,
        "usernameList": username_list,
        "eventTypeSlug": event_type_slug
    }
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, params=params)

    return response.json()

@tool
def cancel_booking(api_key, id, all_remaining_bookings=None, cancellation_reason=None):
    """
    cancels a booking
    api_key, id are required.
    all_remaining_bookings, cancellation_reason are optional.

    """
    url = f"https://api.cal.com/v1/bookings/{id}/cancel"
    params = {
        "apiKey": api_key,
        "allRemainingBookings": all_remaining_bookings,
        "cancellationReason": cancellation_reason
    }

    params = {k: v for k, v in params.items() if v is not None}

    response = requests.delete(url, params=params)

    return response.json()

@tool
def edit_booking(api_key, id, title=None, start=None, end=None, status=None, description=None):
    """
    edits a booking
    api_key, id are required.
    title, start, end, status, description are optional.

    """
    url = f"https://api.cal.com/v1/bookings/{id}"
    params = {
        "apiKey": api_key,
    }
    data = {
        "title": title,
        "start": start,
        "end": end,
        "status": status,
        "description": description
    }
    data = {k: v for k, v in data.items() if v is not None}
    response = requests.patch(url, params=params, data=data)

    return response.json()



def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
        instruct = "Pay attention to the function doc comment to determine what parameters the user needs to provide. If they have not provided enough\
                information to be satisfactory, do not tool call and prompt the user for the missing information.\
                Always mention to the user which parameters are optional. If the user gives a default argument, use it instead of the default.\
                Before tool calling, always review what arguments will be used for the function call.\
                Always prompt the user before reusing any arguments the user has previously provided for multiple calls. They may or may not want to change the arguments."    
        store[session_id].add_user_message(instruct)       
    return store[session_id]



app = Flask(__name__)

# POST endpoint
@app.route('/query', methods=['POST'])
def process_query():
    # Extract JSON data from the request
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract parameters from the JSON data
    query = data.get('query')

    if not isinstance(query, str):
        return jsonify({'error': 'Query must be a string'}), 400
    
    # Additional instructions for model to add to query
    
    
    
    # Initialize tool_messages to store tool outputs, config for message history
    tool_messages = []
    config = {"configurable": {"session_id": "abc4"}}

    # Query the model
    ai_msg = llm_with_message_history.invoke(query, config=config)

    # If model decides to tool call
    if ai_msg.tool_calls:
        
        # For every tool call
        for tool_call in ai_msg.tool_calls:

            # Get the tool the model selected, run the tool with the llm selected parameters, add outputs (ToolMessages) to messages
            selected_tool = {"get_all_bookable_slots": get_all_bookable_slots, "create_booking": create_booking, "find_all_bookings": find_all_bookings, "cancel_booking": cancel_booking, "edit_booking": edit_booking}[tool_call["name"].lower()]

            tool_output = selected_tool.invoke(tool_call["args"])

            tool_messages.append(ToolMessage(json.dumps(tool_output), tool_call_id=tool_call["id"]))

        # Feed ToolMessages back to model
        ai_msg = llm_with_message_history.invoke(tool_messages, config)
    
    response = {
        'response': ai_msg.pretty_repr(),
    }
    
    # Return the response as JSON
    return jsonify(response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the script with your OPENAI API key.")
    parser.add_argument('--apikey', type=str, help='Your API key', required=True)
    args = parser.parse_args()
    os.environ["OPENAI_API_KEY"] = args.apikey

    global llm_with_message_history
    llm = ChatOpenAI(model="gpt-4o") #can specify different model

    #create llm, bind tools, enable message history
    tools = [create_booking,get_all_bookable_slots,find_all_bookings,cancel_booking,edit_booking]
    llm_with_tools = llm.bind_tools(tools)
    llm_with_message_history = RunnableWithMessageHistory(llm_with_tools, get_session_history)

    store = {}

    
    app.run(port=5000)
