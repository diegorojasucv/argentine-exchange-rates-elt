import fileinput
import json
import os
import shutil
import sys

config_filepath = "include/inputs/"
TEMPLATE_FILE = "include/templates/process_file.py"

for filename in os.listdir(config_filepath):
    if filename.endswith(".json"):
        config = json.load(open(f"{config_filepath}{filename}"))
        new_dag_file = f"dags/etl/etl_{config['dag_id']}.py"
        shutil.copyfile(TEMPLATE_FILE, new_dag_file)
        original_stdout = sys.stdout

        for line in fileinput.input(new_dag_file, inplace=True):
            line = line.replace("DAG_ID_HOLDER", config["dag_id"])
            line = line.replace("DESCRIPTION_HOLDER", config["description"])
            line = line.replace("TAG_HOLDER", config["tags"])
            line = line.replace("SOURCE_API_HOLDER", config["source_api"])
            line = line.replace("FUNCTION_HOLDER", config["function"])
            line = line.replace("PROCESS_TYPE_HOLDER", config["process_type"])
            line = line.replace("TABLE_NAME_HOLDER", config["table_name"])
            print(line, end="")
