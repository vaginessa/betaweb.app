from  ..instaPrivate.instagram import insta
def verifyCaptcha(response):
    try:
        resp = insta.session.get(f"https://www.google.com/recaptcha/api/siteverify?secret=6LeKlDAgAAAAAPUAVbCR7w5_XQrmQJDWVGU3Rhyj&response={response}").json()
    except Exception as e:
        return False
    return resp.get("success")