from random import randint
from threading import Thread
import main as user
from faker import Faker
import redis
import atexit
import time


class User(Thread):
    def __init__(self, connection, username, users_list, users_count):
        Thread.__init__(self)
        self.connection = connection
        self.users_list = users_list
        self.users_count = users_count
        user.register(conn, username)
        self.user_id = user.sign_in(conn, username)
        self.username = username

    def run(self):
        while True:
            message_text = fake.sentence(nb_words=10, variable_nb_words=True, ext_word_list=None)
            receiver = users[randint(0, users_count - 1)]
            user.create_message(self.connection, message_text, self.user_id, receiver)

            print(f'`{self.username}` sent message to `{receiver}`: `{message_text}`')
            time.sleep(1)


def exit_handler():
    redis_conn = redis.Redis(charset='utf-8', decode_responses=True)
    online = redis_conn.smembers('online:')
    redis_conn.srem('online:', list(online))
    print('EXIT')


if __name__ == '__main__':
    atexit.register(exit_handler)
    fake = Faker()
    users_count = int(input('Users count = '))
    users = [fake.profile(fields=['username'], sex=None)['username'] for u in range(users_count)]
    threads = []
    for x in range(users_count):
        conn = redis.Redis(charset='utf-8', decode_responses=True)

        print('User: ' + users[x])
        threads.append(User(
            redis.Redis(charset='utf-8', decode_responses=True),
            users[x], users, users_count))
    input('Press ENTER to start emulation...')
    for t in threads:
        t.start()
