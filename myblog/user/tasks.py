from django.conf import settings
from myblog.celery import app
from tools.sms import YunTongXin


@app.task
def send_sms_celery(phone, code):
    obj = YunTongXin(
        settings.ACCOUNT_SID,
        settings.ACCOUNT_TOKEN,
        settings.APP_ID,
        settings.TEMPLATE_ID
    )
    res = obj.run(phone, code)
    return res