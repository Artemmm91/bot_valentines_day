class Gender:
    def __init__(self, gender):
        self.__gender = gender

    ANY = 0
    MALE = 1
    FEMALE = 2

    def __repr__(self):
        if self.__gender == Gender.MALE:
            return "M"
        elif self.__gender == Gender.FEMALE:
            return "F"
        else:
            return "A"

    def __eq__(self, other):
        return self.__gender == other.__gender


MALE = Gender(Gender.MALE)
FEMALE = Gender(Gender.FEMALE)
ANY = Gender(Gender.ANY)


def get(gender_str):
    if gender_str == 'Мужской':
        return MALE
    elif gender_str == 'Женский':
        return FEMALE
    else:
        return ANY


def __is_can_be_a_partner(my_gender, my_partner_gender, other_gender, other_partner_gender):
    if (other_partner_gender == my_gender or other_partner_gender == ANY) and \
            (my_partner_gender == other_gender or my_partner_gender == ANY):
        return True
    return False


def is_can_be_a_partner(me, other):
    return __is_can_be_a_partner(me.gender, me.partner_gender, other.gender, other.partner_gender)
