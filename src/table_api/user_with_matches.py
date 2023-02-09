class UserWithMatches:
    class UserInMatch:
        def __init__(self, name, vk_link, matches_count):
            self.name = name
            self.vk_link = vk_link
            self.matches_count = int(matches_count)

    def __init__(self, name, vk_link, matches):
        self.name = name
        self.vk_link = vk_link
        self.vk_id = None
        self.matches = []
        for match in matches:
            self.matches.append(UserWithMatches.UserInMatch(match[1], match[2], match[4]))

    def get_message(self):
        message = f"Привет, {self.name}!\n" \
                  f"По результатам анкеты 14 февраля у тебя...\n"
        for match in self.matches:
            if match.matches_count >= 20:
                message += "Идеальный мэтч"
            elif match.matches_count >= 18:
                message += "Почти идеальное совпадение"
            elif match.matches_count >= 16:
                message += "Хорошее совпадение"
            else:
                message += "Неплохое совпадение"

            message += f" c {match.name} (vk: {match.vk_link})\n"

        message += "\nСпасибо за участие в онлайн-этапе! Счастливого дня святого Валентина!!!\n"
        return message
