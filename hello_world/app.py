import json
import gspread
from datetime import datetime
from utils import create_worksheet, delete_worksheet, list_worksheets, rename_worksheet
from utils import add_records, list_records, delete_record, find_records, get_record, update_record

spreadsheet_name = "Expenses2025"
client = gspread.service_account(filename='credentials.json')
spreadsheet = client.open(spreadsheet_name)

months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}


def lambda_handler(event, context):
    # print(event)
    
    method = event.get("httpMethod","")
    path   = event.get("path","")
    body   = json.loads(event['body']) if event['body'] else {}
    query_params = event.get('queryStringParameters') if event.get('queryStringParameters') else {}

    print("body:-",body)
    print("method:-", method)
    print("path:-",path)
    print("query_params:-",query_params)
    
    resp = []
    message = ''
    
    try:
        
        # Method : GET
        if path == "/list-worksheets" and method=="GET": 
            message = "list of worksheets..!"
            resp = list_worksheets(spreadsheet)
        
        #in working..
        elif path == "/create-worksheet" and method == "POST":
            worksheet_name = body.get("worksheet_name", "")
            col_names = body.get("col_names", [])

            if col_names and worksheet_name:
                message = create_worksheet(spreadsheet, worksheet_name, col_names)
            else:
                raise Exception("Check worksheet name and added record..!")

        # Method : POST
        elif path == "/rename-worksheet" and method == "POST":
            worksheet_name = body.get("worksheet_name", "") 
            new_worksheet_name = body.get("new_worksheet_name", "")
            if worksheet_name and new_worksheet_name:
                message = rename_worksheet(worksheet_name, new_worksheet_name)
            else:
                raise Exception('worksheet name and new worksheet name required..!')
            
        # Method : POST
        elif path == "/add-records" and method == "POST":
            records = body.get("records", [])
            worksheet_name = body.get('worksheet_name', '')

            if records and worksheet_name:
                message = add_records(worksheet_name,records)
            else:
                raise Exception("Check worksheet name and added record..!")

        # Method : GET
        elif path == "/list-records" and method == "GET":
            worksheet_name = query_params.get('worksheet_name', '')
            month = query_params.get('month', '')
            sort_by    = query_params.get('sort_by', '').title()
            sort_order = query_params.get('sort_order', False)
            
            if worksheet_name:
                resp    = list_records(worksheet_name)
                message = "list of worksheet records..!"
                
                # filter monthly records
                if month in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10","11", "12"]:
                    resp = list(filter(lambda rec: f"-{month}-" in rec['Date'], resp))
                
                # sort by and sorting order
                if sort_by and resp and (sort_by in resp[0].keys()):
                    if sort_by.title() == 'Date':
                        resp.sort(key=lambda x: datetime.strptime(x[sort_by], "%d-%m-%Y"), reverse=bool(sort_order))
                    resp.sort(key=lambda x: x[sort_by], reverse=bool(sort_order))
            else:
                raise Exception('Enter vaild worksheet name..!')
        
        # Method : GET
        elif path == "/get-record" and method == "GET":
            worksheet_name = query_params.get('worksheet_name', '')
            rec_id = query_params.get('rec_id', '')
            
            if worksheet_name and rec_id:
                resp = get_record(worksheet_name,rec_id)
                message = "Record get successfully..!"
            else:
                raise Exception("Enter valid worksheet name and rec_id..!")
        
        # Method : PATCH
        elif path == "/update-record" and method == "PATCH":
            rec_id         = body.get("rec_id", "")
            rec_data       = body.get("rec_data", {})
            
            date = rec_data.get('Date','')
            if date == "": raise Exception('Date required..!')
                
            month = datetime.strptime(date, "%d-%m-%Y").month
            worksheet_name = months[month]
                
            rec_data = list(rec_data.values())   
            if worksheet_name and rec_id and rec_data:
                message = update_record(worksheet_name, rec_id, rec_data)
            else:
                raise Exception("Enter valid worksheet name, rec_id and rec_data")

        # Method : DELETE
        elif path == "/delete-record" and method == "DELETE":
            # worksheet_name = body.get("worksheet_name", "")
            date = query_params.get("date", "")
            rec_id = query_params.get("rec_id", "")
            
            if date == "": raise Exception('Date required..!')
            
            month = datetime.strptime(date, "%d-%m-%Y").month
            worksheet_name = months[month]
            
            if worksheet_name and rec_id:
                message = delete_record(worksheet_name, rec_id)
            else:
                raise Exception("Enter valid date and rec_id..!")

        elif path == "/to-do" and (method in ["POST", "GET", "DELETE"]):
            worksheet_name = "To-Do"
            records = body.get("records", [])
            rec_id  = query_params.get("rec_id","")
            
            if method == "POST":
                add_records(worksheet_name, records)
                message = "todo added..!"

            elif method == "GET":
                resp = list_records(worksheet_name)
                message = "list of to-do..!"

            elif method == "DELETE":
                delete_record(worksheet_name, rec_id)            
                message = "todo deleted successfully..!"
        else:
            raise Exception("Invalid path......!")

        # print(message)
        # print(resp)
        
        return {
                "statusCode": 200,
                "body": json.dumps({
                "message": message,
                "data": resp
            }),
        }


    except Exception as e:
        print(e)
        return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(e),            
                }),
        }
