def generate_client(url, proto_name, serviceName, methodName, requestName):
  content = []

  # Import statements
  content.append('import time')
  content.append('import grpc')
  content.append('from .%s_pb2 import %s' % (proto_name, requestName))
  content.append('from .%s_pb2_grpc import %sStub' % (proto_name, serviceName))
  content.append('\n')

  # Client definition
  content.append('client = %sStub(grpc.insecure_channel("%s"))' % (serviceName, url))

  # Make request
  content.append('request = %s()' % requestName)
  content.append('\n')

  # Get response
  content.append('def make_request():')

  content.append('\tstart = time.time()')
  content.append('\tresponse = client.%s(request)' % methodName)
  content.append('\tend = time.time()')

  content.append('\treturn {"response": response, "time": end - start}')

  return '\n'.join(content)
