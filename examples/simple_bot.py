# /Zakovskiy/amino.py/
# simple amino bot

from amino import Client

Amino = Client(email="email", password="password");

while 1:
	result = Amino.listen()
	
	mtype = result["message_type"];
	community_id = result["community_id"];
	thread_id = result["thread_id"];

	if(mtype == 0):
		msg = result["content"];
		Amino.send(message=msg, community_id=community_id, thread_id=thread_id);
