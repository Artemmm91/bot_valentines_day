import urllib.parse

from config.system_config import LINK_TO_FORM, FORM_FIELD_NAME_TO_ID


def create_form_link(user_info):
    info = []
    if "first_name" in user_info and "last_name" in user_info:
        info.append(["name", f"{user_info['first_name']} {user_info['last_name']}"])
    if "screen_name" in user_info:
        info.append(["vk_page_link", f"vk.com/{user_info['screen_name']}"])
    if "sex" in user_info:
        if user_info["sex"] > 0:
            info.append(["sex", "Мужской" if user_info["sex"] == 2 else "Женский"])
            info.append(["sex_of_partner", "Женский" if user_info["sex"] == 2 else "Мужской"])
    return LINK_TO_FORM + "?" + "&".join(
        ["entry." + str(FORM_FIELD_NAME_TO_ID[i[0]]) + "=" + urllib.parse.quote(i[1]) for i in info])
