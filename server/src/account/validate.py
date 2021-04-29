from utils import filters as f


register_validator = {
    'username': [f.required, f.not_empty],
    'password': [f.required, f.not_empty]
}


login_validator = {
    'username': [f.required, f.not_empty],
    'password': [f.required, f.not_empty]
}


user_get_validator = {
    'tags': [f.required],
    'name': [f.required]
}


user_get_validator = {
    'username': [f.required, f.not_empty],
    'password': [f.required, f.not_empty]
}