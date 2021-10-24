from datetime import datetime, timedelta
from pydantic import BaseModel

class Calendar(BaseModel):
	id: Optional[pydantic]
	name: str
	events: List[Event]

	def to_json(self):
		return jsonable_encoder(self)

	def to_b

class Event(BaseModel):
	title: str
	start_time: datetime 
	duration: timedelta
	notes: str