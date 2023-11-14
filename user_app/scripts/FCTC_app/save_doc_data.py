import os
import json
import ast
import pymongo

def upload_data_to_db(
        meta_data   = {},
        client      = None,
):
    db      = client.myDatabase
    reports = db['reports']

    print("-----------------------------------------------")
    print(meta_data)

    try:
        cursor = reports.find({"actuator_serial_number": meta_data["actuator_serial_number"]})
        cursor = list(cursor)

        if len(cursor) == 0:
            result = reports.insert_one(meta_data)
        elif len(cursor) > 0:
            result = reports.replace_one(
                {"actuator_serial_number": meta_data["actuator_serial_number"]},
                meta_data
            )
        print(result)
    # return a friendly error if the operation fails
    except pymongo.errors.OperationFailure:
        print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        return False
    else:
        print("Inserted 1 document.")
        print("\n") 
        return True
    return True
    
def download_data_from_db(
        actuator_no = "",
        client      = None,
):
    db      = client.myDatabase
    reports = db['reports']

    cursor  = reports.find({"actuator_serial_number": actuator_no})
    cursor  = list(cursor)

    return cursor