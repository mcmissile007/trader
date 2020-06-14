import requests
import json

class Matrix:

    def __init__(self,base_url,user_name,password,user_id = None,home_server = None,access_token = None,room_id = None):
        self.base_url = base_url
        self.user_name = user_name
        self.password = password
        self.user_id = user_id
        self.home_server = home_server
        self.access_token = access_token
        self.room_id = room_id
        
    
    def is_supported_login_password(self):
        r = requests.get(self.base_url + "login")
        if r.status_code != 200 :
             return False
        response = r.json()
        for flow in response['flows']:
            if flow['type'] == "m.login.password":
                return True
        return False
        

    
    def register(self):
        if not self.is_supported_login_password():
            return False
        post_data = {'username': self.user_name,'password':self.password,'auth':{"type":"m.login.password"}}
        r = requests.post(self.base_url + "register", data=json.dumps(post_data))
        if r.status_code != 200:
            return False
        response = r.json()
        if 'user_id' in response:
            self.user_id = response['user_id']
        else:
            return False
        if 'access_token' in response:
            self.access_token = response['access_token']
        else:
            return False
        if 'home_server' in response:
            self.home_server = response['home_server']
        else:
            return False
        return True

    def login(self):
        if not self.is_supported_login_password():
            print("Not supported login password")
            return False
        post_data = {'user': self.user_name,'password':self.password,"type":"m.login.password"}
        r = requests.post(self.base_url + "login", data=json.dumps(post_data))
        if r.status_code != 200:
            return False
        response = r.json()
        if 'user_id' in response:
            self.user_id = response['user_id']
        else:
            return False
        if 'access_token' in response:
            self.access_token = response['access_token']
        else:
            return False
        if 'home_server' in response:
            self.home_server = response['home_server']
        else:
            return False
        return True
    
    def create_room(self,alias_name,name,topic):
        if self.access_token == None:
            return False
        post_data = {"preset": "private_chat","room_alias_name": alias_name,"name": name,"topic": topic,"creation_content": {"m.federate": False }}
        r = requests.post(self.base_url + "createRoom?access_token=" + self.access_token,data = json.dumps(post_data))
        if r.status_code != 200:
            return False
        response = r.json()
        if 'room_id' in response:
            self.room_id = response['room_id']
        else:
            return False
        return True

    def invite_user_to_room(self,user_id,room_id = None):
        if self.access_token == None:
            return False
        if room_id == None  and self.room_id == None:
            return False
        if room_id == None  and self.room_id != None:
            room_id = self.room_id
        post_data = {'user_id': user_id}
        r = requests.post(self.base_url + "rooms/" + room_id + "/invite?access_token=" + self.access_token,data = json.dumps(post_data))
        if r.status_code != 200:
            return False
        return True
    
    def send_message(self,message,room_id = None):
        if self.access_token == None:
            return False
        if room_id == None  and self.room_id == None:
            return False
        if room_id == None  and self.room_id != None:
            room_id = self.room_id
        post_data = {"msgtype":"m.text", "body": message}
        r = requests.post(self.base_url + "rooms/" + room_id + "/send/m.room.message?access_token=" + self.access_token,data = json.dumps(post_data))
        if r.status_code != 200:
            return False
        return True




        





    

    