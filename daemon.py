import json
import threading

import redis

from config import *
from utils import motor


class Runner(threading.Thread):
    def __init__(self, redis_obj, channels):
        self.redis = redis_obj
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)

    def run_motor(self, cmd_str):
        # TODO: setup method to track whether pins are configured
        motor.setup()
        if cmd_str in ['forward', 'f']:
            motor_cmd = motor.forward
        elif cmd_str in ['reverse', 'r']:
            motor_cmd = motor.reverse
        elif cmd_str in ['left', 'l']:
            motor_cmd = motor.left
        elif cmd_str in ['right', 'r']:
            motor_cmd = motor.right
        elif cmd_str in ['stop', 's']:
            motor_cmd = motor.stop
        else:
            motor_cmd = None

        if motor_cmd:
            motor_cmd()

    def work(self, item):
        try:
            data = json.loads(item.get('ctrl', '{}'))
        except ValueError:
            # TODO: add logging statement about failure to load
            data = {}

        motor_cmd_str = data.get('motor', None)
        if motor_cmd_str:
            self.run_motor(motor_cmd_str)

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                self.work(item)

if __name__ == "__main__":
    client = Runner(redis.Redis(), ['ctrl'])
    client.start()
