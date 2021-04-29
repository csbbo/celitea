from utils import filters as f


EmailCaptchaValidator = {
    'email': [f.email]
}

RegisterValidator = {
    'username': [],
    'password': [],
    'email': [f.email],
    'captcha': [],
}


LoginValidator = {
    'username': [],
    'password': []
}


ProfilePostValidator = {
    'username': [f.not_required],

    'email': [f.not_required, f.email],
    'phone': [f.not_required, f.phone],
    'remark': [f.not_required],
    'avatar': [f.not_required],

    'number': [f.not_required],
    'sex': [f.not_required],
    'wechat': [f.not_required],
    'qq': [f.not_required],
    'github': [f.not_required],
    'blog': [f.not_required],
    'birthday': [f.not_required],
    'grade': [f.not_required],
    'major': [f.not_required],
    'company': [f.not_required],
    'location': [f.not_required],
}
