import requests
import json
from time import timezone
from time import time as timestamp
from websocket import create_connection
import base64

class Client:
	sid = "";
	auid = "";

	def login(email, password):
		global sid, auid;
		result = requests.post("https://service.narvii.com/api/v1/g/s/auth/login", data=json.dumps({"email":email,"secret":"0 "+password,"deviceID":"015051B67B8D59D0A86E0F4A78F47367B749357048DD5F23DF275F05016B74605AAB0D7A6127287D9C","clientType":100,"action":"normal","timestamp":(int(timestamp() * 1000))}), headers={'Content-Type': 'application/json'}).json()
		sid = result["sid"];
		auid = result["auid"];
		return result

	def getMessages(community_id, thread_id, size):
		global sid;
		res = requests.get("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/chat/thread/"+thread_id+"/message?v=2&pagingType=t&size="+str(size)+"&sid="+sid, headers={'Content-Type': 'application/json'})
		return res.json()

	def getThread(community_id, thread_id):
		global sid;
		res = requests.post("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/chat/thread/"+thread_id+"?sid="+sid, headers={'Content-Type': 'application/json'});
		return res.json()

	def ban(userId: str, community_id, reason: str, banType: int = None):
		global sid;

		response = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/user-profile/"+userId+"/ban?sid="+sid, headers={'Content-Type': 'application/json'}, data={
		    "reasonType": banType,
		    "note": {
		        "content": reason
		    },
		    "timestamp": int(timestamp() * 1000)
		}).json();
		return response;

	def get_banned_users(community_id, start: int = 0, size: int = 25):
		global sid;
		response = requests.get("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/user-profile?type=banned&start="+str(start)+"&size="+str(size)+"&sid="+sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def unban(community_id, userId: str, reason: str):
		global sid;
		data = json.dumps({
		    "note": {
		        "content": reason
		    },
		    "timestamp": int(timestamp() * 1000)
		})

		response = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/user-profile/"+userId+"/unban?sid="+sid, headers={'Content-Type': 'application/json'}, data=data)
		return response.json();

	def listen():
		global sid
		ws = create_connection("wss://ws1.narvii.com?signbody=015051B67B8D59D0A86E0F4A78F47367B749357048DD5F23DF275F05016B74605AAB0D7A6127287D9C%7C"+str((int(timestamp() * 1000)))+"&sid="+sid);
		return json.loads(ws.recv());

	def setNickname(nickname, community_id, uid):
		global sid;
		result = requests.post("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/user-profile/"+uid+"?sid="+sid,
			data=json.dumps({"nickname":nickname, "timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def createUserChat(message, com, uid):
		global sid;
		result = requests.post("https://service.narvii.com/api/v1/x"+str(com)+"/s/chat/thread?sid="+sid,
			data=json.dumps({'inviteeUids': [uid],"initialMessageContent":None,"type":0,"timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def deleteMessage(thread_id: str, community_id, messageId: str, asStaff: bool = False, reason: str = None):
		global sid;
		data = json.dumps({
		    "adminOpName": 102,
		    "adminOpNote": {"content": reason},
		    "timestamp": int(timestamp() * 1000)
		})
		if not asStaff: response = requests.delete("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/chat/thread/"+thread_id+"/message/"+messageId+"?sid="+sid, headers={'Content-Type': 'application/json'})
		else: response = requests.post("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/chat/thread/"+thread_id+"/message/"+messageId+"/admin?sid="+sid, headers={'Content-Type': 'application/json'}, data=data)
		return response.json()

	def kick(author: str, thread_id: str, community_id, allowRejoin):
		global sid;
		response = requests.delete("https://service.narvii.com/api/v1/x"+community_id+"/s/chat/thread/"+thread_id+"/member/"+author+"?allowRejoin="+str(allowRejoin)+"&sid="+sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def loadStickerImage(path):
		global sid;
		result = requests.post("https://service.narvii.com/api/v1/g/s/media/upload/target/sticker?sid="+sid,
			data=requests.get(path).content,
			headers={'Content-Type': 'application/octet-stream'}).json();
		return result;

	def createStickerpack(name, stickers, community_id):
		global sid;
		result = requests.post("https://service.narvii.com/api/v1/x"+str(com)+"/s/sticker-collection?sid="+sid,
			data=json.dumps({"collectionType":3,"description":"stickerpack","iconSourceStickerIndex":0,"name":name,"stickerList":stickers,"timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def searchUserThread(uid, community_id):
		global sid;
		result = requests.get("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/chat/thread?type=exist-single&cv=1.2&q="+uid+"&sid="+sid).json();
		return result;

	def send(message, community_id, thread_id):
		global sid
		result = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/chat/thread/"+thread_id+"/message?sid="+sid,
			data=json.dumps({"content":message,"type":0,"clientRefId":43196704,"timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def sendSystem(message, community_id, thread_id):
		global sid;
		result = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/chat/thread/"+thread_id+"/message?sid="+sid,
			data=json.dumps({"content":message,"type":100,"clientRefId":43196704,"timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def adminDeleteMessage(mid, community_id, thread_id):
		global sid;
		result = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/chat/thread/"+thread_id+"/message/"+mid+"/admin?sid="+sid,
			data=json.dumps({"adminOpName": 102, "timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def getUsersThread(community_id, thread_id):
		global sid
		result = requests.get("https://service.narvii.com/api/v1/x"+community_id+"/s/chat/thread/"+thread_id+"/member?sid="+sid+"&type=default&start=0&size=50").json();
		return result;

	def getChats(com, start, size):
		global sid;
		result = requests.get("https://service.narvii.com/api/v1/x"+str(com)+"/s/chat/thread?type=joined-me&start="+str(start)+"&size="+str(size)+"&sid="+sid).json();
		return result;

	def getUser(uid, com):
		global sid;
		result = requests.get("https://service.narvii.com/api/v1/x"+str(com)+"/s/user-profile/"+str(uid)+"?action=visit&sid="+sid).json();
		return result;

	def sendImage(image, community_id, thread_id):
		global sid;
		img = base64.b64encode(open(image, "rb").read())
		result = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/chat/thread/"+thread_id+"/message?sid="+sid,
			data=json.dumps({"type":0,"clientRefId":43196704,"timestamp":(int(timestamp() * 1000)),"mediaType":100,"mediaUploadValue":img.strip().decode(),"mediaUploadValueContentType" : "image/jpg","mediaUhqEnabled":False,"attachedObject":None}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def join_chat(community_id, thread_id):
		global sid, auid;
		response = requests.post("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/chat/thread/"+thread_id+"/member/"+auid+"?sid="+sid, headers={'Content-Type': 'application/json'}).json()
		return response;

	def leave_chat(community_id, thread_id):
		global sid, auid;
		response = requests.delete("https://service.narvii.com/api/v1/x"+str(community_id)+"/s/chat/thread/"+thread_id+"/member/"+auid+"?sid="+sid, headers={'Content-Type': 'application/json'}).json()
		return response;

	def sendGif(image, community_id, thread_id):
		global sid;
		img = base64.b64encode(open(image, "rb").read())
		result = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/chat/thread/"+thread_id+"/message?sid="+sid,
			data=json.dumps({"type":0,"clientRefId":43196704,"timestamp":(int(timestamp() * 1000)),"mediaType":100,"mediaUploadValue":img.strip().decode(),"mediaUploadValueContentType" : "image/gid","mediaUhqEnabled":False,"attachedObject":None}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def commentProfile(content, community_id, author):
		global sid;
		result = requests.post("https://service.narvii.com/api/v1/x"+community_id+"/s/user-profile/"+author+"/comment?sid="+sid,
			data=json.dumps({"content":content,'mediaList': [],"eventSource":"PostDetailView","timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;
