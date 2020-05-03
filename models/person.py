class Person:
    def __init__(self, id: int, name: str, sex: str, birth_date: str, death_date: str = None,
                 f_id: int = None, m_id: int = None, s_id: int = None):
        self.id = id
        self.f_id = f_id
        self.m_id = m_id
        self.s_id = s_id
        self.name = name
        self.sex = sex
        self.birth_date = birth_date
        self.death_date = death_date
