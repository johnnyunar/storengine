from apscheduler.schedulers.background import BackgroundScheduler

from shop import gopay_api


def start():
    """
    The Order status updater calls the update_gopay_orders function every 5 minutes to keep the orders up-to-date.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(gopay_api.update_gopay_orders, 'interval', minutes=1)
    scheduler.start()
