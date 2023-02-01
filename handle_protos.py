from file_manager import upsert_file
import os

def handle_proto_file(supabase, path, file, api_id):
  file_content = supabase.storage().from_("protos").download(api_id + '/' + file["name"])
  file_path = path + '/' + file["name"]

  upsert_file(file_path, file_content, mode='wb+')


def compile_all_proto_files(path):
  protoc_cmd = "python -m grpc_tools.protoc --proto_path=%s --python_out=%s --grpc_python_out=%s %s/*.proto" % (path, path, path, path)
  print("Compiling all proto files...")
  print(protoc_cmd)
  os.system(protoc_cmd)
  print("Done compiling all proto files.")


def fix_import(path):
  cmd = "cd tmp/checks/check_id && sed -i 's/^\(import.*pb2\)/from . \%s/g' *.py" % "1"
  os.system(cmd)


def handle_protos(supabase, path, api_id):
  proto_files = supabase.storage().from_("protos").list(api_id)

  for file in proto_files:
      handle_proto_file(supabase, path, file, api_id)

  compile_all_proto_files(path)

  fix_import(path)