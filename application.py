import requests
import re
from flask import Flask
from flask import request, redirect
import os


app = Flask(__name__)

api_key = os.environ['API_KEY']
app_name = "Trello-Github"


def add_comment(token, boards, commit):
    endpoint = "https://api.trello.com/1/"

    short_id = re.match(r".*#([0-9]+).*", commit['message']).group(1)
    board = re.match(r".*#([a-z-]+).*", commit['message']).group(1)

    if not short_id:
        print("no short id")
        return False

    if not board:
        print("no board_id")
        return False

    if board not in boards:
        print("board id invalid")
        return False

    url = "{}boards/{}/cards?key={}&token={}".format(endpoint, boards[board], api_key, token)

    card_to_comment = None
    for card in requests.get(url).json():
        if str(card['idShort']) == short_id:
            card_to_comment = card
            break

    if not card_to_comment:
        print("no matching card")
        return False

    message = commit['message'].replace("#{}".format(board), "").replace("#{}".format(short_id), "").strip()
    comment = "{} - {}\n{}".format(commit['user'], message, commit['url'])

    url = "{}cards/{}/actions/comments?key={}&token={}".format(endpoint, card_to_comment['shortLink'], api_key, token)
    requests.post(url, {"text": comment})


@app.route('/token')
def token():
    return redirect('https://trello.com/1/authorize?key={}&name={}&expiration=never&response_type=token&scope=read,write'.format(api_key, app_name))


@app.route('/test')
def token():
    if "board" not in request.args or "token" not in request.args:
        return "Include board ID and token in the url (/token to get a token)"

    url = "{}boards/{}/cards?key={}&token={}".format(endpoint, request.args['board'] api_key, request.args['token'])
    return requests.get(url).text


# order-processing=sgxSNLsD&com=teAbm4HS&token=5f155...209e8
@app.route('/webhook', methods=["POST"])
def hello_world():

    boards = {}
    for k, v in request.args.items():
        boards[k] = v
    token = boards['token']
    del boards['token']

    for commit in request.get_json(force=True)['commits']:

        add_comment(token, boards, {
            "message": commit['message'],
            "url": commit['url'],
            "user": commit['author']['name']
        })
    return "Done."

if __name__ == '__main__':
    app.run(debug=True)
