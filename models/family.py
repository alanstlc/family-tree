class Family:
    def __init__(self, parents: list, kids: list):
        self.father = None
        self.mother = None
        for parent in parents:
            if parent.sex == 'M':
                self.father = parent
            else:
                self.mother = parent
        self.kids = kids
