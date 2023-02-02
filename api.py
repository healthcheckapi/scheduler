from flask import Flask
from flask_restful import Resource, Api, reqparse
from crontab import CronTab
import os

app = Flask(__name__)
api = Api(app)
# cron = CronTab(tabfile='healthcheck-cron.tab')
cron = CronTab(user='myuser')

class SchedulerList(Resource):
  parser = reqparse.RequestParser()

  def post(self):
    self.parser.add_argument('check_id', type=str, required=True, help="This field cannot be left blank!")
    self.parser.add_argument('interval', type=int, required=True, help="This field cannot be left blank!")
    data = self.parser.parse_args()

    print(type(data['interval']))

    job = cron.new(command='/usr/bin/python3 /home/vitoria/Documents/healthcheckapi/healthcheck/check_script/script.py %s %s >> /tmp/out.txt' % (data['check_id'], os.getcwd() + '/check_script'), comment=data['check_id'])
    job.minute.every(data['interval'])

    cron.write()
    
    return "Cron job created for check_id [%s] to run every %s minutes" % (data['check_id'], data['interval']), 201

  def delete(self):
    for job in cron:
      cron.remove(job)
      cron.write()

    return None, 204

  def get(self):
    return [{'key': job.comment, 'enable': job.is_enabled(), 'valid': job.is_valid()} for job in cron], 200

class Scheduler(Resource):
  def delete(self, check_id):
    for job in cron:
      if job.comment == check_id:
        cron.remove(job)
        cron.write()
        break

    return None, 204


api.add_resource(SchedulerList, '/scheduler')
api.add_resource(Scheduler, '/scheduler/<check_id>')

if __name__ == "__main__":
    app.run(debug=True)
