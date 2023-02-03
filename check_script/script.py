import os
import sys
import json
import importlib
from dotenv import load_dotenv
from handle_protos import handle_protos
from supabase import create_client, Client
import generate_check_client as generate_client
from google.protobuf.json_format import MessageToJson
from file_manager import make_module, create_directory_if_not_exist, upsert_file

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_entity(supabase, table, entity_id, column_eq = "id"):
    response = supabase.table(table).select("*").eq(column_eq, entity_id).execute()

    if (response.data is None or len(response.data) == 0):
        print("Something went wrong while fetching %s[%s = %s]." % (table, column_eq, entity_id))
        exit(1)

    return response.data[0]


def execute_check():
    print('---------------------------------------')
    print("Executing check %s..." % check_id)

    check = fetch_entity(supabase, "checks", check_id)
    api = fetch_entity(supabase, "apis", check["api_id"])
    files = fetch_entity(supabase, "files", check["api_id"], "api_id")

    check_path = "tmp/checks/%s" % check_id

    print("Check: ", check)
    print("API: ", api)

    print("Creating directory %s" % check_path)

    create_directory_if_not_exist('tmp')
    create_directory_if_not_exist('tmp/checks')
    create_directory_if_not_exist(check_path)
    make_module(check_path)

    print("Created directory %s" % check_path)
    print("Handling protos...")

    handle_protos(supabase, check_path, check["api_id"])

    print("Handled protos.")
    print("Generating client...")

    content = generate_client.generate_client(api['url'], "recommendations", check['service'], check['method'], "RecommendationRequest")

    print("Generated client.")
    print("Upserting client.py...")

    upsert_file("%s/client.py" % check_path, content)

    print("Upserted client.py.")

    print("current directory: ", os.getcwd())

    current_path = (os.getcwd() if os.getcwd()[0] != '/' else os.getcwd()[1:]).replace('/', '.')

    client_module_path = current_path + '.' + check_path.replace('/', '.')
    print("client module path: ", client_module_path)

    print("Importing client...")
    client = importlib.import_module('%s.client' % check_path.replace('/', '.'))
    # client = importlib.import_module('%s.client' % client_module_path)

    print("Making request...")

    result = client.make_request()

    print("Made request.")

    print("Result: ", result)

    response = MessageToJson(result['response']) if result['response'] is not None else None
    latency = result['latency']
    error = json.dumps(result['error'])
    status = result['status']

    print("Inserting check result...")
    supabase.table("check_results").insert({ 'check_id': check_id, 'response': response, 'latency': latency, 'status': status, 'error': error }).execute()
    print("Inserted check result.")

    print("Removing directory %s" % check_path)
    os.system("rm -rf %s" % check_path)

    print("Removed directory %s" % check_path)

    print("Done executing check %s." % check_id)
    print('---------------------------------------')


if __name__ == "__main__":
    print("sys.argv: ", sys.argv)

    if len(sys.argv) < 2:
        print("Usage: python script.py <check_id>")
        exit(1)

    check_id = sys.argv[1]
    print("check_id: ", check_id)

    if len(sys.argv) > 2:
        working_dir = sys.argv = sys.argv[2]
        print("Changing working directory from %s to %s" % (os.getcwd(), working_dir))
        os.chdir(working_dir)

    try:
        execute_check()
    except Exception as e:
        print("Something went wrong while executing check %s." % check_id)
        print(e)
