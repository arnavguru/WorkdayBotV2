import collections
import json

from dictionaries import missing_item_dict, missing_item_slots, missing_item_functions, phone_country_code_dict, \
    error_handler, work_style_dict, locations_dict, states_dict
from global_variables import company_name, chatbot_name, company_portal
from slack_info import get_slack_email
from workday_web_services import human_resources, custom_reports, staffing


# Responses

def close(session_attributes, message):
    """
    Return a response to Lex with no further input from user

    :param session_attributes: Values to be stored across multiple intents
    :param message: Message to be returned to the user
    :return: JSON message for Lex ending current conversation
    """
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': "Fulfilled",
            'message': {
                "contentType": "PlainText",
                "content": message
            }
        }
    }

    print('####CLOSE')
    print((str(response).replace('\'', '"')).replace('None', 'null'))

    return response


def delegate(session_attributes, slots):
    """
    Return the session attributes to Lex for use in configured responses.
    Used in cases where response is fixed with certain dynamic parts.

    :param session_attributes: Values to be stored across multiple intents
    :param slots: Slots for the current intent in use
    :return: JSON message with updated session attributes and slots for response configured on Lex
    """
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            "slots": slots,
        }
    }

    print('####DELEGATE')
    print((str(response).replace('\'', '"')).replace('None', 'null'))

    return response


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Return a response to Lex for user to provide value for a slot.

    :param session_attributes: Values to be stored across multiple intents
    :param intent_name: Intent being used to fetch information from user
    :param slots: Slots for the current intent in use
    :param slot_to_elicit: Slot to be prompted for user input
    :param message: Prompt message to be returned to the user
    :return: JSON message for Lex prompting user to provide value for a slot
    """
    response = {
        'sessionAttributes': session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "message": {
                "contentType": "PlainText",
                "content": message
            },
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit
        }
    }

    print('####ELICIT_SLOT')
    print((str(response).replace('\'', '"')).replace('None', 'null'))

    return response


# Standalone functions

def get_slots(intent_request):
    """
    Returns a dictionary with slot names and values

    :param intent_request: JSON message from Lex
    :return: Dictionary of slot names and their values
    """
    return intent_request['currentIntent']['slots']


def get_session_attributes(event):
    """
    Returns a dictionary with session attribute names and values.
    Returns None if there are no attributes.

    :param event: JSON message from Lex
    :return: Dictionary of session attributes names and their values or None if no attributes are available
    """
    try:
        session_attributes = event['sessionAttributes']
        if session_attributes is None:
            raise KeyError
    except KeyError:
        session_attributes = {}

    return session_attributes


def validate_empid(session_attributes):
    """
    Returns True if Employee ID is available in Session Attributes. Returns False if missing.

    :param session_attributes: Session attributes from Lex JSON message
    :return: If emp_id attribute sis present then returns True otherwise False
    """
    if session_attributes is not None:
        return session_attributes.__contains__('emp_id')
    else:
        return False


def get_emp_id_slack(event):
    """
    Returns the Workday employee id.
    Requests Slack user email id using the user id from the Lex message.
    Requests Workday employee id from custom report using the slack email id.

    Returns 'Not Found' if value is not available from either Slack API or Workday.

    Based on assumption that Slack email id and Workday primary work email address are same.

    :param event: JSON message from Lex
    :return: Returns Workday Employee ID using the Slack User ID. Returns 'Not Found' if Employee ID is not found
    """
    if event['requestAttributes']['x-amz-lex:channel-type'].__contains__('Slack'):
        emp_email_id = get_slack_email(event)
        emp_id = custom_reports.get_emp_id_from_email(emp_email_id)
        if emp_id is not None:
            return emp_id
        else:
            return "Not Found"
    else:
        return "Not Found"


def get_emp_id(event):
    session_attributes = get_session_attributes(event)
    slots = get_slots(event)

    if validate_empid(session_attributes):
        emp_id = session_attributes['emp_id']
        return emp_id

    elif slots.__contains__("EmployeeID") and slots["EmployeeID"] is not None:
        emp_id = slots["EmployeeID"]
        return emp_id

    elif event['requestAttributes'] is not None:
        if event['requestAttributes']['x-amz-lex:channel-type'].__contains__('Slack'):
            emp_id = get_emp_id_slack(event)
            if emp_id != "Not Found":
                return emp_id
            else:
                message = "Unable to find you in Workday. Please check if your Slack email address is same as your " \
                          "work email address in Workday"
                return close(session_attributes, message)
        else:
            message = f"{event['requestAttributes']['x-amz-lex:channel-type']} is not supported at the moment."
            return close(session_attributes, message)

    else:
        message = "Please provide your Employee ID"
        return elicit_slot(session_attributes, 'Greeting', {"EmployeeID": None}, 'EmployeeID', message)


def get_emp_first_name(event):
    session_attributes = get_session_attributes(event)

    if session_attributes.__contains__('first_name') and session_attributes['first_name'] is not None:
        return session_attributes['first_name']
    else:
        emp_id = get_emp_id(event)
        if type(emp_id) == dict:
            return emp_id

        workday_response, status_code = human_resources.get_workers(str(emp_id))

        if status_code == 200:
            first_name = \
                workday_response['env:Envelope']['env:Body']['wd:Get_Workers_Response']['wd:Response_Data'][
                    'wd:Worker']['wd:Worker_Data']['wd:Personal_Data']['wd:Name_Data']['wd:Preferred_Name_Data'][
                    'wd:Name_Detail_Data']['wd:First_Name']

            return first_name

        else:
            message = f"Employee ID {emp_id} was not found in Workday. Please provide a valid Employee ID"
            return elicit_slot(session_attributes, 'Greeting', {"EmployeeID": None}, 'EmployeeID',
                               message)


def get_emp_country(event, emp_id):
    session_attributes = get_session_attributes(event)

    if session_attributes.__contains__('emp_country') and session_attributes['emp_country'] is not None:
        return session_attributes['emp_country']
    else:
        workday_response, status_code = human_resources.get_workers(str(emp_id))

        if status_code == 200:
            worker_country_id_list = \
                workday_response['env:Envelope']['env:Body']['wd:Get_Workers_Response']['wd:Response_Data'][
                    'wd:Worker'][
                    'wd:Worker_Data']['wd:Personal_Data']['wd:Name_Data']['wd:Preferred_Name_Data'][
                    'wd:Name_Detail_Data'][
                    'wd:Country_Reference']['wd:ID']
            worker_country = \
                next((item for item in worker_country_id_list if item['@wd:type'] == 'ISO_3166-1_Alpha-3_Code'), None)[
                    '#text']

            return worker_country

        else:
            message = f"Employee ID {emp_id} was not found in Workday. Please provide a valid Employee ID"
            return elicit_slot(session_attributes, 'Greeting', {"EmployeeID": None}, 'EmployeeID',
                               message)


def fetch_missing_data(missing_data_report):
    missing_data_list = {}
    num = 1

    if type(missing_data_report) == collections.OrderedDict:
        missing_data_report.pop('wd:Employee_ID')
        for key in missing_data_report.keys():
            if missing_data_report[key] == '1':
                key = key.split(':')[1]
                missing_data_list[str(num)] = key
                num += 1

    if len(missing_data_list.keys()) == 0:
        missing_data_list = None

    return missing_data_list


def update_session_attributes(session_attributes, new_attributes):
    for key in new_attributes.keys():
        session_attributes[key] = new_attributes[key]

    return session_attributes


def format_slot_value(event, emp_id, missing_slot, slot_value):
    if missing_slot == 'Mail':
        if slot_value.__contains__('mailto'):
            slot_value = str(slot_value).split(':', 2)[-1]
    elif missing_slot == 'Phone':
        slot_value = phone_country_code_dict[get_emp_country(event, emp_id)] + ':' + slot_value
    else:
        slot_value = slot_value

    return slot_value


# Intent Handlers

def reset_all_attributes(event):
    session_attributes = get_session_attributes(event)
    slots = get_slots(event)

    session_attributes_copy = session_attributes.copy()

    for key in session_attributes_copy.keys():
        if key not in ['chatbot_name', 'company_name', 'first_name', 'emp_id']:
            session_attributes.pop(key)

    return delegate(session_attributes, slots)


def generate_attributes(event):
    session_attributes = get_session_attributes(event)
    slots = get_slots(event)

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    first_name = get_emp_first_name(event)

    if type(first_name) == dict:
        return first_name

    new_attributes = {
        'emp_id': emp_id,
        'first_name': first_name,
        'company_name': company_name,
        'chatbot_name': chatbot_name
    }
    session_attributes = update_session_attributes(session_attributes, new_attributes)

    return delegate(session_attributes, slots)


def change_preferred_name(event):
    session_attributes = get_session_attributes(event)
    current_intent = event['currentIntent']['name']
    slots = get_slots(event)

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    emp_country = get_emp_country(event, emp_id)

    first_name = slots['PrefFirstName']
    last_name = slots['PrefLastName']

    if first_name is None:
        message = 'Please provide your preferred first name'
        return elicit_slot(session_attributes, current_intent, slots, 'PrefFirstName', message)

    if last_name is None:
        message = 'Please provide your preferred last name'
        return elicit_slot(session_attributes, current_intent, slots, 'PrefLastName', message)

    middle_name = ''
    full_name = f'{first_name} {last_name}'

    workday_response, status_code = \
        human_resources.change_preferred_name(emp_id, emp_country, first_name, middle_name, last_name)

    if status_code == 200:
        message = f"Your preferred name has been changed to {full_name}"
        new_attributes = {
            'emp_country': emp_country,
            'first_name': first_name,
        }
        session_attributes = update_session_attributes(session_attributes, new_attributes)

    else:
        message = workday_response['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
        message += '\nPlease contact HR to complete this action'

    return close(session_attributes, message)


def change_business_title(event):
    session_attributes = get_session_attributes(event)
    current_intent = event['currentIntent']['name']
    slots = get_slots(event)

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    business_title = slots['NewBusinessTitle']

    if business_title is None:
        message = 'Please provide your new business title'
        return elicit_slot(session_attributes, current_intent, slots, 'NewBusinessTitle', message)

    worker_position = custom_reports.get_primary_position(emp_id)

    workday_response, status_code = human_resources.change_business_title(emp_id, worker_position, business_title)

    if status_code == 200:
        message = f"Your business title has been changed to {business_title}"
    else:
        message = workday_response['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
        message += '\nPlease contact HR to complete this action'

    return close(session_attributes, message)


def day_one_setup(event):
    session_attributes = get_session_attributes(event)
    message = 'Yet to be Implemented'

    return close(session_attributes, message)


def disability_details_update(event):
    session_attributes = get_session_attributes(event)

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    emp_country = get_emp_country(event, emp_id)

    if type(emp_country) == dict:
        return emp_country

    disability_portal = f"{company_portal}{str(emp_country).lower()}/personalinfo/"

    new_attributes = {
        'emp_country': emp_country,
        'company_name': company_name,
        'url': disability_portal
    }
    session_attributes = update_session_attributes(session_attributes, new_attributes)

    return delegate(session_attributes, slots={})


def update_missing_info(event):
    session_attributes = get_session_attributes(event)
    current_intent = event['currentIntent']['name']
    slots = get_slots(event)
    user_choice = slots['UserChoice']

    try:
        continue_update = session_attributes['update_in_progress']
    except KeyError:
        continue_update = None

    try:
        missing_data = session_attributes['missing_personal_info']
        missing_data = json.loads(missing_data)
    except KeyError:
        missing_data = None

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    first_name = get_emp_first_name(event)

    if missing_data is None and user_choice is None:
        missing_data_report = custom_reports.get_missing_data(emp_id)

        if missing_data_report is None:
            message = "Unable to validate your information on Workday. Please reach out to HR for verify your " \
                      "personal information"

            new_attributes = {
                'emp_id': emp_id
            }
            session_attributes = update_session_attributes(session_attributes, new_attributes)

            return close(session_attributes, message)

        else:
            missing_data = fetch_missing_data(missing_data_report)

            if missing_data is None:
                message = "All of your required information is up to date."

                new_attributes = {
                    'emp_id': emp_id,
                    'missing_personal_info': None
                }
                session_attributes = update_session_attributes(session_attributes, new_attributes)

                return close(session_attributes, message)

            else:
                missing_item_keys = missing_data.keys()
                missing_item_values = missing_data.values()

                message = f'Hi {first_name},\nYou would now be aware that we are enabling work-from-home arrangements' \
                          f' in response to the COVID-19 pandemic.\n\n'

                if len(missing_item_keys) == 1:
                    missing_item = missing_item_dict[missing_item_values.__iter__().__next__()]
                    message += f"I see your {missing_item.lower()} is not updated in your Workday profile.\n" \
                               f"Would you like to update it now? [Yes/No]"

                    new_attributes = {
                        'emp_id': emp_id,
                        'missing_personal_info': json.dumps(missing_data),
                        'update_missing_data_choice': None
                    }
                    session_attributes = update_session_attributes(session_attributes, new_attributes)

                    return elicit_slot(session_attributes, current_intent, slots, "UserChoice", message)

                else:
                    message += "I see that the below items are missing:\n"
                    for key in missing_item_keys:
                        missing_item = missing_item_dict[missing_data[key]]
                        message += str(key) + ". " + missing_item + '\n'
                    message += "\nWould you like to update it now? [Yes/No]"

                    new_attributes = {
                        'emp_id': emp_id,
                        'missing_personal_info': json.dumps(missing_data),
                        'update_missing_data_choice': None
                    }
                    session_attributes = update_session_attributes(session_attributes, new_attributes)

                    return elicit_slot(session_attributes, current_intent, slots, "UserChoice", message)

    elif missing_data is not None and \
            (user_choice is not None or continue_update is not None):
        if user_choice == 'No' or user_choice == 'no':
            message = "No worries. We can update it later"

            new_attributes = {
                'emp_id': emp_id,
                'missing_personal_info': None,
                'update_missing_data_choice': None,
                'update_in_progress': None
            }
            session_attributes = update_session_attributes(session_attributes, new_attributes)

            return close(session_attributes, message)

        elif user_choice == 'Yes' or user_choice == 'yes' or continue_update == '1':
            message = ''
            if user_choice == 'Yes':
                message += 'Ok! Let\'s do it.\n'

            missing_item_keys = missing_data.keys()
            missing_item_values = missing_data.values()

            missing_value = missing_item_values.__iter__().__next__()
            missing_key = missing_item_keys.__iter__().__next__()
            missing_slot = missing_item_slots[missing_value]
            missing_item = missing_item_dict[missing_value]

            # new_logic

            # single_slot_updates
            if missing_item in ['Home Phone Number', 'Home Email']:
                if slots[missing_slot] is None:
                    message += f"\nPlease provide your {missing_item.lower()}"
                    return elicit_slot(session_attributes, current_intent, slots, missing_slot, message)
                else:
                    slot_value = slots[missing_slot]

                    if missing_slot == 'Mail':
                        if slot_value.__contains__('mailto'):
                            slot_value = str(slot_value).split(':', 2)[-1]
                    elif missing_slot == 'Phone':
                        slot_value = phone_country_code_dict[get_emp_country(event, emp_id)] + ':' + slot_value
                    else:
                        slot_value = slot_value

                    workday_response, status_code = missing_item_functions[missing_value](emp_id, 'HOME', slot_value)

                    if status_code == 200:
                        message = f"Your {missing_item.lower()} has been updated successfully."
                    else:
                        message = workday_response['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault'][
                            'faultstring']
                        message += '\nPlease login into Workday or contact HR to complete this action'

            # multiple_slots_updates
            else:
                message = 'Development for missing data needing multiple slots to update is in progress'

                return close(session_attributes, message)

            missing_data.pop(missing_key)
            missing_item_keys = missing_data.keys()
            missing_item_values = missing_data.values()

            if len(missing_item_keys) == 0:
                message += "\n\nThanks for sharing the requested information."

                new_attributes = {
                    'emp_id': emp_id,
                    'missing_personal_info': None,
                    'update_missing_data_choice': None,
                    'update_in_progress': None
                }
                session_attributes = update_session_attributes(session_attributes, new_attributes)

                return close(session_attributes, message)

            else:
                missing_value = missing_item_values.__iter__().__next__()
                missing_slot = missing_item_slots[missing_value]
                missing_item = missing_item_dict[missing_value]

                new_attributes = {
                    'emp_id': emp_id,
                    'missing_personal_info': json.dumps(missing_data),
                    'update_missing_data_choice': '1',
                    'update_in_progress': '1'
                }
                session_attributes = update_session_attributes(session_attributes, new_attributes)

                message += f"\n\nPlease provide your {missing_item.lower()}"
                return elicit_slot(session_attributes, current_intent, slots, missing_slot, message)

        else:
            message = "Please respond no either 'Yes' or 'No'"

            return elicit_slot(session_attributes, current_intent, slots, "UserChoice", message)

    else:
        event['sessionAttributes']["missing_personal_info"] = None
        event['sessionAttributes']["update_in_progress"] = None
        event['sessionAttributes']["update_missing_data_choice"] = None

        return update_missing_info(event)


def bot_intro(event):
    session_attributes = get_session_attributes(event)
    slots = get_slots(event)

    new_attributes = {
        'company_name': company_name,
        'chatbot_name': chatbot_name
    }
    session_attributes = update_session_attributes(session_attributes, new_attributes)

    return delegate(session_attributes, slots)


def suggest_utterance(event):
    """

    :param event: JSON message from Lex
    :return: Alternative utterances similar to current query
    """
    session_attributes = get_session_attributes(event)
    keywords = error_handler.keys()
    utterance = str(event["inputTranscript"]).lower()

    alternates = None

    for word in keywords:
        if utterance.lower().__contains__(word):
            alternates = error_handler[word]

    if alternates is None:
        message = "Sorry, I am unable to help you with this. Please reach out to HR."
    else:
        message = "Your query looks similar to a query I have answers to.\n Please try entering the below query\n"
        if len(alternates) == 1:
            message += ("\"" + alternates[0] + "\"" + "\n")
        else:
            for line in alternates:
                message += ("\"" + line + "\"" + "\n")

    return close(session_attributes, message)


def update_home_email(event):
    session_attributes = get_session_attributes(event)
    current_intent = event['currentIntent']['name']
    slots = get_slots(event)

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    email_address = slots['EmailID']

    if email_address is None:
        message = 'Please provide your new home email address'
        return elicit_slot(session_attributes, current_intent, slots, 'EmailID', message)

    workday_response, status_code = human_resources.change_home_contact_information_email(emp_id, 'HOME', email_address)

    if status_code == 200:
        message = f"Your email address has been changed to {email_address}"
    else:
        message = workday_response['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
        message += '\nPlease contact HR to complete this action'

    return close(session_attributes, message)


def worker_checkin(event):
    session_attributes = get_session_attributes(event)
    current_intent = event['currentIntent']['name']
    slots = get_slots(event)

    try:
        custom_location = session_attributes['custom_location']
    except KeyError:
        custom_location = None

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    first_name = get_emp_first_name(event)

    work_style = str(slots['WorkStyle'])
    location = str(slots['Location'])
    confirm = str(slots['Confirm'])

    if work_style.lower() == 'none':
        message = 'Where are you working from today?\nPlease enter the LETTER beside the option that best describes ' \
                  'your work location today:\n\nA) Working from home\nB) Working from office\nC) Working from client' \
                  ' location\nD) On Personal Time Off'

        new_attributes = {
            'emp_id': emp_id,
            'first_name': first_name,
        }
        session_attributes = update_session_attributes(session_attributes, new_attributes)

        return elicit_slot(session_attributes, current_intent, slots, 'WorkStyle', message)

    if work_style.lower() not in ['a', 'b', 'c', 'd']:
        message = f"'{work_style}' is not a valid choice. Please select by entering the letter corresponding to the " \
                  f"relevant option\n\nA) Working from home\nB) Working from office\nC) Working from client " \
                  "location\nD) On Personal Time Off"

        new_attributes = {
            'emp_id': emp_id,
            'first_name': first_name,
        }
        session_attributes = update_session_attributes(session_attributes, new_attributes)

        return elicit_slot(session_attributes, current_intent, slots, 'WorkStyle', message)

    if location.lower() == 'none':
        message = 'What location are you working in today? Please enter the LETTER next to the option that best ' \
                  'describes your location:\n\nA) Bengaluru\nB) Hyderabad\nC) Pune\nD) Chennai\nE) Gurugram\n' \
                  'F) Mumbai\nG) Kolkata\nH) Noida\nI) New Delhi\nJ) Others'

        return elicit_slot(session_attributes, current_intent, slots, 'Location', message)

    if location.lower() not in ['a', 'b', 'c', 'd' 'e', 'f', 'g', 'h', 'i', 'j'] and custom_location is None:
        message = f"'{location}' is not a valid choice. Please enter the LETTER next to the option that best " \
                  f"describes your location:\n\nA) Bengaluru\nB) Hyderabad\nC) Pune\nD) Chennai\nE) Gurugram\n" \
                  f"F) Mumbai\nG) Kolkata\nH) Noida\nI) New Delhi\nJ) Others"

        new_attributes = {
            'emp_id': emp_id,
            'first_name': first_name,
            'custom_location': None
        }
        session_attributes = update_session_attributes(session_attributes, new_attributes)

        return elicit_slot(session_attributes, current_intent, slots, 'Location', message)

    if location.lower() == 'j':
        message = 'Looks like the place you are looking for is not my provided list. Please enter the name of the ' \
                  'city/town you are currently in:'

        new_attributes = {
            'custom_location': '1'
        }
        session_attributes = update_session_attributes(session_attributes, new_attributes)

        return elicit_slot(session_attributes, current_intent, slots, 'Location', message)

    work_style = work_style_dict[work_style.lower()]
    if location.lower() in locations_dict.keys():
        location = locations_dict[location.lower()]

    if confirm.lower() == 'none':
        message = f"I've noted that your current work location is: {work_style}, in {location}.\n" \
                  f"If you have the computer, internet, and work instructions to continue your work, please end the " \
                  f"chat by typing: DONE\nIf you need to let me know you help with computer, internet, or work " \
                  f"instructions, type: NEXT"

        return elicit_slot(session_attributes, current_intent, slots, 'Confirm', message)

    elif confirm.lower() not in ['done', 'next']:
        message = "That's not a valid choice. Please enter either DONE or NEXT to proceed further."

        return elicit_slot(session_attributes, current_intent, slots, 'Confirm', message)

    else:
        workday_response, status_code = staffing.edit_worker_additional_data(emp_id, work_style + ':' + location)

        if status_code == 200:
            if confirm.lower() == 'done':
                message = "Thanks for checking in.\n\nFinally, here is the HR Message of the day:\nAll GMS employees" \
                          " who have travelled internationally for either business or personal reasons are to remain" \
                          " at home for the first 14 days after returning. During that time, please do not report to" \
                          " GMS or client offices. If unable to work from home during that time, please consult with" \
                          " your supervisor or HR lead. \n Please check-in again tomorrow"

            else:
                message = "Thanks for checking in. \n\nPlease contact GMS IT Support for any help required with " \
                          "computer, internet or work setup. You can reach to them over Slack or call 1800 123 " \
                          "123456. \n Please check-in again tomorrow"

            return close(session_attributes, message)

        else:
            message = workday_response['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
            message += '\nPlease contact HR to complete this action'

            return close(session_attributes, message)


def update_emergency_contact(event):
    session_attributes = get_session_attributes(event)
    current_intent = event['currentIntent']['name']
    slots = get_slots(event)

    update_details = False

    if slots['Update'] is not None and slots['Update'].lower() == 'yes':
        update_details = True
        session_attributes['update_details'] = '1'

    elif slots['Update'] is not None and slots['Update'].lower() == 'no':
        message = 'Thanks for confirming the details.'
        return close(session_attributes, message)

    elif session_attributes.__contains__('update_details') and session_attributes['update_details'] is not None:
        if session_attributes['update_details'] == '1':
            update_details = True
        else:
            update_details = False

    try:
        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'Update':
            if str(event['inputTranscript']).lower() == 'yes':
                update_details = True
                slots['Update'] = 'yes'
                session_attributes['update_details'] = '1'
            elif str(event['inputTranscript']).lower() == 'no':
                message = 'Thanks for confirming the details.'
                return close(session_attributes, message)
    except KeyError:
        pass

    emp_id = get_emp_id(event)

    if type(emp_id) == dict:
        return emp_id

    if update_details is False:
        current_emergency_details, get_workers_status_code = human_resources.get_workers(emp_id)

        if get_workers_status_code == 200:
            first_related_person = None
            try:
                first_related_person_list = \
                    current_emergency_details['env:Envelope']['env:Body']['wd:Get_Workers_Response'][
                        'wd:Response_Data']['wd:Worker']['wd:Worker_Data']['wd:Related_Person_Data'][
                        'wd:Related_Person']

                for person in first_related_person_list:
                    if 'wd:Emergency_Contact' in person.keys():
                        first_related_person = person

            except KeyError:
                first_related_person = None

            if first_related_person is not None:
                related_person_name = \
                    first_related_person['wd:Personal_Data']['wd:Name_Data']['wd:Preferred_Name_Data'][
                        'wd:Name_Detail_Data']['@wd:Formatted_Name']

                try:
                    related_person_address = \
                        first_related_person['wd:Personal_Data']['wd:Contact_Data']['wd:Address_Data'][
                            '@wd:Formatted_Address'].replace('&#xa;', ',')
                except KeyError:
                    related_person_address = 'Not Available'

                try:
                    related_person_phone = first_related_person['wd:Personal_Data']['wd:Contact_Data']['wd:Phone_Data'][
                        '@wd:International_Formatted_Phone']
                except KeyError:
                    related_person_phone = 'Not Available'

                try:
                    related_person_email = first_related_person['wd:Personal_Data']['wd:Contact_Data'][
                        'wd:Email_Address_Data']['wd:Email_Address']
                except KeyError:
                    related_person_email = 'Not Available'

                message = f'Your current emergency details are as follows:\n\nContact Name: {related_person_name}\n\n' \
                          f'Address: {related_person_address}\n\nPhone number: {related_person_phone}\n\n Email ID:' \
                          f' {related_person_email}\n\nWould you like to update this information? [YES/NO]'

            else:
                message = "Your emergency contact details are not available on Workday.\nWould you like to update " \
                          "this information? [YES/NO]"

            new_attributes = {
                'emp_id': emp_id,
                'update_details': None
            }
            session_attributes = update_session_attributes(session_attributes, new_attributes)

            return elicit_slot(session_attributes, current_intent, slots, 'Update', message)

        else:
            message = current_emergency_details['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']

            new_attributes = {
                'emp_id': emp_id,
                'update_details': None
            }
            session_attributes = update_session_attributes(session_attributes, new_attributes)

            return close(session_attributes, message)

    else:
        country = get_emp_country(event, emp_id)

        relation_type = slots['Relation']

        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'Relation':
            slots['Relation'] = str(event['inputTranscript']).lower()
            relation_type = str(event['inputTranscript']).lower()

        if relation_type is None:
            message = 'Please specify the relationship (Father, Mother, Spouse, Child, etc)'
            return elicit_slot(session_attributes, current_intent, slots, 'Relation', message)

        relation_type = str(relation_type).capitalize()

        relative_first_name = slots['RelativeFirstName']

        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'RelativeFirstName':
            slots['RelativeFirstName'] = str(event['inputTranscript']).capitalize()
            relative_first_name = str(event['inputTranscript']).capitalize()

        if relative_first_name is None:
            message = 'Please provide the first name of the contact:'
            return elicit_slot(session_attributes, current_intent, slots, 'RelativeFirstName', message)

        relative_last_name = slots['RelativeLastName']

        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'RelativeLastName':
            slots['RelativeLastName'] = str(event['inputTranscript']).capitalize()
            relative_last_name = str(event['inputTranscript']).capitalize()

        if relative_last_name is None:
            message = 'Please provide the last name of the contact:'
            return elicit_slot(session_attributes, current_intent, slots, 'RelativeLastName', message)

        postal_code = slots['PostalCode']

        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'PostalCode':
            slots['PostalCode'] = str(event['inputTranscript']).lower()
            postal_code = str(event['inputTranscript']).lower()

        if postal_code is None:
            message = 'Please provide their postal code/zip code'
            return elicit_slot(session_attributes, current_intent, slots, 'PostalCode', message)

        # relative_state = slots['State']
        #
        # if event['recentIntentSummaryView'][0]['slotToElicit'] == 'State':
        #     slots['State'] = str(event['inputTranscript']).lower()
        #     relative_state = str(event['inputTranscript']).lower()
        #
        # if relative_state is None:
        #     message = 'Please provide the State/Province where they live'
        #     return elicit_slot(session_attributes, current_intent, slots, 'State', message)
        #
        # relative_state_converted = states_dict[str(relative_state).lower()]
        #
        # relative_city = slots['City']
        #
        # if event['recentIntentSummaryView'][0]['slotToElicit'] == 'City':
        #     slots['City'] = str(event['inputTranscript']).lower()
        #     relative_city = str(event['inputTranscript']).lower()
        #
        # if relative_city is None:
        #     message = 'Please provide the City/Town where they live'
        #     return elicit_slot(session_attributes, current_intent, slots, 'City', message)

        complete_address = slots['AddressLine']

        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'AddressLine':
            slots['AddressLine'] = str(event['inputTranscript']).lower()
            complete_address = str(event['inputTranscript']).lower()

        if complete_address is None:
            message = 'Please provide their address'
            return elicit_slot(session_attributes, current_intent, slots, 'AddressLine', message)

        address_line, relative_city, relative_state = complete_address.split(',')
        address_line = str(address_line).strip()
        relative_city = str(relative_city).strip()
        relative_state = str(relative_state).strip()
        relative_state_converted = states_dict[str(relative_state).lower()]

        phone_number = slots['PhoneNumber']

        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'PhoneNumber':
            slots['PhoneNumber'] = str(event['inputTranscript']).lower()
            phone_number = str(event['inputTranscript']).lower()

        if phone_number is None:
            message = 'Please provide their phone number'
            return elicit_slot(session_attributes, current_intent, slots, 'PhoneNumber', message)

        email_address = slots['EmailID']

        if event['recentIntentSummaryView'][0]['slotToElicit'] == 'EmailID':
            slots['EmailID'] = str(event['inputTranscript']).lower()
            email_address = str(event['inputTranscript']).lower()

        if email_address is None:
            message = 'Please provide your new home email address'
            return elicit_slot(session_attributes, current_intent, slots, 'EmailID', message)

        workday_response, status_code = human_resources.change_emergency_contact(emp_id, country, relation_type,
                                                                                 relative_first_name,
                                                                                 relative_last_name,
                                                                                 address_line,
                                                                                 str(relative_city).capitalize(),
                                                                                 relative_state_converted, postal_code,
                                                                                 phone_number, email_address)

        if status_code == 200:
            message = 'Thanks for providing the information. Your emergency contact details have been updated on ' \
                      'Workday.'

        else:
            message = workday_response['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
            message += '\nPlease contact HR to complete this action'

        new_attributes = {
            'emp_id': emp_id,
            'update_details': None
        }
        session_attributes = update_session_attributes(session_attributes, new_attributes)

        return close(session_attributes, message)


def lambda_handler(event, context):
    current_intent = event['currentIntent']['name']
    session_attributes = get_session_attributes(event)
    slots = get_slots(event)

    print('####EVENT')
    print((str(event).replace('\'', '"')).replace('None', 'null'))

    print('####SLOTS')
    print(slots)

    print('####SESSION_ATTRIBUTES')
    print(session_attributes)

    if current_intent in ['Greeting', 'AlternateGreeting', 'OfficeAccess', 'TravelAdvisory', 'CovidExposure',
                          'QuarantineGuidelines', 'WorkFromHomeGuidlelines']:
        response = generate_attributes(event)
    elif current_intent == 'MissingPersonalInfo':
        response = update_missing_info(event)
    elif current_intent == 'PreferredName':
        response = change_preferred_name(event)
    elif current_intent == 'BusinessTitle':
        response = change_business_title(event)
    elif current_intent == 'FirstDaySetup':
        response = day_one_setup(event)
    elif current_intent == 'DisabilityDetailsUpdate':
        response = disability_details_update(event)
    elif current_intent == 'BotIntroduction':
        response = bot_intro(event)
    elif current_intent == 'AlternateIntent':
        response = suggest_utterance(event)
    elif current_intent == 'EmailUpdate':
        response = update_home_email(event)
    elif current_intent == 'CovidCheckIn':
        response = worker_checkin(event)
    elif current_intent == 'CancelCurrentIntent':
        response = reset_all_attributes(event)
    elif current_intent == 'EmergencyContactDetails':
        response = update_emergency_contact(event)
    else:
        message = f'Intent with name {current_intent} not supported yet'
        response = close(session_attributes, message)

    return response
