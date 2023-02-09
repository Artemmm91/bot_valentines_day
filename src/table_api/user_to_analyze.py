class UserToAnalyze:
    def __init__(self, name, vk_link, gender, partner_gender, answers, detailed_answer, user_id):
        self.name = name
        self.vk_link = vk_link
        self.gender = gender
        self.partner_gender = partner_gender
        self.answers = answers
        self.detailed_answer = detailed_answer
        self.id = user_id

    def __repr__(self):
        return f"{self.id}) {self.name} (vk {self.vk_link}) ({self.gender} {self.partner_gender}): {self.answers} \"{self.detailed_answer}\""

    def count_match(self, other):
        count = 0
        for i, j in zip(self.answers, other.answers):
            if i == j:
                count += 1
        return count
