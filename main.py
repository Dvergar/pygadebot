import simplejson as json
import urllib2

from twisted.internet import reactor, protocol
from twisted.internet.task import LoopingCall
from twisted.words.protocols import irc

HOST, PORT = 'irc.freenode.net', 6667
url_search = 'http://search.twitter.com/search.json?' + \
            'q=python%20game%20-%22monty%20python%22'


def get_last_tweet():
    print "get_last_tweet"
    content = urllib2.urlopen(url_search).read()
    content_json = json.loads(content)
    results = content_json['results']

    for msg in results:
        text = msg['text']
        if text.find('http') != -1:
            return msg['id'], str(msg['text'])


class MyFirstIRCProtocol(irc.IRCClient):
    nickname = 'AlakoBot'
    last_id = None

    def send_tweet(self, msg):
        msg = "[Twitter]> " + msg
        self.say(self.factory.channel, msg)

    def check_twitter(self):
        _id, tweet_msg = get_last_tweet()
        if _id != None and _id != self.last_id:
            self.send_tweet(tweet_msg)
            self.last_id = _id

    def signedOn(self):
        self.join(self.factory.channel)
        lc = LoopingCall(self.check_twitter)
        lc.start(60)

    def privmsg(self, user, channel, message):
        print "user", user, "message", message
        command = message.split(' ')[0]
        _id, tweet_msg = get_last_tweet()
        if command == '!lasttweet':
            self.send_tweet(tweet_msg)


class MyFirstIRCFactory(protocol.ReconnectingClientFactory):
    protocol = MyFirstIRCProtocol
    channel = '##yourchannel'

if __name__ == '__main__':
    reactor.connectTCP(HOST, PORT, MyFirstIRCFactory())
    reactor.run()
