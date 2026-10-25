from homeassistant_api import Client
import threading
import queue

class SmartHome:
    def __init__(self, URL, TOKEN):
        self.URL = URL
        self.TOKEN = TOKEN
        self.request_queue = queue.Queue()
        self.resolver = threading.Thread(target=self.resolveRequests,daemon=True)
        self.resolver.start()

    def resolveRequests(self):
        with Client(self.URL, self.TOKEN) as client:
            if client.check_api_running():
                print("Connected to homeassistant")
                while True:
                    data = self.request_queue.get()
                    print("got data {}".format(data))
                    domain = client.get_domain(data["domain"])
                    if data["domain"] == "light":
                        domain.turn_on(entity_id=data["id"],brightness_pct=data["brightness"])
                    if data["domain"] == "lock":
                        if data["action"] == "unlock":
                            domain.unlock(id=data["id"])
                        if data["action"] == "lock":
                            domain.lock(id=data["id"])
                    if data["domain"] == "media_player":
                        if data["action"] == "play.music":
                            domain.play_media(
                                entity_id=data["id"],
                                media_content_id=data["content"],
                                media_content_type="music",
                            )
                        if data["action"] == "play.video":
                            domain.play_media(
                                entity_id=data["id"],
                                media_content_id=data["content"],
                                media_content_type="video",
                            )
                        if data["action"] == "stop":
                            domain.media_stop(entity_id=data["id"])
                        if data["action"] == "pause":
                            domain.media_pause(entity_id=data["id"])

    def lightOn(self,id,brightness=100):
        self.request_queue.put({"domain":"light","id":id,"brightness":brightness})
        return True

    def lightOff(self,id):
        self.request_queue.put({"domain":"light","id":id,"brightness":0})
        return True

    def lockUnlock(self,id):
        self.request_queue.put({"domain":"lock","id":id,"action":"unlock"})

    def lockLock(self,id):
        self.request_queue.put({"domain":"lock","id":id,"action":"lock"})

    def mediaStartMusic(self,id,content):
        self.request_queue.put({"domain":"media_player","id":id,"action":"play.music","content":content})

    def mediaStartVideo(self,id,content):
        self.request_queue.put({"domain":"media_player","id":id,"action":"play.video","content":content})

    def mediaStop(self,id):
        self.request_queue.put({"domain":"media_player","id":id,"action":"stop"})

    def mediaPause(self,id):
        self.request_queue.put({"domain":"media_player","id":id,"action":"pause"})