import random


class RequestHandler:
    @staticmethod
    def classify(body):
        # temporary solution
        emotions = ["sad", "happy"]
        return [random.choice(emotions) for i in range(len(body["sentences"]))]

    @staticmethod
    def learn(body):
        # temporary solution
        return {"success": random.choice([True, False]), "error": "Some custom error"}

    def handle(self, path, body):
        if path in self.mapping:
            return self.mapping[path](body)

    def __init__(self):
        self.mapping = {
            "/api/classify": RequestHandler.classify,
            "/api/learn": RequestHandler.learn
        }