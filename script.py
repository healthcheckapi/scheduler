import os
from dotenv import load_dotenv
from supabase import create_client, Client
import generate_check_client as generate_client
import importlib
from file_manager import make_module, create_directory_if_not_exist, upsert_file
from handle_protos import handle_protos

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

check_id = 'check_id'

PROTOS_PATH = "tmp/checks/%s" % check_id


if __name__ == "__main__":
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    create_directory_if_not_exist('tmp')
    create_directory_if_not_exist('tmp/checks')
    create_directory_if_not_exist(PROTOS_PATH)
    make_module(PROTOS_PATH)

    handle_protos(supabase, PROTOS_PATH, check_id)

    content = generate_client.generate_client("vitoria-example.fly.dev:9090", "recommendations", "Recommendations", "Recommend", "RecommendationRequest")

    upsert_file("%s/client.py" % PROTOS_PATH, content)

    result = importlib.import_module('tmp.checks.check_id.client').make_request()

    print(result)

    os.system("rm -rf %s" % PROTOS_PATH)

