# coding=utf-8
import requests
import json
import time
from websocket import create_connection
import base64
from typing import BinaryIO
import random
from string import hexdigits
from uuid import UUID
from binascii import hexlify
from os import urandom
from locale import getdefaultlocale as locale
from hashlib import sha1
import string

class Client:

	def __init__(self, email, password, device_id:str="22F67FB1D87173A6C295BD38AAE7806CCC0173C2A788F6D8E6D66C0A3F29D038C10CD30964D672AB56", proxy:dict=None):
		self.device_id = device_id
		self.api = "https://service.narvii.com/api/v1/"
		self.proxy = proxy
		self.sid = None
		self.headers = {
			"NDCDEVICEID": self.device_id,
			"NDCAUTH":"",
			"Accept-Language": "en-US",
			"Content-Type": "application/json; charset=utf-8",
			"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)", 
			"Host": "service.narvii.com",
			"Accept-Encoding": "gzip",
			"Connection": "Keep-Alive"
		}
		if email and password:
			self.login(email, password)

	def login(self, email, password):
		data = {
			"auth_type": 0,
			"recaptcha_challenge": "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + "_-", k=462)).replace("--", "-"),
			"recaptcha_version": "v3",
			"secret": password,
			"email":email
		}
		result = requests.post("https://aminoapps.com/api/auth", json=data)
		json = result.json()
		headers = result.headers
		if json.get("code") == 200:
			self.sid = headers["set-cookie"][4:195]
			self.headers["NDCAUTH"] = headers["set-cookie"][4:195]
			self.auid = json["result"]["uid"]
			#self.reload_socket()
		else:
			print(">> Error: " + json["api:message"])


	def register(self, nickname: str = None, email: str = None, password: str = None, verificationCode:str=None, deviceId: str = None):
		if not deviceId:
			deviceId = self.headers["NDCDEVICEID"]

		data = {
			"secret": f"0 {password}",
			"deviceID": deviceId,
			"email": email,
			"clientType": 100,
			"nickname": nickname,
			"latitude": 0,
			"longitude": 0,
			"address": None,
			"validationContext": {
				"data": {
					"code": verificationCode
				},
				"type": 1,
				"identity": email
			},
			"clientCallbackURL": "narviiapp://relogin",
			"type": 1,
			"identity": email,
			"timestamp": int(time.time() * 1000)
		}

		return requests.post(f"{self.api}g/s/auth/register", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()

	def request_verify_code(self, email):
		data = {
			"identity": email,
			"type": 1,
			"deviceID": self.headers["NDCDEVICEID"]
		}
		response = requests.post(f"{self.api}g/s/auth/request-security-validation", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def get_from_deviceid(self, device_id:str="None"):
		return requests.get(f"{self.api}/g/s/auid?deviceId={device_id}", headers=self.headers, proxies=self.proxy).json()

	def reload_socket(self):
		"""
			!not working
			hold on...
		"""
		self.socket_time = time.time()
		self.ws = create_connection(f"wss://ws1.narvii.com?signbody={self.headers['NDCDEVICEID']}%7C{int(time.time() * 1000)}&sid={self.sid}", header=self.headers)

	def accept_host(self, community_id:int = None, chatId: str = None):
		data = {
			"timestamp": int(time.time() * 1000)
		}
		response = requests.post(f"{self.api}/x{community_id}/s/chat/thread/{chatId}/accept-organizer", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def get_notification(self, community_id, start:int = 0, size:int = 10):
		response = requests.get(f"{self.api}/x{community_id}/s/notification?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return response

	def check_device(self, deviceId: str):
		data = {
			"deviceID": deviceId,
			"bundleID": "com.narvii.amino.master",
			"clientType": 100,
			"timezone": -int(time.timezone) // 1000,
			"systemPushEnabled": True,
			"locale": locale()[0],
			"timestamp": int(time.time() * 1000)
		}

		response = requests.post(f"{self.api}/g/s/device", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def get_wallet_info(self):
		response = requests.get(f"{self.api}/g/s/wallet", headers=self.headers, proxies=self.proxy).json()
		return response

	def get_wallet_history(self, start:int = 0, size:int = 25):
		response = requests.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return response

	def get_communitys(self, start: int = 0, size: int = 25):
		response = requests.get(f"{self.api}g/s/community/joined?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return response

	def watch_ad(self):
		response = requests.post(f"{self.api}g/s/wallet/ads/video/start", headers=self.headers, proxies=self.proxy).json()
		return response

	def transfer_host(self, community_id, chatId: str, userIds: list):
		data = {
			"uidList": userIds,
			"timestamp": int(time.time() * 1000)
		}

		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{chatId}/transfer-organizer", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def join_chat(self, community_id, thread_id):
		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}", headers=self.headers, proxies=self.proxy).json()
		return response

	def getMessages(self, community_id, thread_id, size):
		response = requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?v=2&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy)
		return response

	def getThread(self, community_id, thread_id):
		response = requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}", headers=self.headers, proxies=self.proxy)
		return response

	def sendAudio(self, path, community_id, thread_id):
		audio = base64.b64encode(open(path, "rb").read())
		data = {
			"content":None,
			"type":2,
			"clientRefId":827027430,
			"timestamp":int(time.time() * 1000),
			"mediaType":110,
			"mediaUploadValue":audio,
			"attachedObject":None
		}
		return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()

	def ban(self, userId: str, community_id, reason: str, banType: int = None):
		data = {
			"reasonType": banType,
			"note": {
				"content": reason
			},
			"timestamp": int(time.time() * 1000)
		}
		response = requests.post(f"{self.api}x{community_id}/s/user-profile/{userId}/ban", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def get_banned_users(self, community_id, start: int = 0, size: int = 25):
		response = requests.get(f"{self.api}x{community_id}/s/user-profile?type=banned&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return response

	def unban(self, community_id, userId: str, reason: str):
		data = {
			"note": {
				"content": reason
			},
			"timestamp": int(time.time() * 1000)
		}

		response = requests.post(f"{self.api}x{community_id}/s/user-profile/{userId}/unban", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def listen(self, return_data:int=1):
		if((time.time() - self.socket_time) > 100):
			self.ws.close()
			self.reload_socket()
		res = {}
		while 1:
			try:
				res = json.loads(self.ws.recv())
				break
			except:
				continue
		return res

	def setNickname(self, nickname, community_id):
		data = {
			"nickname":nickname,
			"timestamp":(int(time.time() * 1000))
		}
		result = requests.post(f"{self.api}x{community_id}/s/user-profile/{self.auid}", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def createUserChat(self, message, community_id, uid):
		data = {
			'inviteeUids': [uid],
			"initialMessageContent":message,
			"type":0,
			"timestamp":(int(time.time() * 1000))
		}
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def deleteMessage(self, thread_id: str, community_id, messageId: str, asStaff: bool = False, reason: str = None):
		data = {
			"adminOpName": 102,
			"adminOpNote": {"content": reason},
			"timestamp": int(time.time() * 1000)
		}

		if not asStaff: response = requests.delete(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message/{messageId}", headers=self.headers, proxies=self.proxy).json()
		else: response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message/{messageId}/admin", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		
		return response

	def kick(self, author: str, thread_id: str, community_id, allowRejoin:int = 0):
		response = requests.delete(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{author}?allowRejoin={allowRejoin}", headers=self.headers, proxies=self.proxy).json()
		return response

	def loadStickerImage(self, path):
		result = requests.post(self.api+"g/s/media/upload/target/sticker", data=requests.get(path).content, headers=self.headers, proxies=self.proxy).json()
		return result

	def createStickerpack(self, name, stickers, community_id):
		data = {
			"collectionType":3,
			"description":"stickerpack",
			"iconSourceStickerIndex":0,
			"name":name,
			"stickerList":stickers,
			"timestamp":(int(time.time() * 1000))
		}
		result = requests.post(f"{self.api}x{community_id}/s/sticker-collection", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def searchUserThread(self, uid, community_id):
		result = requests.get(f"{self.api}x{community_id}/s/chat/thread?type=exist-single&cv=1.2&q={uid}", headers=self.headers, proxies=self.proxy).json()
		return result

	def vc_permission(self, community_id: str, thread_id: str, permission: int):
		data = {
			"vvChatJoinType": permission,
			"timestamp": int(time.time() * 1000)
		}
		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/vvchat-permission", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def sendEmbed(self, community_id: str, chatId: str, message: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):
		data = {
			"type": 0,
			"content": message,
			"clientRefId": int(time.time() / 10 % 1000000000),
			"attachedObject": {
				"objectId": None,
				"objectType": 100,
				"link": None,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": b""+embedImage
			},
			"extensions": {"mentionedArray": None},
			"timestamp": int(time.time() * 1000)
		}
		response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{chatId}/message", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def send(self, message, community_id : str, thread_id, reply_message_id:str = None, notifcation : list = None, clientRefId:int=43196704):
		data = {
			"content":message,
			"type":0,
			"clientRefId":clientRefId,
			"mentionedArray": [notifcation],
			"timestamp":(int(time.time() * 1000))
		}
		if (reply_message_id != None): data["replyMessageId"] = reply_message_id
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def sendSystem(self, message, community_id, thread_id):
		data = {
			"content":message,
			"type":100,
			"clientRefId":43196704,
			"timestamp":(int(time.time() * 1000))
		}
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def adminDeleteMessage(self, mid, community_id, thread_id):
		data = {
			"adminOpName": 102,
			"timestamp":(int(time.time() * 1000))
		}
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message/{mid}/admin", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def getUsersThread(self, community_id, thread_id):
		result = requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member&type=default&start=0&size=50", headers=self.headers, proxies=self.proxy).json()
		return result

	def getThreads(self, community_id, start: int = 0, size: int = 5):
		result = requests.get(f"{self.api}x{community_id}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return result

	def thank_tip(self, community_id, thread_id: str, author: str):
		response = requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/tipping/tipped-users/{author}/thank", headers=self.headers, proxies=self.proxy).json()
		return response

	def get_user(self, user_id):
		result = requests.get(f"{self.api}g/s/user-profile/{user_id}?action=visit", headers=self.headers, proxies=self.proxy).json()
		return result

	def get_tipped_users_wall(self, community_id, blog_id, start:int = 0, size:int = 25):
		response = requests.get(f"{self.api}/x{community_id}/s/blog/{blog_id}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return response

	def sendImage(self, image, community_id, thread_id):
		image = base64.b64encode(open(image, "rb").read())
		data = {
			"type":0,
			"clientRefId":43196704,
			"timestamp":(int(time.time() * 1000)),
			"mediaType":100,
			"mediaUploadValue":image.strip().decode(),
			"mediaUploadValueContentType" : "image/jpg",
			"mediaUhqEnabled":False,
			"attachedObject":None
		}
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def join_community(self, community_id: str):
		data = {
			"timestamp": int(time.time() * 1000)
		}
		response = requests.post(f"{self.api}x{community_id}/s/community/join", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return response

	def invite_to_chat(self, community_id, thread_id: str, userId: [str, list]):
		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		
		data = {
			"uids": userIds,
			"timestamp": int(time.time() * 1000)
		}

		response = requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/member/invite", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def get_online_users(self, community_id, start: int = 0, size: int = 25):
		response = requests.get(f"{self.api}/x{community_id}/s/live-layer?topic=ndtopic:x{community_id}:online-members&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return response

	def get_users_community(self, community_id, start:int = 0, size:int = 25):
		response = requests.get(f"{self.api}x{community_id}/s/user-profile?type=recent&start={start}&size={size}", headers=self.headers).json()
		return response

	def get_users(self, start:int=0, size:int=25):
		response = requests.get(f"{self.api}g/s/user-profile?type=recent&start={start}&size={size}", headers=self.headers).json()
		return response

	def leave_chat(self, community_id, thread_id):
		response = requests.delete(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}", headers=self.headers, proxies=self.proxy).json()
		return response

	def sendGif(self, image, community_id, thread_id):
		img = base64.b64encode(open(image, "rb").read())
		data = {
			"type":0,
			"clientRefId":43196704,
			"timestamp":(int(time.time() * 1000)),
			"mediaType":100,
			"mediaUploadValue":img.strip().decode(),
			"mediaUploadValueContentType" : "image/gid",
			"mediaUhqEnabled":False,
			"attachedObject":None
		}
		result = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def commentProfile(self, content, community_id, author):
		data = {
			"content":content,
			'mediaList': [],
			"eventSource":"PostDetailView",
			"timestamp":(int(time.time() * 1000))
		}
		result = requests.post(f"{self.api}x{community_id}/s/user-profile/{author}/comment", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return result

	def get_from_code(self, code: str):
		response = requests.get(f"{self.api}/g/s/link-resolution?q={code}", headers=self.headers, proxies=self.proxy).json()
		return response
	
	def get_user_blogs(self, community_id, author, start:int = 0,size:int = 25):
		response = requests.get(f"{self.api}/x{community_id}/s/blog?type=user&q={author}&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()
		return response

	def get_community_info(self, community_id):
		response = requests.get(f"{self.api}/g/s-x{community_id}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.headers, proxies=self.proxy).json()
		return response

	def check(self, community_id:int = 0, tz: int = -int(time.timezone) // 1000):
		data = {
			"timezone": tz,
			"timestamp": int(time.time() * 1000)
		}

		response = requests.post(f"{self.api}/x{community_id}/s/check-in", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def send_coins_blog(self, community_id:int = 0, blogId:str = None, coins:int = None, transactionId:str = None):
		if(transactionId is None): transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))
		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId},
			"timestamp": int(time.time() * 1000)
		}
		response = requests.post(f"{self.api}/x{community_id}/s/blog/{blogId}/tipping", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		return response

	def send_coins_chat(self, community_id:int = None, thread_id:str = None, coins:int = None, transactionId:str = None):
		if(transactionId is None): transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))
		data = {
			"coins": coins,
			"tippingContext": {"transactionId":transactionId},
			"timestamp": int(time.time() * 1000)
		}
		response = requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/tipping", data=json.dumps(data), headers=self.headers, proxies=self.proxy).json()
		
		return response

	def lottery(self, community_id, tz: str = -int(time.timezone) // 1000):
		data = {
			"timezone": tz,
			"timestamp": int(time.time() * 1000)
		}

		response = requests.post(f"{self.api}/x{community_id}/s/check-in/lottery", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()
		return response

	def edit_thread(self, community_id:int = None, thread_id:str = None, content:str = None, title:str = None, backgroundImage:str = None):
		res = []
		if backgroundImage is not None:
			data = json.dumps({"media": [100, backgroundImage, None], "timestamp": int(time.time() * 1000)})
			response = requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}/background", data=data, headers=self.headers, proxies=self.proxy)
			res.append(response.json())

		data = {"timestamp":int(time.time() * 1000)}

		if(content): data["content"] = content
		if(title):   data["title"]   = title
		response = requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}", headers=self.headers, data=json.dumps(data), proxies=self.proxy)
		res.append(response.json())
		return res
	   
	
	# Moder:{

	def moderation_history_community(self, community_id, size: int = 25):
		return requests.get(f"{self.api}/x{community_id}/s/admin/operation?pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

	def moderation_history_user(self, community_id:int = 0, userId: str = None, size: int = 25):
		return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={userId}&objectType=0&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

	def moderation_history_blog(self, community_id:int = 0, blogId: str = None, size: int = 25):
		return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={blogId}&objectType=1&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

	def moderation_history_quiz(self, community_id:int = 0, quizId: str = None, size: int = 25):
		return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={quizId}&objectType=1&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

	def moderation_history_wiki(self, community_id:int = 0, wikiId: str = None, size: int = 25):
		return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={wikiId}&objectType=2&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

	def give_curator(self, community_id, uid):
		return requests.post(f"{self.api}/x{community_id}/s/user-profile/{uid}/curator", headers=self.headers, data=json.dumps({}), proxies=self.proxy).json()
	
	def give_leader(self, community_id, uid):
		return requests.post(f"{self.api}/x{community_id}/s/user-profile/{uid}/leader", headers=self.headers, data=json.dumps({}), proxies=self.proxy).json()

	# }

	# Bubble:{

	def upload_bubble_1(self, file:str):
		data = open(file, "rb").read()
		return requests.post(f"{self.api}/g/s/media/upload/target/chat-bubble-thumbnail", headers=self.headers, data=data, proxies=self.proxy).json()

	def upload_bubble_2(self, community_id:int, template_id, file):
		data = open(file, "rb").read()
		return requests.post(f"{self.api}/x{community_id}/s/chat/chat-bubble/{template_id}", headers=self.headers,data=data, proxies=self.proxy).json()

	def generate_bubble(self, community_id:int, file:str,template_id:str="fd95b369-1935-4bc5-b014-e92c45b8e222",):
		data = open(file, "rb").read()
		return requests.post(f"{self.api}/x{community_id}/s/chat/chat-bubble/templates/{template_id}/generate", headers=self.headers, data=data, proxies=self.proxy).json()

	def get_bubble_info(self, community_id:int, bid):
		return requests.get(f"{self.api}/x{community_id}/s/chat/chat-bubble/{bid}", headers=self.headers, proxies=self.proxy).json()

	def buy_bubble(self, community_id:int, bid):
		data = {
			"objectId": bid,
			"objectType": 116,
			"v": 1,
			"timestamp": int(time.time() * 1000)
		}
		return requests.post(f"{self.api}x{community_id}/s/store/purchase", headers=self.headers, data=json.dumps(data), proxies=self.proxy).json()

	# }
