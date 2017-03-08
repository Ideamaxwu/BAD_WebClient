#!/usr/bin/env python3

import tornado.ioloop
import tornado.httpclient
import tornado.gen
import simplejson as json
import brokerutils

log = brokerutils.setup_logging(__name__)

class AndroidClientNotifier():
    def __init__(self):
        self.gcmServer = 'https://fcm.googleapis.com/fcm/send'

        # Authorization key is associated with bigactivedata@gmail.com, registered through FCM Console
        self.gcmAuthorizationKey = 'AIzaSyB9OcjeeU0uwdqHtTh9XN-gTsvHL7v6v38'

        # Mobile clients send their tokens and they are stored here
        self.gcmRegistrationTokens = {}
        self.client = tornado.httpclient.AsyncHTTPClient()

    def setRegistrationToken(self, userId, registrationToken):
        log.info('Entering or Updating registration token of User %s' %userId)
        self.gcmRegistrationTokens[userId] = registrationToken

    @tornado.gen.coroutine
    def notify(self, userId, message):
        if userId not in self.gcmRegistrationTokens:
            log.error('User %s does not have an FCM token' %userId)
            return

        registration_token = self.gcmRegistrationTokens[userId]
        post_data = {
                     'registration_ids': [registration_token],
                     'notification': {
                         'title': 'New results',
                         'text': 'In channel %s' % message['channelName']
                     },
                     'priority': 'high',
                     'collapse_key': message['channelName'],
                     'data': message
                    }

        log.info(post_data)

        try:
            request = tornado.httpclient.HTTPRequest(self.gcmServer, method='POST',
                                                     headers={'Content-Type': 'application/json',
                                                              'Authorization': 'key=%s' %self.gcmAuthorizationKey},
                                                     body=json.dumps(post_data))
            response = yield self.client.fetch(request)

            result = json.loads(str(response.body, 'uft-8'))
            log.debug(result)
            if result['success'] == 1:
                log.info('FCM notification sent to %s' %userId)
            else:
                log.info('FCM notification sending failde to %s' %userId)

        except tornado.httpclient.HTTPError as e:
            log.error('FCM notification failed ' + str(e))

    def __del__(self):
        pass

@tornado.gen.coroutine
def test_notification():
    notifier = AndroidClientNotifier()
    notifier.gcmRegistrationTokens[1] = 'epYz7vfEmtA:APA91bFMQtyy5x3v69V7QQSHUpdSvMjgpQRtrvwq-oQwTCEhvZLdCGhbvKmLPuLwI5LG5XbQWEU7ca_GGH5RqKfJ9xx4To2zyKTWllkMoK-pGh65k_9k20byKFmHvWgkAaq2rFA_LLqm'
    yield notifier.notify(1, {'channelName': 'dummychannel', 'results': ['Hello']})

if  __name__ == '__main__':
    tornado.ioloop.IOLoop.current().add_callback(test_notification)
    tornado.ioloop.IOLoop.current().start()
