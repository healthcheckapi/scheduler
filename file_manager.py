import os

def make_module(path):
  with open("%s/__init__.py" % path, "w+") as f:
    f.write("")


def create_directory_if_not_exist(path):
  if not os.path.exists(path):
    os.mkdir(path)


def upsert_file(path, content, mode = 'w+'):
  with open(path, mode) as file:
    file.write(content)