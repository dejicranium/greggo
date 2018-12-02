from celery import Celery

app = Celery('repoll', 
            broker='pyamqp://guest@localhost//',
            include=['repoll.tasks'])


if __name__ == "__main__":
    app.start()