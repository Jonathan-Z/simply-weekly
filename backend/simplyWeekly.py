import json
from flask import Flask
from flask import request, jsonify
from flask_mongoengine import MongoEngine
import datetime
from flask_cors import CORS
import dtExtract

cors = CORS()

app = Flask(__name__)
app.config["DEBUG"] = True

cors.init_app(app=app, supports_credentials=True)

app.config['MONGODB_SETTINGS'] = {
	"db":"calendars",
	"host": "localhost",
	"port": 27017
}

db = MongoEngine()
db.init_app(app)

"""
Object model for Event
"""
class Event(db.EmbeddedDocument):
	title = db.StringField(max_length=256,required=True)
	startTime = db.DateTimeField(required=True)
	duration = db.IntField(min_value=0, max_value=10080) # duration in minutes
	notes = db.StringField(max_length=2048)
	def to_json(self):
		return {"title":self.title,
				"startTime": self.startTime.isoformat(), 
				"duration":self.duration,
				"notes":self.notes}


"""
Calendar object model
"""
class Calendar(db.Document):
	name = db.StringField(max_length=256, required=True)
	events = db.EmbeddedDocumentListField(Event,default = [])

	def to_json(self):

		return {"name":self.name,
				"events": [event.to_json() for event in self.events]}



"""
Base page, which we can just redirect to serve the react FE
"""
@app.route("/", methods=["GET"])
def home():
	return "simplyWeekly"

"""
Get all the currently saved calendar data for this user
"""
@app.route("/api/poll", methods=["GET"])
def poll():
	name = request.args.get("name")
	cal = Calendar.objects(name=name).first()

	if not cal:
		print("No Calendar of " + name + " found")
		print("creating new calendar")

		cal = Calendar(name=name,events=[])
		cal.save()
	else:
		print("Cal Found " + name)

	return jsonify(cal.to_json())


"""
Send an update to add/overrwrite an event to the calandar programmically
An event is uniquely identified
"""
@app.route("/api/update/add", methods=["POST"])
def add():

	req = request.get_json()
	
	name = req["name"]
	cal = Calendar.objects(name=name).first()

	title = req["data"]["title"]
	dt = datetime.datetime.strptime(req["data"]["startTime"], "%Y-%m-%dT%H:%M:%S")

	event = Event(title=title,
					startTime= dt, 
					duration=int(req["data"]["duration"]),
					notes=req["data"]["notes"])


	if cal:
		existing = cal["events"].filter(title=event["title"]).filter(startTime=event["startTime"])
		
		print(existing)

		if existing.count() == 0:
			newEvent = existing.create()
			newEvent["title"] = event["title"]
			newEvent["startTime"] = event["startTime"]
			newEvent["duration"] = event["duration"]
			newEvent["notes"] = event["notes"]
			existing.save()
		else:
			existing.update(title=event["title"],
				startTime=event["startTime"],
				duration=event["duration"],
				notes=event["notes"])
			existing.save()
		return jsonify(cal.to_json())
	else:
		print("No cal found")
		return jsonify({"Error":"No calendar found"})

	return jsonify(cal.to_json())

"""
Send an update to the calandar programmically to remove an entry
"""
@app.route("/api/update/rem", methods=["POST"])
def rem():
	req = request.get_json()
	name = req["name"]
	cal = Calendar.objects(name=name).first()

	title = req["data"]["title"]
	dt = datetime.datetime.strptime(req["data"]["startTime"], "%Y-%m-%dT%H:%M:%S")

	if cal:
		existing = cal["events"].filter(title=title).filter(startTime=dt)
		
		print(existing)

		if existing.count() > 0:
			existing.delete()
			existing.save()
		else:
			print("none found")
		return jsonify(cal.to_json())
	else: 
		print("No cal found")
		return jsonify({"Error":"No calendar found"})

"""
Send an update to the calandar via natural language
"""
@app.route("/api/parse", methods=["GET"])
def parse():
	name = request.args.get("name")
	content = request.args.get("text")


	print(name)

	print(content)

	cal = Calendar.objects(name=name).first()


	if cal is None:
		print("No Calendar of " + name + " found")
		print("creating new calendar")

		cal = Calendar(name=name,events=[])
		cal.save()



	# Now we have the calendar let's zone in on the event

	print(cal.to_json())

	info = dtExtract.extract_info(content)

	print(info)

	event = Event(title=info["title"],
				startTime=info["startTime"], 
				duration=int(info["duration"].total_seconds()/60),
				notes="")


	existing = cal["events"].filter(title=event["title"]).filter(startTime=event["startTime"])
	
	print(existing)

	if existing.count() == 0:
		newEvent = existing.create()
		newEvent["title"] = event["title"]
		newEvent["startTime"] = event["startTime"]
		newEvent["duration"] = event["duration"]
		newEvent["notes"] = event["notes"]
		existing.save()
	else:
		existing.update(title=event["title"],
			startTime=event["startTime"],
			duration=event["duration"],
			notes=event["notes"])
		existing.save()
	return jsonify(cal.to_json())	

