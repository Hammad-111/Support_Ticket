from app.celery_app.celery import celery_app

LOG_FILE = "reply_logs.log"


@celery_app.task
def log_reply(ticket_id: int, message: str):
    line = f"ticket={ticket_id} | reply={message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    return line


@celery_app.task
def send_email(ticket_id: int, message: str):
    line = f"EMAIL ticket={ticket_id} | New reply: {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    return line
