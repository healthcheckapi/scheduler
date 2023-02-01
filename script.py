import os
from dotenv import load_dotenv
from supabase import create_client, Client
import generate_check_client as generate_client
import importlib
from file_manager import make_module, create_directory_if_not_exist, upsert_file
from handle_protos import handle_protos
import json

import time
from timeloop import Timeloop
from datetime import timedelta
from google.protobuf.json_format import MessageToJson

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

check_id = 'd9bd2ce6-9aa2-4145-bcbb-4ba8aca489b9'

tl = Timeloop()

PROTOS_PATH = "tmp/checks/%s" % check_id

def fetch_entity(supabase, table, entity_id, column_eq = "id"):
    response = supabase.table(table).select("*").eq(column_eq, entity_id).execute()

    if (response.data is None or len(response.data) == 0):
        print("Something went wrong while fetching %s[%s = %s]." % (table, column_eq, entity_id))
        exit(1)

    return response.data[0]

@tl.job(interval=timedelta(minutes=1))
def execute_check():
    print('---------------------------------------')
    print("Executing check %s..." % check_id)

    check = fetch_entity(supabase, "checks", check_id)
    api = fetch_entity(supabase, "apis", check["api_id"])
    files = fetch_entity(supabase, "files", check["api_id"], "api_id")

    check_path = "tmp/checks/%s" % check_id

    print("Check: ", check)
    print("API: ", api)

    create_directory_if_not_exist('tmp')
    create_directory_if_not_exist('tmp/checks')
    create_directory_if_not_exist(check_path)
    make_module(check_path)

    handle_protos(supabase, check_path, check["api_id"])

    content = generate_client.generate_client(api['url'], "recommendations", check['service'], check['method'], "RecommendationRequest")

    upsert_file("%s/client.py" % check_path, content)

    result = importlib.import_module('%s.client' % check_path.replace('/', '.')).make_request()

    print("Result: ", result)

    response = MessageToJson(result['response']) if result['response'] is not None else None
    latency = result['latency']
    error = json.dumps(result['error'])
    status = result['status']

    supabase.table("check_results").insert({ 'check_id': check_id, 'response': response, 'latency': latency, 'status': status, 'error': error }).execute()

    os.system("rm -rf %s" % check_path)

    print()

    print("Done executing check %s." % check_id)
    print('---------------------------------------')


if __name__ == "__main__":
    tl.start(block=True)
    # execute_check()

