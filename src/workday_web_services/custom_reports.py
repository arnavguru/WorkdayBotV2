import requests
import xmltodict

from workday_web_services import headers, workday_id, workday_pwd, workday_custom_report_url


def get_primary_position(emp_id):
    report_url = f'{workday_custom_report_url}/ISU_AWS_AGURU/CR_AWS_AGURU_DEFAULT_POSITION'

    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:wd="urn:com.workday/bsvc"
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
            <wd:Execute_Report>
                <wd:Report_Parameters>
                    <wd:Employee>
                        <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                    </wd:Employee>
                </wd:Report_Parameters>
            </wd:Execute_Report>
        </env:Body>
    </env:Envelope>"""

    response = requests.post(report_url, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)
    position_id = response_dict['env:Envelope']['env:Body']['wd:Report_Data']['wd:Report_Entry'][
        'wd:Worker_Profile_Default_Position']['wd:ID']['#text']

    return position_id


def get_emp_id_from_email(emp_email_id):
    report_url = f'{workday_custom_report_url}/ISU_AWS_AGURU/CR_AWS_WORK_EMAIL?format=simplexml'

    body = f"""<?xml version="1.0" encoding="utf-8"?>
        <env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
                        xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:wd="urn:com.workday/bsvc"
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
                <wd:Execute_Report>
                    <wd:Report_Parameters>
                        <wd:primaryWorkEmail>{emp_email_id}</wd:primaryWorkEmail>
                    </wd:Report_Parameters>		
                </wd:Execute_Report>
            </env:Body>
        </env:Envelope>"""

    response = requests.post(report_url, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    if response.content.__contains__(str.encode(emp_email_id)) and response.status_code == 200:
        emp_id = response_dict['env:Envelope']['env:Body']['wd:Report_Data']['wd:Report_Entry']['wd:Employee_ID']
        return emp_id
    else:
        return None


def get_missing_data(emp_id):
    report_url = f'{workday_custom_report_url}/ISU_AWS_AGURU/CR_AWS_MISSING_DATA_REPORT?format=simplexml'

    body = f"""<?xml version="1.0" encoding="utf-8"?>
            <env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:wd="urn:com.workday/bsvc"
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
                    <wd:Execute_Report>
                        <wd:Report_Parameters>
                            <wd:Report_Parameters>
                                <wd:Employee>
                                    <wd:ID wd:type="Employee_ID">{emp_id}</wd:ID>
                                </wd:Employee>
                            </wd:Report_Parameters>
                        </wd:Report_Parameters>		
                    </wd:Execute_Report>
                </env:Body>
            </env:Envelope>"""

    response = requests.post(report_url, data=body, headers=headers)
    response_dict = xmltodict.parse(response.content)

    if response.status_code == 200:
        return response_dict['env:Envelope']['env:Body']['wd:Report_Data']['wd:Report_Entry']
    else:
        return None
