from workday_web_services import human_resources

missing_item_dict = {
    "Check_Home_Email": 'Home Email',
    "Check_Home_Phone": 'Home Phone Number'
}

missing_item_slots = {
    "Check_Home_Email": 'Email',
    "Check_Home_Phone": 'Phone'
}

missing_item_functions = {
    "Check_Home_Email": human_resources.change_home_contact_information_email,
    "Check_Home_Phone": human_resources.change_home_contact_information_phone
}

phone_country_code_dict = {
    'USA': 'USA_1'
}

error_handler = {
    'lgbt': ['What are LGBT community Policies',
             'What are the policies related to the LGBT community'],

    'pwd': ['How to declare the Disability details',
            'How to raise a transportation request for Person with Disability'],
    'disability': ['How to declare the Disability details',
                   'How to raise a transportation request for Person with Disability'],

    'policies': ['I would like to know about the company policies'],
    'policy': ['I would like to know about the company policies'],

    'insurance': ['How update my insurance policy',
                  'How to enroll for insurance'],
    'medical': ['How update my insurance policy',
                'How to enroll for insurance'],

    'dependant': ['How can I add my dependents for insurance'],

    'name': ['Change my preferred name'],

    'title': ['Change my business title',
              'Change my title'],

    'missing': ['Is my personal information missing'],

    'email': ['Change my email address',
              'Update my email']
}

work_style_dict = {
    'a': 'Working from home',
    'b': 'Working from office',
    'c': 'Working from client location',
    'd': 'On Personal Time Off'
}

locations_dict = {
    'a': 'Bengaluru',
    'b': 'Hyderabad',
    'c': 'Pune',
    'd': 'Chennai',
    'e': 'Gurugram',
    'f': 'Mumbai',
    'g': 'Kolkata',
    'h': 'Noida',
    'i': 'New Delhi'
}

states_dict = {
    'california': 'USA-CA'
}

relation_type_dict = {
    'spouse': '620.3',
    'child': '620.6'
}
