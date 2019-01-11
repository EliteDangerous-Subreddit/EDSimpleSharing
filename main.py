import threading
import time

import schedule
import yaml

from reddit_monitor import RedditMonitor
from state import State


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main():
    config = yaml.safe_load(open("config.yml"))
    state = State(config)
    reddit_monitor = RedditMonitor(state)

    reddit_monitor.check_wiki_updates()

    schedule.every(5).minutes.do(run_threaded, reddit_monitor.check_wiki_updates)
    run_threaded(reddit_monitor.check_new_submissions)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
