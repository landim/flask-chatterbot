from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

app = Flask(__name__)

#english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
english_bot = ChatBot("English Bot", 
                    storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
                    database = "bot",
                    database_uri = "mongodb://mongo_user:mongo_secret@0.0.0.0:27017/admin")
trainer = ChatterBotCorpusTrainer(english_bot)
trainer.train("chatterbot.corpus.ecwo")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(english_bot.get_response(userText))


if __name__ == "__main__":
    app.run()
