import json

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests


class Users(object):
    def __init__(self):
        self.users = []
        self.posts = []
        self.community = []

    def add_user(self, user):
        self.users.append(user)

    def create_user(self, username):
        user = {
            'username': username
        }
        self.add_user(user)

    def add_post(self, username, caption, timestamp=time()):
        post = {
            'username': username,
            'caption': caption,
            'timestamp': timestamp
        }
        self.posts.append(post)

    def get_post(self, username):
        user_posts = []
        for post in self.posts:
            if post.get('username') == username:
                user_posts.append(post)
            elif self.isCommunity(post.get('username'),username):
                user_posts.append(post)

        return user_posts

    def isCommunity(self,follower,leader):
        for community in self.community:
            if community.get('leader') == leader:
                if community.get('follower') == follower:
                    return True
        return False

    def add_to_community(self,leader,follower):
        community = {
            'leader': leader,
            'follower': follower
        }
        self.community.append(community)

    def get_user_community(self,username):
        user_community = []
        for follower in self.community:
            if follower.get('leader') == username:
                user_community.append({
                    'follower': follower.get('follower')
                })

        return user_community

    def verifyUser(self, username):
        for user in self.users:
            if username == user.get("username"):
                return True
        return False


app = Flask(__name__)

users = Users()


@app.route("/createUser", methods=["POST"])
def register_user():
    values = request.get_json()
    required = ['username']
    if not all(k in values for k in required):
        return 'Missing values', 400

    users.create_user(values.get('username'))

    response = {'message': f'User successfuly created'}
    return jsonify(response), 201

@app.route("/addPost", methods = ["POST"])
def post():
    values = request.get_json()
    required = ['username', 'caption']
    if not all(k in values for k in required):
        return 'Missing valuse', 400

    if not users.verifyUser(values.get('username')):
        return 'invalid user', 400

    users.add_post(values.get('username'), values.get('caption'))

    response = {'message': f'Post successfuly created'}
    return jsonify(response), 201

@app.route("/getPost", methods = ["POST"])
def get_post():
    values = request.get_json()
    required = ['username']
    if not all(k in values for k in required):
        return 'Missing values', 400

    if not users.verifyUser(values.get('username')):
        return 'invalid user', 400

    response = {
        'posts': list(users.get_post(values.get('username')))
    }
    return jsonify(response), 201

@app.route("/getUsers", methods = ["GET"])
def get_users():
    response = {
        'Users': list(users.users)
    }
    return jsonify(response), 200

@app.route("/getCommunity", methods = ["POST"])
def getcommunity():
    values = request.get_json()
    required = ['username']
    if not all(k in values for k in required):
        return 'Missing values', 400
    if not users.verifyUser(values.get('username')):
        return 'invalid user', 400
    response={
        'Community': list(users.get_user_community(values.get('username')))
    }
    return jsonify(response), 201

@app.route("/addCommunity", methods = ["POST"])
def add_to_community():
    values = request.get_json()
    required = ['leader', 'follower']

    if not all(k in values for k in required):
        return 'Missing values', 400

    if not users.verifyUser(values.get('follower')):
        return 'invalid user', 400
    if not users.verifyUser(values.get('leader')):
        return 'invalid user', 400

    users.add_to_community(values.get('leader'), values.get('follower'))
    response = {'message': f'Successfuly added to community'}
    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)