from datetime import date
import requests
import xmltodict

from workday_web_services import workday_pwd, workday_id, headers, workday_ws_url, version

Human_Resources_URL = f'{workday_ws_url}/Staffing/{version}?WSDL'


def edit_worker_additional_data(emp_id, location_data):
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
                        Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText
                        ">{workday_pwd}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
        </env:Header>
        <env:Body>
            <wd:Edit_Worker_Additional_Data_Request
                xmlns:wd="urn:com.workday/bsvc"
                xmlns:cus="urn:com.workday/tenants/super/data/custom"
                wd:version="{version}">
                <wd:Business_Process_Parameters>
                    <wd:Auto_Complete>true</wd:Auto_Complete>
                    <wd:Run_Now>true</wd:Run_Now>
                </wd:Business_Process_Parameters>
                <wd:Worker_Custom_Object_Data>
                    <wd:Effective_Date>{str(date.today())}</wd:Effective_Date>
                    <wd:Worker_Reference>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Worker_Reference>
                    <wd:Business_Object_Additional_Data>
                        <cus:dailylocationtracker>
                            <cus:locationdata>{location_data}</cus:locationdata>
                        </cus:dailylocationtracker>
                    </wd:Business_Object_Additional_Data>
                </wd:Worker_Custom_Object_Data>
            </wd:Edit_Worker_Additional_Data_Request>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(Human_Resources_URL, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    return response_dict, response.status_code
