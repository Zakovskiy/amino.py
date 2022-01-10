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
import hmac


class Client:
    """
    This is a library for interacting with API Amino

    """

    def __init__(self, email: str = None, password: str = None, device_id: str = "32423150F789A8189A0DDA94FEF4FE6257F797CE5C8CCAEB3E6BA2A8208685E504F77D67524433664C", proxy: dict = None) -> None:
        """
        **Params**
            - email : email address from account
            - password : password from account
        """
        self.device_id = device_id
        self.api = "https://service.narvii.com/api/v1/"
        self.proxy = proxy
        self.sid = None
        self.headers = {
            "NDCDEVICEID": self.device_id,
            "NDC-MSG-SIG": "",
            "NDCAUTH": "",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)", 
        }
        if email and password: self.login(email, password)

    def login(self, email: str, password: str, socket: bool = True) -> dict:
        """
        Login into account

        **Params**
            - email : email address from account
            - password : password from account
        """
        data = json.dumps({
            "email": email,
            "secret": f"0 {password}",
            "deviceID": self.headers["NDCDEVICEID"],
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        response = requests.post(f"{self.api}g/s/auth/login", data=data, headers=self.headers, proxies=self.proxy).json()
        if "sid" in response:
            self.sid = response["sid"]
            self.auid = response["auid"]
            self.headers["NDCAUTH"] = f"sid={self.sid}"
            if socket: self.reload_socket()
        else:
            print(f">>Error: {response['api:message']}")
        return response

    def generate_signature(self, data: str) -> str:
        try:
            mac = hmac.new(bytes.fromhex("fbf98eb3a07a9042ee5593b10ce9f3286a69d4e2"), data.encode("utf-8"), sha1)
            signature = base64.b64encode(bytes.fromhex("32") + mac.digest()).decode("utf-8")
            self.headers["NDC-MSG-SIG"] = signature
            return signature
        except Exception as e:
            self.generate_signature(data)


    def register(self, nickname: str = None, email: str = None, password: str = None,
        verification_code: str = None, device_id: str = None) -> dict:
        if not device_id: device_id = self.headers["NDCDEVICEID"]

        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": device_id,
            "email": email,
            "clientType": 100,
            "nickname": nickname,
            "latitude": 0,
            "longitude": 0,
            "address": None,
            "validationContext": {
                "data": {
                    "code": verification_code
                },
                "type": 1,
                "identity": email
            },
            "clientCallbackURL": "narviiapp://relogin",
            "type": 1,
            "identity": email,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)

        return requests.post(f"{self.api}g/s/auth/register", data=data, headers=self.headers, proxies=self.proxy).json()

    def request_verify_code(self, email: str) -> dict:
        data = json.dumps({
            "identity": email,
            "type": 1,
            "deviceID": self.headers["NDCDEVICEID"]
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}g/s/auth/request-security-validation", headers=self.headers, data=data, proxies=self.proxy).json()

    def get_from_deviceid(self, device_id: str = "") -> dict:
        return requests.get(f"{self.api}/g/s/auid?deviceId={device_id}", headers=self.headers, proxies=self.proxy).json()

    def reload_socket(self) -> None:
        mil = int(time.time()*1000)
        data = f'{self.device_id}|{mil}'
        self.ws_headers = {
            'NDCDEVICEID': self.device_id,
            'NDCAUTH': f'sid={self.sid}',
            'NDC-MSG-SIG': self.generate_signature(data)
        }
        self.socket_time = time.time()
        self.ws = create_connection(f"wss://ws1.narvii.com?signbody={self.device_id}%7C{int(time.time() * 1000)}&sid={self.sid}", header=self.ws_headers)

    def accept_host(self, community_id: int = None, chatId: str = None) -> dict:
        data = json.dumps({
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}/x{community_id}/s/chat/thread/{chatId}/accept-organizer", headers=self.headers, data=data, proxies=self.proxy).json()

    def get_notification(self, community_id: int, start: int = 0, size: int = 10) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/notification?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def check_device(self, device_id: str) -> dict:
        data = json.dumps({
            "deviceID": device_id,
            "bundleID": "com.narvii.amino.master",
            "clientType": 100,
            "timezone": -int(time.timezone) // 1000,
            "systemPushEnabled": True,
            "locale": locale()[0],
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}/g/s/device", headers=self.headers, data=data, proxies=self.proxy).json()

    def get_wallet_info(self) -> dict:
        return requests.get(f"{self.api}/g/s/wallet", headers=self.headers, proxies=self.proxy).json()

    def get_wallet_history(self, start: int = 0, size: int = 25) -> dict:
        return requests.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def get_communities(self, start: int = 0, size: int = 25) -> dict:
        return requests.get(f"{self.api}g/s/community/joined?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def watch_ad(self) -> dict:
        return requests.post(f"{self.api}g/s/wallet/ads/video/start", headers=self.headers, proxies=self.proxy).json()

    def transfer_host(self, community_id: int, thread_id: str, user_ids: list) -> dict:
        data = json.dumps({
            "uidList": user_ids,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/transfer-organizer", headers=self.headers, data=data, proxies=self.proxy).json()

    def join_chat(self, community_id: int, thread_id: str) -> dict:
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}", headers=self.headers, proxies=self.proxy).json()

    def get_messages(self, community_id: int, thread_id: str, size: int = 25) -> dict:
        return requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message?v=2&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

    def get_thread_info(self, community_id: int, thread_id: str) -> dict:
        return requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}", headers=self.headers, proxies=self.proxy).json()

    def send_audio(self, path: str, community_id: int, thread_id: str):
        data = json.dumps({
            "content": None,
            "type": 2,
            "clientRefId": 827027430,
            "timestamp": int(time.time() * 1000),
            "mediaType": 110,
            "mediaUploadValue": base64.b64encode(open(path, "rb").read()),
            "attachedObject": None
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=data, headers=self.headers, proxies=self.proxy).json()

    def user_ban(self, user_id: str, community_id: int, reason: str, ban_type: int = None) -> dict:
        data = json.dumps({
            "reasonType": ban_type,
            "note": {
                "content": reason
            },
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/user-profile/{user_id}/ban", headers=self.headers, data=data, proxies=self.proxy).json()

    def get_banned_users(self, community_id: int, start: int = 0, size: int = 25):
        return requests.get(f"{self.api}x{community_id}/s/user-profile?type=banned&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def user_unban(self, community_id: int, user_id: str, reason: str) -> dict:
        data = json.dumps({
            "note": {
                "content": reason
            },
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/user-profile/{user_id}/unban", headers=self.headers, data=data, proxies=self.proxy).json()

    def listen(self, return_data: int = 1) -> dict:
        if((time.time() - self.socket_time) > 100):
            self.ws.close()
            self.reload_socket()
        while 1:
            try:
                res = json.loads(self.ws.recv())
                return res
            except:
                continue

    def set_nickname(self, nickname: str, community_id: int) -> dict:
        data = json.dumps({
            "nickname": nickname,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/user-profile/{self.auid}", data=data, headers=self.headers, proxies=self.proxy).json()

    def create_user_chat(self, message: str, community_id: int, user_ids: list) -> dict:
        data = json.dumps({
            'inviteeUids': user_ids,
            "initialMessageContent": message,
            "type": 0,
            "timestamp": int(time.time() * 1000)
        })
        return requests.post(f"{self.api}x{community_id}/s/chat/thread", data=data, headers=self.headers, proxies=self.proxy).json()

    def delete_message(self, thread_id: str, community_id: int, messageId: str,
        asStaff: bool = False, reason: str = None) -> dict:
        data = json.dumps({
            "adminOpName": 102,
            "adminOpNote": {"content": reason},
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        if not asStaff: response = requests.delete(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message/{messageId}", headers=self.headers, proxies=self.proxy).json()
        else: response = requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message/{messageId}/admin", headers=self.headers, data=data, proxies=self.proxy).json()
        
        return response

    def user_kick(self, user_id: str, thread_id: str, community_id: int, allowRejoin: int = 0) -> dict:
        return requests.delete(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{user_id}?allowRejoin={allowRejoin}", headers=self.headers, proxies=self.proxy).json()

    def load_sticker_image(self, link: str) -> dict:
        return requests.post(f"{self.api}g/s/media/upload/target/sticker", data=requests.get(link).content, headers=self.headers, proxies=self.proxy).json()

    def create_stickerpack(self, name: str, stickers: list, community_id: int) -> dict:
        data = json.dumps({
            "collectionType": 3,
            "description": "stickerpack",
            "iconSourceStickerIndex": 0,
            "name": name,
            "stickerList": stickers,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/sticker-collection", data=data, headers=self.headers, proxies=self.proxy).json()

    def search_user_thread(self, user_id: str, community_id: int) -> dict:
        return requests.get(f"{self.api}x{community_id}/s/chat/thread?type=exist-single&cv=1.2&q={user_id}", headers=self.headers, proxies=self.proxy).json()

    def vc_permission(self, community_id: str, thread_id: str, permission: int) -> dict:
        data = json.dumps({
            "vvChatJoinType": permission,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/vvchat-permission", headers=self.headers, data=data, proxies=self.proxy).json()

    def send_embed(self, community_id: str, chatId: str, message: str = None, embedTitle: str = None,
        embedContent: str = None, embedImage: BinaryIO = None) -> dict:
        data = json.dumps({
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
            "extensions": {
                "mentionedArray": None
            },
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{chatId}/message", headers=self.headers, data=data, proxies=self.proxy).json()

    def send_message(self, message: str, community_id: str, thread_id, reply_message_id: str = None,
        notifcation: list = None, clientRefId: int = 43196704) -> dict:
        data = {
            "content": message,
            "type": 0,
            "clientRefId": clientRefId,
            "mentionedArray": [notifcation],
            "timestamp": int(time.time() * 1000)
        }
        if (reply_message_id != None): data["replyMessageId"] = reply_message_id
        data = json.dumps(data)
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=data, headers=self.headers, proxies=self.proxy).json()

    def send_system(self, message: str, community_id: int, thread_id: str) -> dict:
        data = json.dumps({
            "content": message,
            "type": 100,
            "clientRefId": 43196704,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=data, headers=self.headers, proxies=self.proxy).json()

    def admin_delete_message(self, message_id: str, community_id: int, thread_id: str) -> dict:
        data = json.dumps({
            "adminOpName": 102,
            "timestamp":(int(time.time() * 1000))
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message/{mid}/admin", data=data, headers=self.headers, proxies=self.proxy).json()

    def get_users_thread(self, community_id: int, thread_id: str, start: int = 0, size: int = 50) -> dict:
        return requests.get(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member&type=default&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def get_threads(self, community_id: int, start: int = 0, size: int = 5) -> dict:
        return requests.get(f"{self.api}x{community_id}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def thank_tip(self, community_id: int, thread_id: str, user_id: str) -> dict:
        return requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/tipping/tipped-users/{user_id}/thank", headers=self.headers, proxies=self.proxy).json()

    def get_user_global(self, user_id: str) -> dict:
        return requests.get(f"{self.api}g/s/user-profile/{user_id}?action=visit", headers=self.headers, proxies=self.proxy).json()

    def get_tipped_users_wall(self, community_id: int, blog_id: str, start: int = 0, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/blog/{blog_id}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def send_image(self, path: str, community_id: int, thread_id: str) -> dict:
        data = json.dumps({
            "type": 0,
            "clientRefId": 43196704,
            "timestamp": int(time.time() * 1000),
            "mediaType": 100,
            "mediaUploadValue": base64.b64encode(open(path, "rb").read()).strip().decode(),
            "mediaUploadValueContentType" : "image/jpg",
            "mediaUhqEnabled": False,
            "attachedObject": None
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/message", data=data, headers=self.headers, proxies=self.proxy).json()

    def join_community(self, community_id: str) -> dict:
        data = json.dumps({
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/community/join", data=data, headers=self.headers, proxies=self.proxy).json()

    def invite_to_chat(self, community_id: str, thread_id: str, userId: [str, list]) -> dict:
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        
        data = json.dumps({
            "uids": userIds,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/member/invite", headers=self.headers, data=data, proxies=self.proxy).json()

    def get_online_users(self, community_id: int, start: int = 0, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/live-layer?topic=ndtopic:x{community_id}:online-members&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def get_users_community(self, community_id: int, start: int = 0, size: int = 25) -> dict:
        return requests.get(f"{self.api}x{community_id}/s/user-profile?type=recent&start={start}&size={size}", headers=self.headers).json()

    def get_global_users(self, start: int = 0, size: int = 25) -> dict:
        return requests.get(f"{self.api}g/s/user-profile?type=recent&start={start}&size={size}", headers=self.headers).json()

    def leave_chat(self, community_id: int, thread_id: str) -> dict:
        return requests.delete(f"{self.api}x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}", headers=self.headers, proxies=self.proxy).json()

    def comment_profile(self, community_id, user_id, content) -> dict:
        data = json.dumps({
            "content": content,
            'mediaList': [],
            "eventSource": "PostDetailView",
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/user-profile/{user_id}/comment", data=data, headers=self.headers, proxies=self.proxy).json()

    def get_from_code(self, code: str) -> dict:
        return requests.get(f"{self.api}/g/s/link-resolution?q={code}", headers=self.headers, proxies=self.proxy).json()
    
    def get_user_blogs(self, community_id: int, user_id, start: int = 0, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/blog?type=user&q={user_id}&start={start}&size={size}", headers=self.headers, proxies=self.proxy).json()

    def get_community_info(self, community_id: int) -> dict:
        return requests.get(f"{self.api}/g/s-x{community_id}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.headers, proxies=self.proxy).json()

    def check(self, community_id:int = 0, tz: int = -int(time.timezone) // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}/x{community_id}/s/check-in", headers=self.headers, data=data, proxies=self.proxy).json()

    def send_coins_blog(self, community_id: int = 0, blog_id: str = None, coins: int = None, transactionId: str = None):
        if(transactionId is None): transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))
        data = json.dumps({
            "coins": coins,
            "tippingContext": {"transactionId": transactionId},
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}/x{community_id}/s/blog/{blog_id}/tipping", data=data, headers=self.headers, proxies=self.proxy).json()

    def send_coins_chat(self, community_id: int = None, thread_id: str = None,
        coins: int = None, transactionId: str = None) -> dict:
        if(transactionId is None): transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = json.dumps({
            "coins": coins,
            "tippingContext": {
                "transactionId":transactionId
            },
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        
        return requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/tipping", data=data, headers=self.headers, proxies=self.proxy).json()

    def lottery(self, community_id: int, tz: str = -int(time.timezone) // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}/x{community_id}/s/check-in/lottery", headers=self.headers, data=data, proxies=self.proxy).json()

    def edit_thread(self, community_id: int = None, thread_id: str = None, content: str = None,
        title: str = None, backgroundImage: str = None) -> dict:
        if backgroundImage:
            data = json.dumps({
                "media": [100, backgroundImage, None],
                "timestamp": int(time.time() * 1000)
            })
            self.generate_signature(data)
            requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}/member/{self.auid}/background", data=data, headers=self.headers, proxies=self.proxy).json()

        data = {
            "timestamp":int(time.time() * 1000)
        }

        if(content): data["content"] = content
        if(title):   data["title"]   = title
        data = json.dumps(data)
        self.generate_signature(data)
        return requests.post(f"{self.api}/x{community_id}/s/chat/thread/{thread_id}", headers=self.headers, data=data, proxies=self.proxy).json()
       
    
    # Moder:{

    def moderation_history_community(self, community_id: int, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/admin/operation?pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

    def moderation_history_user(self, community_id: int, userId: str = None, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={userId}&objectType=0&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

    def moderation_history_blog(self, community_id: int, blog_id: str = None, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={blog_id}&objectType=1&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

    def moderation_history_quiz(self, community_id: int, quiz_id: str = None, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={quiz_id}&objectType=1&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

    def moderation_history_wiki(self, community_id: int, wiki_id: str = None, size: int = 25) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/admin/operation?objectId={wiki_id}&objectType=2&pagingType=t&size={size}", headers=self.headers, proxies=self.proxy).json()

    def give_curator(self, community_id: int, user_id: str) -> dict:
        return requests.post(f"{self.api}/x{community_id}/s/user-profile/{user_id}/curator", headers=self.headers, data=json.dumps({}), proxies=self.proxy).json()
    
    def give_leader(self, community_id: int, user_id: str) -> dict:
        return requests.post(f"{self.api}/x{community_id}/s/user-profile/{user_id}/leader", headers=self.headers, data=json.dumps({}), proxies=self.proxy).json()

    # }

    # Bubble:{

    def upload_bubble_1(self, path: str) -> dict:
        data = open(path, "rb").read()
        return requests.post(f"{self.api}/g/s/media/upload/target/chat-bubble-thumbnail", headers=self.headers, data=data, proxies=self.proxy).json()

    def upload_bubble_2(self, community_id: int, template_id: str, path: str) -> dict:
        data = open(path, "rb").read()
        return requests.post(f"{self.api}/x{community_id}/s/chat/chat-bubble/{template_id}", headers=self.headers,data=data, proxies=self.proxy).json()

    def generate_bubble(self, community_id: int, path: str, template_id: str = "fd95b369-1935-4bc5-b014-e92c45b8e222",) -> dict:
        data = open(path, "rb").read()
        return requests.post(f"{self.api}/x{community_id}/s/chat/chat-bubble/templates/{template_id}/generate", headers=self.headers, data=data, proxies=self.proxy).json()

    def get_bubble_info(self, community_id: int, bubble_id) -> dict:
        return requests.get(f"{self.api}/x{community_id}/s/chat/chat-bubble/{bubble_id}", headers=self.headers, proxies=self.proxy).json()

    def buy_bubble(self, community_id: int, bubble_id) -> dict:
        data = json.dumps({
            "objectId": bubble_id,
            "objectType": 116,
            "v": 1,
            "timestamp": int(time.time() * 1000)
        })
        self.generate_signature(data)
        return requests.post(f"{self.api}x{community_id}/s/store/purchase", headers=self.headers, data=data, proxies=self.proxy).json()

    # }