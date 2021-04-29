from utils.i18n import en_US, zh_CN


def i18n(accept_language):
    dic = {
        'en-US': en_US,
        'zh-CN': zh_CN,
    }
    lang = str(accept_language).split(',')[0]
    if lang not in dic.keys():
        return zh_CN
    return dic[lang]
