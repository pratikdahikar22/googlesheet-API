import uuid


def get_unique_id()->str:
    return str(uuid.uuid4())

def get_worksheet(worksheet_name:str)-> object:
    
    try:
        from app import spreadsheet          # change app with lambda_handla file name before deployment
        return spreadsheet.worksheet(worksheet_name.title())
    except Exception as e:
        print("get_worksheet error: ", e)
        raise Exception("Invalid worksheet Name..!")

#=================== spreadsheet CRUD function =======================

def create_worksheet(spreadsheet:object, worksheet_name:str, col_names:list[str])-> str:
    # Add new worksheet in spreadsheet
    worksheet_name = worksheet_name.title()
    col_names = ["uuid"] +  col_names
    try:
        worksheet = spreadsheet.add_worksheet(worksheet_name, 1000, 26)
        worksheet.append_row([col.title() for col in col_names])
        return "Worksheet created successfully..!"  
    except Exception as e:
        print("create_worksheet error :", e)
        raise Exception(f"sheet with the name {worksheet_name} already exists.")

def list_worksheets(spreadsheet:object)->list[str]:
    return [worksheet.title for worksheet in spreadsheet.worksheets()]

def delete_worksheet(spreadsheet:object, worksheet_name:str)-> str:
    # delete worksheet in spreadsheet
    worksheet = get_worksheet(worksheet_name)
    resp = spreadsheet.del_worksheet(worksheet)
    return "Worksheet deleted sucessfully..!"  

def rename_worksheet(worksheet_name:str, new_worksheet_name:str)->str:
    worksheet = get_worksheet(worksheet_name=worksheet_name)
    resp = worksheet.update_title(new_worksheet_name)
    return "Worksheet name updated..!"
    
#=================== Worksheet CRUD function =======================

def add_records(worksheet_name:str, records:list[list[str]])->str:
    worksheet = get_worksheet(worksheet_name)
    title_row_len = len(worksheet.get("1:1")[0]) - 1
    for rec in records:
        if len(rec) != title_row_len:
            raise Exception('Invalid data..!') 
                   
    records = [[get_unique_id()]+rec for rec in records]
    worksheet.append_rows(records)
    return "Record added successfully..!"
    

def list_records(worksheet_name:str)->list[dict]:
    worksheet = get_worksheet(worksheet_name)
    return worksheet.get_all_records()


def get_record(worksheet_name:str, rec_id:str)->dict:
    worksheet = get_worksheet(worksheet_name)
    rec = worksheet.find(rec_id)
    if rec:
        # first method --- time required 5 sec
        title_row = worksheet.get("1:1")[0]
        print(title_row)
        rec_row   = worksheet.get(f"{rec.row}:{rec.row}")[0]
        return dict(zip(title_row, rec_row))

        #second method --- time required 4 sec
        # return worksheet.get(f"{rec.row}:{rec.row}")[0]
    
    return "Invalid ID..!"


def update_record(worksheet_name:str, rec_id:str, rec_data:list[str])->str:
    worksheet = get_worksheet(worksheet_name)
    rec = worksheet.find(rec_id)
    if rec:
        worksheet.batch_update([{
            'range': f'{rec.row}:{rec.row}',
            'values': [[rec.value] + rec_data]
        }])
        return "Record updated successfully..!"
        
    return 'Invalid ID..!'
            

def delete_record(worksheet_name:str, rec_id:str)->str:
    worksheet = get_worksheet(worksheet_name)
   
    rec = worksheet.find(rec_id)
    if rec:
        worksheet.delete_rows(rec.row)
        return "Record deleted successfully..!"
    return "Invalid ID..!"
        
        
# -------------------------------------------check below

def find_records(worksheet_name:str, text:str):
    worksheet = get_worksheet(worksheet_name)

    if worksheet:
        return worksheet.findall(text)
    else:
        return "Invalid worksheet name..!"





