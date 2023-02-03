from file_manager import upsert_file
import os
import subprocess

def handle_proto_file(supabase, path, file, api_id):
  file_content = supabase.storage().from_("protos").download(api_id + '/' + file["name"])
  file_path = path + '/' + file["name"]

  upsert_file(file_path, file_content, mode='wb+')


def compile_all_proto_files(path):
  protoc_cmd = "/home/myuser/venv/bin/python -m grpc_tools.protoc --proto_path=%s --python_out=%s --grpc_python_out=%s %s/*.proto" % (path, path, path, path)
  print("Compiling all proto files...")
  print(protoc_cmd)
  erorr = subprocess.run(protoc_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stderr.decode('utf-8')

  if erorr:
    print("Error while compiling protos: ", erorr)
  else:
    print("Done compiling all proto files.")


def fix_import(path):
  cmd = "cd %s && sed -i 's/^\(import.*pb2\)/from . \%s/g' *.py" % (path, "1")
  os.system(cmd)


def handle_protos(supabase, path, api_id):
  proto_files = supabase.storage().from_("protos").list(api_id)

  for file in proto_files:
      handle_proto_file(supabase, path, file, api_id)

  compile_all_proto_files(path)

  fix_import(path)