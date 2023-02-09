import re

ID_NAME_REGEX = re.compile(r"^\[([^|]+)|\S+]$")
LINK_NAME_REGEX = re.compile(r"vk\.com\/([a-zA-Z0-9._]+)")


def parse_name_message(message):
    id_name_search = ID_NAME_REGEX.search(message)
    if id_name_search:
        return id_name_search.group(1)

    link_name_search = LINK_NAME_REGEX.search(message)
    if link_name_search:
        return link_name_search.group(1)

    return None


def parse_name_from_link(link):
    link_name_search = LINK_NAME_REGEX.search(link)
    if link_name_search:
        return link_name_search.group(1)
    return None
