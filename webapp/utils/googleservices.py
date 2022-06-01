from ..instaPrivate.instagram import insta
import requests


def verifyCaptcha(response):
    try:
        resp = insta.session.get(
            f"https://www.google.com/recaptcha/api/siteverify?secret=6LeKlDAgAAAAAPUAVbCR7w5_XQrmQJDWVGU3Rhyj&response={response}")
        if resp.status_code != 200:
            return False
    except Exception as e:
        return False
    return resp.json().get("success")
