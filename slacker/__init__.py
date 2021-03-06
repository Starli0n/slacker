# Copyright 2014 Oktay Sancak
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import requests


API_BASE_URL = 'https://slack.com/api/{method}?token={token}'


__all__ = ['Slacker', 'Error']


class Error(Exception):
    pass


class Response(object):
    def __init__(self, body):
        self.raw = body
        self.body = json.loads(body)
        self.successful = self.body['ok']
        self.error = self.body.get('error')


class API(object):
    def __init__(self, token):
        self.token = token

    def _request(self, method, **kwargs):
        response = requests.get(API_BASE_URL.format(method=method, token=self.token),
                                params=kwargs)
        assert response.status_code == 200
        response = Response(response.text)

        if not response.successful:
            raise Error(response.error)

        return response


class Auth(API):
    def test(self):
        return self._request('auth.test')


class Users(API):
    def list(self):
        return self._request('users.list')


class Groups(API):
    def list(self, exclude_archived=None):
        return self._request('groups.list', exclude_archived=exclude_archived)

    def history(self, channel,
                latest=None, oldest=None, count=None):
        return self._request('groups.history',
                             channel=channel,
                             latest=latest,
                             oldest=oldest,
                             count=count)


class Channels(API):
    def list(self, exclude_archived=None):
        return self._request('channels.list',
                             exclude_archived=exclude_archived)

    def history(self, channel,
                latest=None, oldest=None, count=None):
        return self._request('channels.history',
                             channel=channel,
                             latest=latest,
                             oldest=oldest,
                             count=count)

    def mark(self, channel, ts):
        return self._request('channels.mark',
                             channel=channel,
                             ts=ts)


class Chat(API):
    def post_message(self, channel, text,
                     username=None, parse=None, link_names=None,
                     attachments=None, unfurl_links=None, icon_url=None,
                     icon_emoji=None):
        return self._request('chat.postMessage',
                             channel=channel,
                             text=text,
                             username=username,
                             parse=parse,
                             link_names=link_names,
                             attachments=attachments,
                             unfurl_links=unfurl_links,
                             icon_url=icon_url,
                             icon_emoji=icon_emoji)


class IM(API):
    def list(self):
        return self._request('im.list')

    def history(self, channel,
                latest=None, oldest=None, count=None):
        return self._request('im.history',
                             channel=channel,
                             latest=latest,
                             oldest=oldest,
                             count=count)


class Search(API):
    def all(self, query,
            sort=None, sort_dir=None, highlight=None, count=None, page=None):
        return self._request('search.all',
                             query=query,
                             sort=sort,
                             sort_dir=sort_dir,
                             highlight=highlight,
                             count=count,
                             page=page)

    def files(self, query,
              sort=None, sort_dir=None, highlight=None, count=None, page=None):
        return self._request('search.files',
                             query=query,
                             sort=sort,
                             sort_dir=sort_dir,
                             highlight=highlight,
                             count=count,
                             page=page)

    def messages(self, query,
                 sort=None, sort_dir=None, highlight=None, count=None,
                 page=None):
        return self._request('search.messages',
                             query=query,
                             sort=sort,
                             sort_dir=sort_dir,
                             highlight=highlight,
                             count=count,
                             page=page)


class Files(API):
    def list(self, user=None, ts_from=None, ts_to=None, types=None, count=None,
             page=None):
        return self._request('files.list',
                             user=user,
                             ts_from=ts_from,
                             ts_to=ts_to,
                             types=types,
                             count=count,
                             page=page)

    def upload(self, file,
               filetype=None, filename=None, title=None, initial_comment=None,
               channels=None):
        with open(file, 'rb') as f:
            if isinstance(channels, (tuple, list)):
                channels = ','.join(channels)

            response = requests.post(API_BASE_URL.format(method='files.upload',
                                                         token=self.token),
                                     params={
                                        'filetype': filetype,
                                        'filename': filename,
                                        'title': title,
                                        'initial_comment': initial_comment,
                                        'channels': channels
                                     },
                                     files={'file': f})
            assert response.status_code == 200
            response = Response(response.text)

            if not response.successful:
                raise Error(response.error)

            return response


class Stars(API):
    def list(self, user=None, count=None, page=None):
        return self._request('stars.list',
                             user=user,
                             count=count,
                             page=page)


class Slacker(object):
    def __init__(self, token):
        self.auth = Auth(token)
        self.users = Users(token)
        self.groups = Groups(token)
        self.channels = Channels(token)
        self.chat = Chat(token)
        self.im = IM(token)
        self.files = Files(token)
        self.stars = Stars(token)
