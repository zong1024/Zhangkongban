try:
    import ujson as json
except ImportError:
    import json

import urequests
from umqtt.simple import MQTTClient


def _ensure_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


class LocalHttpClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def _url(self, path):
        if not path:
            return self.base_url
        if path.startswith("/"):
            return self.base_url + path
        return self.base_url + "/" + path

    def get_json(self, path="", headers=None):
        response = urequests.get(self._url(path), headers=headers)
        try:
            return response.json()
        finally:
            response.close()

    def post_json(self, path="", payload=None, headers=None):
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload or {})
        response = urequests.post(self._url(path), data=body, headers=headers)
        try:
            try:
                return response.json()
            except Exception:
                return response.text
        finally:
            response.close()


class LocalMqttClient:
    def __init__(
        self,
        server,
        client_id,
        port=1883,
        user=None,
        password=None,
        keepalive=60,
        ssl=False,
        ssl_params=None,
    ):
        if ssl_params is None:
            ssl_params = {}
        self._client = MQTTClient(
            client_id=client_id,
            server=server,
            port=port,
            user=user,
            password=password,
            keepalive=keepalive,
            ssl=ssl,
            ssl_params=ssl_params,
        )

    def connect(self, clean_session=True):
        return self._client.connect(clean_session=clean_session)

    def disconnect(self):
        self._client.disconnect()

    def set_callback(self, callback):
        self._client.set_callback(callback)

    def subscribe(self, topic):
        self._client.subscribe(_ensure_bytes(topic))

    def publish(self, topic, payload, retain=False, qos=0):
        self._client.publish(
            _ensure_bytes(topic),
            _ensure_bytes(payload),
            retain=retain,
            qos=qos,
        )

    def publish_json(self, topic, payload, retain=False, qos=0):
        self.publish(topic, json.dumps(payload), retain=retain, qos=qos)

    def check(self):
        self._client.check_msg()

    def wait(self):
        self._client.wait_msg()
