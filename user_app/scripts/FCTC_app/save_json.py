import json
import os
import ast

def save_json(
        meta_data = {}
):

    json_object     = json.dumps(meta_data, indent=4)
    out_path        = "../../report_data/json/{}".format(meta_data['actuator_serial_number'])

    with open( out_path, "w") as outfile:
        json.dump(json_object, outfile)
    
    return None


def file_exists(
        actuator_number = "",
) -> bool:
    
    json_files_dir  = "../../report_data/json/"
    
    files_list      = os.listdir(json_files_dir)

    if actuator_number in files_list:
        return True
    else:
        return False
    

def read_json(
        actuator_number = ""
) -> dict:
    meta_data = {}

    json_files_path  = "../../report_data/json/{}".format(actuator_number)
    #print(json_files_path)
    file             = open(json_files_path)
    meta_data        = json.load(file)
    meta_data        = ast.literal_eval(meta_data)
    return meta_data