from datetime import date

import requests
import xmltodict

from workday_web_services import workday_pwd, workday_id, headers, workday_ws_url, version

Human_Resources_URL = f'{workday_ws_url}/Human_Resources/{version}?WSDL'


def get_workers(emp_id):
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <env:Envelope
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <env:Header>
            <wsse:Security env:mustUnderstand="1">
                <wsse:UsernameToken>
                    <wsse:Username>{workday_id}</wsse:Username>
                    <wsse:Password
                        Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"
                        >{workday_pwd}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </env:Header>
        <env:Body>
            <wd:Get_Workers_Request xmlns:wd="urn:com.workday/bsvc" wd:version="{version}">
                <wd:Request_References>
                    <wd:Worker_Reference>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Worker_Reference>
                </wd:Request_References>
                <wd:Response_Filter>
                    <wd:Page>1</wd:Page>
                    <wd:Count>1</wd:Count>
                </wd:Response_Filter>
                <wd:Response_Group>
                    <wd:Include_Personal_Information>true</wd:Include_Personal_Information>
                    <wd:Include_Related_Persons>true</wd:Include_Related_Persons>
                </wd:Response_Group>
            </wd:Get_Workers_Request>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(Human_Resources_URL, data=body, headers=headers)

    response_dict = xmltodict.parse(response.content)

    return response_dict, response.status_code


def change_preferred_name(emp_id, country, first_name, middle_name, last_name):
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <env:Envelope
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <env:Header>
            <wsse:Security env:mustUnderstand="1">
                <wsse:UsernameToken>
                    <wsse:Username>{workday_id}</wsse:Username>
                    <wsse:Password
                        Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"
                        >{workday_pwd}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </env:Header>
        <env:Body>
            <wd:Change_Preferred_Name_Request
                xmlns:wd="urn:com.workday/bsvc"
                wd:version="{version}">
                <wd:Business_Process_Parameters>
                    <wd:Auto_Complete>true</wd:Auto_Complete>
                    <wd:Run_Now>true</wd:Run_Now>
                </wd:Business_Process_Parameters>
                <wd:Change_Preferred_Name_Data>
                    <wd:Person_Reference>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Person_Reference>
                    <wd:Name_Data>
                        <wd:Country_Reference>
                            <wd:ID wd:type="ISO_3166-1_Alpha-3_Code">{country}</wd:ID>
                        </wd:Country_Reference>
                        <wd:First_Name>{first_name}</wd:First_Name>
                        <wd:Middle_Name>{middle_name}</wd:Middle_Name>
                        <wd:Last_Name>{last_name}</wd:Last_Name>
                    </wd:Name_Data>
                </wd:Change_Preferred_Name_Data>
            </wd:Change_Preferred_Name_Request>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(Human_Resources_URL, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    return response_dict, response.status_code


def change_business_title(emp_id, position, business_title):
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <env:Header>
            <wsse:Security env:mustUnderstand="1">
                <wsse:UsernameToken>
                    <wsse:Username>{workday_id}</wsse:Username>
                    <wsse:Password
                        Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"
                        >{workday_pwd}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </env:Header>
        <env:Body>
            <wd:Change_Business_Title_Request xmlns:wd="urn:com.workday/bsvc" wd:version="{version}">
                <wd:Business_Process_Parameters>
                    <wd:Auto_Complete>true</wd:Auto_Complete>
                    <wd:Run_Now>true</wd:Run_Now>
                </wd:Business_Process_Parameters>
                <wd:Change_Business_Title_Business_Process_Data>
                    <wd:Worker_Reference>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Worker_Reference>
                    <wd:Job_Reference>
                        <wd:ID wd:type="WID">{position}</wd:ID>
                    </wd:Job_Reference>
                    <wd:Change_Business_Title_Data>
                        <wd:Event_Effective_Date>{str(date.today())}</wd:Event_Effective_Date>
                        <wd:Proposed_Business_Title>{business_title}</wd:Proposed_Business_Title>
                    </wd:Change_Business_Title_Data>
                </wd:Change_Business_Title_Business_Process_Data>
            </wd:Change_Business_Title_Request>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(Human_Resources_URL, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    return response_dict, response.status_code


def change_home_contact_information_email(emp_id, usage, email):
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <env:Header>
            <wsse:Security env:mustUnderstand="1">
                <wsse:UsernameToken>
                    <wsse:Username>{workday_id}</wsse:Username>
                    <wsse:Password
                        Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"
                        >{workday_pwd}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </env:Header>
        <env:Body>
            <wd:Change_Home_Contact_Information_Request
                xmlns:wd="urn:com.workday/bsvc" wd:version="{version}">
                <wd:Business_Process_Parameters>
                    <wd:Auto_Complete>true</wd:Auto_Complete>
                    <wd:Run_Now>true</wd:Run_Now>
                </wd:Business_Process_Parameters>
                <wd:Change_Home_Contact_Information_Data>
                    <wd:Person_Reference>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Person_Reference>
                    <wd:Event_Effective_Date>{str(date.today())}</wd:Event_Effective_Date>
                    <wd:Person_Contact_Information_Data>
                        <wd:Person_Email_Information_Data
                            wd:Replace_All="true">
                            <wd:Email_Information_Data wd:Delete="false">
                                <wd:Email_Data>
                                    <wd:Email_Address>{email}</wd:Email_Address>
                                </wd:Email_Data>
                                <wd:Usage_Data wd:Public="true">
                                    <wd:Type_Data wd:Primary="true">
                                        <wd:Type_Reference>
                                            <wd:ID wd:type="Communication_Usage_Type_ID">{usage}</wd:ID>
                                        </wd:Type_Reference>
                                    </wd:Type_Data>
                                </wd:Usage_Data>
                            </wd:Email_Information_Data>
                        </wd:Person_Email_Information_Data>
                    </wd:Person_Contact_Information_Data>
                </wd:Change_Home_Contact_Information_Data>
            </wd:Change_Home_Contact_Information_Request>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(Human_Resources_URL, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    return response_dict, response.status_code


def change_home_contact_information_phone(emp_id, usage, phone):
    emp_country_code = str(phone).split(':', 2)[0]
    phone = str(phone).split(':', 2)[1]

    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <env:Envelope
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <env:Header>
            <wsse:Security env:mustUnderstand="1">
                <wsse:UsernameToken>
                    <wsse:Username>{workday_id}</wsse:Username>
                    <wsse:Password
                        Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"
                        >{workday_pwd}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </env:Header>
        <env:Body>
            <wd:Change_Home_Contact_Information_Request
                xmlns:wd="urn:com.workday/bsvc"
                wd:version="{version}">
                <wd:Business_Process_Parameters>
                    <wd:Auto_Complete>true</wd:Auto_Complete>
                    <wd:Run_Now>true</wd:Run_Now>
                </wd:Business_Process_Parameters>
                <wd:Change_Home_Contact_Information_Data>
                    <wd:Person_Reference>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Person_Reference>
                    <wd:Event_Effective_Date>{str(date.today())}</wd:Event_Effective_Date>
                    <wd:Person_Contact_Information_Data>
                        <wd:Person_Phone_Information_Data wd:Replace_All="true">
                            <wd:Phone_Information_Data wd:Delete="false">
                                <wd:Phone_Data>
                                    <wd:Device_Type_Reference>
                                        <wd:ID wd:type="Phone_Device_Type_ID">Mobile</wd:ID>
                                    </wd:Device_Type_Reference>
                                    <wd:Country_Code_Reference>
                                        <wd:ID wd:type="Country_Phone_Code_ID">{emp_country_code}</wd:ID>
                                    </wd:Country_Code_Reference>
                                    <wd:Complete_Phone_Number>{phone}</wd:Complete_Phone_Number>
                                </wd:Phone_Data>
                                <wd:Usage_Data wd:Public="true">
                                    <wd:Type_Data wd:Primary="true">
                                        <wd:Type_Reference>
                                            <wd:ID wd:type="Communication_Usage_Type_ID">{usage}</wd:ID>
                                        </wd:Type_Reference>
                                    </wd:Type_Data>
                                </wd:Usage_Data>
                            </wd:Phone_Information_Data>
                        </wd:Person_Phone_Information_Data>
                    </wd:Person_Contact_Information_Data>
                </wd:Change_Home_Contact_Information_Data>
            </wd:Change_Home_Contact_Information_Request>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(Human_Resources_URL, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    return response_dict, response.status_code


def change_emergency_contact(emp_id, country, relation_type, first_name, last_name, address_line_1, city, state,
                             postal_code, phone_number, email):
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
    <env:Envelope xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" 
     xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
        <env:Header>
            <wsse:Security env:mustUnderstand="1">
                <wsse:UsernameToken>
                    <wsse:Username>{workday_id}</wsse:Username>
                    <wsse:Password 
                    Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"
                    >{workday_pwd}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </env:Header>
        <env:Body>
            <wd:Change_Emergency_Contacts_Request xmlns:wd="urn:com.workday/bsvc" wd:version="{version}">
                <wd:Business_Process_Parameters>
                    <wd:Auto_Complete>true</wd:Auto_Complete>
                    <wd:Run_Now>true</wd:Run_Now>
                </wd:Business_Process_Parameters>
                <wd:Change_Emergency_Contacts_Data>
                    <wd:Person_Reference>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Person_Reference>
                    <wd:Replace_All>true</wd:Replace_All>
                    <wd:Emergency_Contacts_Reference_Data>
                        <wd:Delete>false</wd:Delete>
                        <wd:Emergency_Contact_Data>
                        <wd:Primary>true</wd:Primary>
                        <wd:Priority>1</wd:Priority>
                        <wd:Related_Person_Relationship_Reference>
                            <wd:ID wd:type="Related_Person_Relationship_ID">{relation_type}</wd:ID>
                        </wd:Related_Person_Relationship_Reference>
                            <wd:Emergency_Contact_Personal_Information_Data>
                                <wd:Person_Name_Data>
                                    <wd:Legal_Name_Data>
                                        <wd:Name_Detail_Data>
                                            <wd:Country_Reference>
                                                <wd:ID wd:type="ISO_3166-1_Alpha-3_Code">{country}</wd:ID>
                                            </wd:Country_Reference>
                                            <wd:First_Name>{first_name}</wd:First_Name>
                                            <wd:Last_Name>{last_name}</wd:Last_Name>
                                        </wd:Name_Detail_Data>
                                    </wd:Legal_Name_Data>
                                    <wd:Preferred_Name_Data>
                                        <wd:Name_Detail_Data>
                                            <wd:Country_Reference>
                                                <wd:ID wd:type="ISO_3166-1_Alpha-3_Code">{country}</wd:ID>
                                            </wd:Country_Reference> 
                                            <wd:First_Name>{first_name}</wd:First_Name>
                                            <wd:Last_Name>{last_name}</wd:Last_Name> 
                                        </wd:Name_Detail_Data>
                                    </wd:Preferred_Name_Data> 
                                </wd:Person_Name_Data>
                                <wd:Contact_Information_Data>
                                    <wd:Address_Data wd:Delete="false" wd:Do_Not_Replace_All="true">
                                        <wd:Country_Reference>
                                            <wd:ID wd:type="ISO_3166-1_Alpha-3_Code">{country}</wd:ID>
                                        </wd:Country_Reference>
                                        <wd:Last_Modified>{str(date.today())}</wd:Last_Modified>
                                        <wd:Address_Line_Data wd:Type="ADDRESS_LINE_1"
                                        >{address_line_1}</wd:Address_Line_Data>
                                        <wd:Municipality>{city}</wd:Municipality>
                                        <wd:Country_Region_Reference>
                                            <wd:ID wd:type="Country_Region_ID">{state}</wd:ID>
                                        </wd:Country_Region_Reference>                                        
                                        <wd:Postal_Code>{postal_code}</wd:Postal_Code>
                                        <wd:Usage_Data wd:Public="false">
                                            <wd:Type_Data wd:Primary="true">
                                                <wd:Type_Reference>
                                                    <wd:ID wd:type="Communication_Usage_Type_ID">HOME</wd:ID>
                                                </wd:Type_Reference>
                                            </wd:Type_Data>
                                        </wd:Usage_Data>
                                    </wd:Address_Data>
                                    <wd:Phone_Data wd:Delete="false" wd:Do_Not_Replace_All="true">
                                        <wd:Country_ISO_Code>{country}</wd:Country_ISO_Code>
                                        <wd:Phone_Number>{phone_number}</wd:Phone_Number>
                                        <wd:Phone_Device_Type_Reference>
                                            <wd:ID wd:type="Phone_Device_Type_ID">Mobile</wd:ID>
                                        </wd:Phone_Device_Type_Reference>
                                        <wd:Usage_Data wd:Public="true">
                                            <wd:Type_Data wd:Primary="true">
                                                <wd:Type_Reference>
                                                    <wd:ID wd:type="Communication_Usage_Type_ID">HOME</wd:ID>
                                                </wd:Type_Reference>
                                            </wd:Type_Data>
                                        </wd:Usage_Data>
                                    </wd:Phone_Data>
                                    <wd:Email_Address_Data wd:Delete="false" wd:Do_Not_Replace_All="true">
                                        <wd:Email_Address>{email}</wd:Email_Address>
                                        <wd:Usage_Data wd:Public="true">
                                            <wd:Type_Data wd:Primary="true">
                                                <wd:Type_Reference>
                                                    <wd:ID wd:type="Communication_Usage_Type_ID">HOME</wd:ID>
                                                </wd:Type_Reference>
                                            </wd:Type_Data> 
                                        </wd:Usage_Data>
                                    </wd:Email_Address_Data>
                                </wd:Contact_Information_Data>
                            </wd:Emergency_Contact_Personal_Information_Data>
                        </wd:Emergency_Contact_Data>
                    </wd:Emergency_Contacts_Reference_Data>
                </wd:Change_Emergency_Contacts_Data>
            </wd:Change_Emergency_Contacts_Request>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(Human_Resources_URL, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    return response_dict, response.status_code
