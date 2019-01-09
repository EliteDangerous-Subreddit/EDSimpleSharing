import threading

import yaml

from RedditMonitor import RedditMonitor
from State import State


def main():
    config = yaml.safe_load(open("config.yml"))
    state = State(config)
    reddit_monitor = RedditMonitor(state)
    t = threading.Thread(target=reddit_monitor.check_new_submissions)
    t.start()
    reddit_monitor.check_wiki_updates()


if __name__ == '__main__':
    main()
