import json, requests, pafy, sys, os
from flask import Flask, request, abort, redirect
from bs4 import BeautifulSoup, SoupStrainer
from data.InstagramAPI import InstagramAPI

app = Flask(__name__)
# instaAPI = InstagramAPI('jogedt', 'jogedjoged')
# marker = instaAPI.login()
# if marker == False:
#     instaAPI = InstagramAPI('bolinebot', 'bot321tob')
#     marker = instaAPI.login()
key = ['randi123', 'betakey']

@app.route('/coba', methods=['GET'])
def root():
    if marker == True:
        return str('it works !!!')
    else:
        return str('instagram is not logged in :(')

@app.route('/instainfo/<username>', methods=['GET'])
def instainfo(username):
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            result['error'] = None
            query = instaAPI.searchUsername(username)
            if query['status'] == 'ok':
                result['find'] = True
                result['result'] = {}
                query = query['user']
                result['result']['username'] = query['username']
                result['result']['mediacount'] = query['media_count']
                result['result']['following'] = query['following_count']
                result['result']['bio'] = query['biography']
                result['result']['name'] = query['full_name']
                result['result']['follower'] = query['follower_count']
                result['result']['private'] = query['is_private']
                result['result']['url'] = query['hd_profile_pic_url_info']['url']
            else:
                result['find'] = False
        return result
    except Exception as e:
        result['error'] = str(e)
        return result

@app.route('/instastory/<username>', methods=['GET'])
def instastory(username):
    result = {}
    try:
        keys = request.args.get('key')
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            result['error'] = None
            query = instaAPI.searchUsername(username)
            if query['status'] == 'ok':
                result['find'] = True
                userID = query['user']['pk']
                query = instaAPI.getStory(userID)
                data = query['items']
                if len(data) == 0:
                    result['url'] = []
                    if query['user']['is_private'] == True:
                        if 'friendship_status' in query['user']:
                            if query['user']['friendship_status']['following'] == True:
                                result['reason'] = 1
                        else:
                            result['reason'] = 2
                            instaAPI.follow(userID)
                    else:
                        result['reason'] = 1
                else:
                    result['url'] = []
                    for a in data:
                        items = {}
                        tipe = a['media_type']
                        items['tipe'] = tipe
                        if tipe == 1:
                            items['link'] = a['image_versions2']['candidates'][0]['url']
                        elif tipe == 2:
                            items['link'] = a['video_versions'][0]['url']
                            items['preview'] = a['image_versions2']['candidates'][1]['url']
                        result['url'].append(items)
            else:
                result['find'] = False
        return result
    except Exception as e:
        result['error'] = str(e)
        return result

@app.route('/instapost/<username>/<post_ke>')
def instapost(username, post_ke):
    result = {}
    try:
        keys = request.args.get('key')
        post_ke = int(post_ke)
        if keys not in key:
            result['error'] = 'need auth key'
        else:
            query = instaAPI.searchUsername(username)
            if query['status'] == 'ok':
                result['find'] = True
                userID = query['user']['pk']
                query = instaAPI.getUserFeed(userID)
                if query['status'] == 'ok':
                    result['see'] = True
                    if post_ke > len(query['items']):
                        user_feed = insta.getTotalUserFeed(userID, post_ke)
                    else:
                        user_feed = query['items']
                    mediacount = len(user_feed)
                    if post_ke <= mediacount:
                        result['banyak'] = True
                        post_ke = post_ke - 1
                        mediatype = user_feed[post_ke]['media_type']
                        result['media'] = {}
                        result['media']['mediatype'] = mediatype
                        result['media']['like_count'] = user_feed[post_ke]['like_count']
                        if 'comments_disabled' not in user_feed[post_ke]:
                            result['media']['comment_count'] = user_feed[post_ke]['comment_count']
                        else:
                            result['media']['comment_count'] = 'Disabled'
                        try:
                            result['media']['caption'] = user_feed[post_ke]['caption']['text']
                        except Exception as e:
                            result['media']['caption'] = ''
                        if mediatype == 1:
                            result['media']['url'] = user_feed[post_ke]['image_versions2']['candidates'][0]['url']
                        elif mediatype == 2:
                            result['media']['url'] = user_feed[post_ke]['video_versions'][1]['url']
                            result['media']['preview'] = user_feed[post_ke]['image_versions2']['candidates'][0]['url']
                        elif mediatype == 8:
                            result['media']['url'] = []
                            for a in user_feed[post_ke]['carousel_media']:
                                med = a['media_type']
                                items = {}
                                items['mediatype'] = med
                                if med == 1:
                                    items['url'] = a['image_versions2']['candidates'][0]['url']
                                elif med == 2:
                                    items['url'] = a['video_versions'][1]['url']
                                    items['preview'] =a['image_versions2']['candidates'][0]['url']
                                result['media']['url'].append(items)
                    else:
                        result['banyak'] = False
                else:
                    result['see'] = False
                    instaAPI.follow(userID)
            else:
                result['find'] = False
        return result
    except Exception as e:
        result['error'] = str(e)
        return result

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)