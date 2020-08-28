from amino import Client

Amino = Client(email="email", password="password");

while True:
	try:
		result = Amino.listen();
	except:
		continue;

	if(result["t"] == 1000):
		mtype = result["o"]["chatMessage"]["type"];
		community_id = str(result["o"]["ndcId"]);
		thread_id = result["o"]["chatMessage"]["threadId"];

		if(mtype == 0):
			msg = result["o"]["chatMessage"]["content"];
			Amino.send(message=msg, community_id=community_id, thread_id=thread_id);
