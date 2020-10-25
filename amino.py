# coding=utf-8
import requests
import json
from time import timezone
from time import time as timestamp
from websocket import create_connection
import base64
from typing import BinaryIO

class Client:
	api = "https://service.narvii.com/api/v1/";

	def __init__(self, email, password):
		result = requests.post(self.api+"g/s/auth/login", data=json.dumps({"email":email,"secret":"0 "+password,"deviceID":"015051B67B8D59D0A86E0F4A78F47367B749357048DD5F23DF275F05016B74605AAB0D7A6127287D9C","clientType":100,"action":"normal","timestamp":(int(timestamp() * 1000))}), headers={'Content-Type': 'application/json'}).json()
		self.sid = result["sid"];
		self.auid = result["auid"];

	def get_notification(self, community_id, start:int = 0, size:int = 10):
		response = requests.get(f"{self.api}/x{community_id}/s/notification?start={start}&size={size}&sid="+self.sid, headers={'Content-Type': 'application/json'});
		return response.json();

	def get_wallet_history(self, start:int = 0, size:int = 25):
		response = requests.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}&sid="+self.sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def moderation_history_user(self, community_id, userId: str = None, size: int = 25):
		response = requests.get(self.api+"x"+community_id+"/s/admin/operation?pagingType=t&size="+str(size)+"&sid="+self.sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def get_comms(self, start: int = 0, size: int = 25):
		response = requests.get(f"{self.api}g/s/community/joined?start={start}&size={size}&sid="+self.sid, headers={'Content-Type': 'application/json'}).json()
		return response

	def watch_ad(self):
		response = requests.post(self.api+"g/s/wallet/ads/video/start?sid="+self.sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def transfer_host(self, community_id, chatId: str, userIds: list):
		data = json.dumps({
			"uidList": userIds,
			"timestamp": int(timestamp() * 1000)
		})

		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{chatId}/transfer-organizer?sid="+self.sid, headers={'Content-Type': 'application/json'}, data=data).json()
		return response;

	def join_chat(self, community_id, thread_id):
		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{chat_id}/member/{self.auid}?sid="+self.sid, headers={'Content-Type': 'application/json'}).json()
		return response;

	def getMessages(self, community_id, thread_id, size):
		res = requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?v=2&pagingType=t&size={size}&sid="+self.sid, headers={'Content-Type': 'application/json'})
		return res.json()

	def getThread(self, community_id, thread_id):
		res = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}?sid="+self.sid, headers={'Content-Type': 'application/json'});
		return res.json();

	def sendAudio(self, path, community_id, thread_id):
		audio = base64.b64encode(open(path, "rb").read())
		return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?sid="+self.sid, data=json.dumps({"content":None,"type":2,"clientRefId":827027430,"timestamp":int(timestamp() * 1000),"mediaType":110,"mediaUploadValue":audio,"attachedObject":None}), headers={'Content-Type': 'application/json'}).json();

	def ban(self, userId: str, community_id, reason: str, banType: int = None):

		response = requests.post(f"{self.api}x{community_id}/s/user-profile/{userId}/ban?sid="+self.sid, headers={'Content-Type': 'application/json'}, data={
			"reasonType": banType,
			"note": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		}).json();
		return response;

	def get_banned_users(self, community_id, start: int = 0, size: int = 25):
		response = requests.get(f"{self.api}x{community_id}/s/user-profile?type=banned&start={start}&size={size}&sid="+self.sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def unban(self, community_id, userId: str, reason: str):
		data = json.dumps({
			"note": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = requests.post(self.api+"x"+community_id+"/s/user-profile/"+userId+"/unban?sid="+self.sid, headers={'Content-Type': 'application/json'}, data=data)
		return response.json();

	def listen(self):
		ws = create_connection("wss://ws1.narvii.com?signbody=015051B67B8D59D0A86E0F4A78F47367B749357048DD5F23DF275F05016B74605AAB0D7A6127287D9C%7C"+str((int(timestamp() * 1000)))+"&sid="+self.sid);
		return json.loads(ws.recv());

	def setNickname(self, nickname, community_id, uid):
		result = requests.post(self.api+"x"+str(community_id)+"/s/user-profile/"+uid+"?sid="+self.sid,
			data=json.dumps({"nickname":nickname, "timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def createUserChat(self, message, community_id, uid):
		result = requests.post(self.api+"x"+str(community_id)+"/s/chat/thread?sid="+self.sid,
			data=json.dumps({'inviteeUids': [uid],"initialMessageContent":message,"type":0,"timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;я

	def deleteMessage(self, thread_id: str, community_id, messageId: str, asStaff: bool = False, reason: str = None):
		data = json.dumps({
			"adminOpName": 102,
			"adminOpNote": {"content": reason},
			"timestamp": int(timestamp() * 1000)
		})
		if not asStaff: response = requests.delete(self.api+"x"+str(community_id)+"/s/chat/thread/"+thread_id+"/message/"+messageId+"?sid="+self.sid, headers={'Content-Type': 'application/json'})
		else: response = requests.post(self.api+"x"+str(community_id)+"/s/chat/thread/"+thread_id+"/message/"+messageId+"/admin?sid="+self.sid, headers={'Content-Type': 'application/json'}, data=data)
		return response.json()

	def kick(self, author: str, thread_id: str, community_id, allowRejoin):
		response = requests.delete(self.api+"x"+community_id+"/s/chat/thread/"+thread_id+"/member/"+author+"?allowRejoin="+str(allowRejoin)+"&sid="+self.sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def loadStickerImage(self, path):
		result = requests.post(self.api+"g/s/media/upload/target/sticker?sid="+self.sid,
			data=requests.get(path).content,
			headers={'Content-Type': 'application/octet-stream'}).json();
		return result;

	def createStickerpack(self, name, stickers, community_id):
		result = requests.post(self.api+"x"+str(com)+"/s/sticker-collection?sid="+self.sid,
			data=json.dumps({"collectionType":3,"description":"stickerpack","iconSourceStickerIndex":0,"name":name,"stickerList":stickers,"timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def searchUserThread(self, uid, community_id):
		result = requests.get(self.api+"x"+str(community_id)+"/s/chat/thread?type=exist-single&cv=1.2&q="+uid+"&sid="+self.sid).json();
		return result;

	def vc_permission(self, community_id: str, thread_id: str, permission: int):
		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/vvchat-permission?sid="+self.sid,headers={'Content-Type': 'application/json'}, data=json.dumps({"vvChatJoinType": permission,"timestamp": int(timestamp() * 1000)}))
		return response.json();

	def sendEmbed(self, community_id: str, chatId: str, message: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):
		data = {
			"type": 0,
			"content": message,
			"clientRefId": int(timestamp() / 10 % 1000000000),
			"attachedObject": {
				"objectId": None,
				"objectType": 100,
				"link": None,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": b""+embedImage
			},
			"extensions": {"mentionedArray": None},
			"timestamp": int(timestamp() * 1000)
		}
		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{chatId}/message?sid="+self.sid, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
		return response.json()

	def send(self, message, community_id : str, thread_id, notifcation : list = None):
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?sid="+self.sid,
			data=json.dumps({"content":message,"type":0,"clientRefId":43196704,"mentionedArray": [notifcation], "timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def sendSystem(self, message, community_id, thread_id):
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?sid="+self.sid,
			data=json.dumps({"content":message,"type":100,"clientRefId":43196704,"timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def adminDeleteMessage(self, mid, community_id, thread_id):
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message/{mid}/admin?sid="+self.sid,
			data=json.dumps({"adminOpName": 102, "timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def getUsersThread(self, community_id, thread_id):
		result = requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member?sid="+self.sid+"&type=default&start=0&size=50").json();
		return result;

	def getThreads(self, community_id, start: int = 0, size: int = 5):
		result = requests.get(f"{self.api}x{community_id}/s/chat/thread?type=joined-me&start={start}&size={size}&sid="+self.sid).json();
		return result;

	def thank_tip(self, community_id, thread_id: str, author: str):
		response = requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/tipping/tipped-users/{author}/thank?sid="+self.sid, headers={'Content-Type': 'application/json'})
		return response.json();

	def getUser(self, user_id, community_id):
		result = requests.get(f"{self.api}x{community_id}/s/user-profile/{user_id}?action=visit&sid="+self.sid).json();
		return result;

	def get_tipped_users_wall(self, community_id, blog_id, start:int = 0, size:int = 25):
		response = requests.get(f"{self.api}/x{community_id}/s/blog/{blog_id}/tipping/tipped-users-summary?start={start}&size={size}&sid="+self.sid, headers={'Content-Type': 'application/json'});
		return response.json();

	def sendImage(self, image, community_id, thread_id):
		img = base64.b64encode(open(image, "rb").read())
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?sid="+self.sid,
			data=json.dumps({"type":0,"clientRefId":43196704,"timestamp":(int(timestamp() * 1000)),"mediaType":100,"mediaUploadValue":img.strip().decode(),"mediaUploadValueContentType" : "image/jpg","mediaUhqEnabled":False,"attachedObject":None}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def join_community(self, community_id: str):
		response = requests.post(f"{self.api}x{community_id}/s/community/join?sid="+self.sid, data=json.dumps({"timestamp": int(timestamp() * 1000)}), headers={'Content-Type': 'application/json'}).json()
		return response

	def join_chat(self, community_id, thread_id):
		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}?sid="+self.sid, headers={'Content-Type': 'application/json'}).json()
		return response;

	def get_users_community(self, community_id, start:int = 0, size:int = 25):
		response = requests.get(f"{self.api}x{community_id}/s/user-profile?type=recent&start={start}&size={size}&sid="+self.sid).json();
		return response

	def leave_chat(self, community_id, thread_id):
		response = requests.delete(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}?sid="+self.sid, headers={'Content-Type': 'application/json'}).json()
		return response;

	def sendGif(self, image, community_id, thread_id):
		img = base64.b64encode(open(image, "rb").read())
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?sid="+self.sid,
			data=json.dumps({"type":0,"clientRefId":43196704,"timestamp":(int(timestamp() * 1000)),"mediaType":100,"mediaUploadValue":img.strip().decode(),"mediaUploadValueContentType" : "image/gid","mediaUhqEnabled":False,"attachedObject":None}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def commentProfile(self, content, community_id, author):
		result = requests.post(f"{self.api}x{community_id}/s/user-profile/{author}/comment?sid="+self.sid,
			data=json.dumps({"content":content,'mediaList': [],"eventSource":"PostDetailView","timestamp":(int(timestamp() * 1000))}),
			headers={'Content-Type': 'application/json'}).json();
		return result;

	def get_user_blogs(self, community_id, author, start:int = 0,size:int = 25):
		response = requests.get(f"{self.api}/x{community_id}/s/blog?type=user&q={author}&start={start}&size={size}&sid="+self.sid, headers={'Content-Type': 'application/json'})
		return response.json()

	def get_community_info(self, community_id):
		response = requests.get(f"{self.api}/g/s-x{community_id}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers={'Content-Type': 'application/json'})
		return response.json();
