class Person:
    def __init__(self, id: (int, str), name: str, sex: str, b_date: str = None, d_date: str = None,
                 f_id: (int, str) = None, m_id: (int, str) = None, s_id: (int, str) = None):
        self.id = str(id)
        self.f_id = str(f_id) if f_id else None
        self.m_id = str(m_id) if m_id else None
        self.s_id = str(s_id) if s_id else None
        self.name = name
        self.sex = sex
        self.b_date = b_date
        self.d_date = d_date
