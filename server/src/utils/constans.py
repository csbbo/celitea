class Choices:
    @classmethod
    def choices(cls, *, exclude_field=()):
        d = cls.__dict__
        ret = {str(d[item]) for item in d.keys() if not item.startswith("_")}
        return list(ret - set(exclude_field))


class UserTypeEnum(Choices):
    super_admin = 3
    admin = 2
    number = 1
    guest = 0


class MajorEnum(Choices):
    computer_science_and_technology = '计算机科学与技术'
    internet_of_things = '物联网'
    software_engineering = '软件工程'
    network_engineering = '网络工程'
