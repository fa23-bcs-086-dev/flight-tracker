import threading
import time


def _worker(db):
    # placeholder background worker loop (e.g., price scraping, cleanup)
    while True:
        try:
            # implement scheduled jobs here using `db`
            time.sleep(60)
        except Exception:
            time.sleep(60)


def run_scheduler(db):
    """
    Start background scheduler as a daemon thread and return the Thread.
    """
    t = threading.Thread(target=_worker, args=(db,), daemon=True)
    t.start()
    return t