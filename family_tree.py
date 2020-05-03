import json
import re

from graphviz import Graph

from models import Family, Person

def add_new_family_record(families, family_id, parents, kid):
    if family_id in families:
        if kid:
            families[family_id].kids.append(kid)
    else:
        families[family_id] = Family(parents, [kid]) if kid else Family(parents, [])

def create_families(persons):
    families = {}
    for person_id in persons:
        person = persons[person_id]
        # look for rather and mother
        if person.f_id or person.m_id:
            if person.f_id and person.m_id:
                family_id = '{}-{}'.format(person.f_id, person.m_id)
                add_new_family_record(families, family_id, [persons[person.f_id], persons[person.m_id]], person)
            else:
                if person.f_id:
                    family_id = person.f_id
                    add_new_family_record(families, family_id, [persons[person.f_id]], person)
                elif person.m_id:
                    family_id = person.m_id
                    add_new_family_record(families, family_id, [persons[person.m_id]], person)
        # look for spouse
        s_id = person.s_id
        if s_id and s_id in persons:
            if person.sex == 'M':
                family_id = '{}-{}'.format(person.id, person.s_id)
            else:
                family_id = '{}-{}'.format(person.s_id, person.id)
            add_new_family_record(families, family_id, [person, persons[person.s_id]], None)
    return families

def create_label(persons, person_id):
    person = persons[person_id]
    label = person.name
    if person.birth_date and person.birth_date != 'null':
        label += "\n*{}".format(person.birth_date)
    if person.death_date or person.death_date == 'null':
        label += "\n+{}".format(person.death_date)
    return label

def create_family_tree(persons, families):
    dot = Graph(comment='Family tree', edge_attr={'arrowhead': 'none'},
                graph_attr={'splines': 'ortho', 'overlap': 'scalexy', 'concentrate': 'true', #'rankdir': 'LR',
                            }, node_attr={'shape': 'box'})

    for family_id in families:
        family = families[family_id]

        f_id = str(family.father.id) if hasattr(family, 'father') else None
        m_id = str(family.mother.id) if hasattr(family, 'mother') else None

        if f_id:
            dot.node(f_id, create_label(persons, family.father.id))
            marriage_id = f_id
        if m_id:
            dot.node(m_id, create_label(persons, family.mother.id))
            marriage_id = m_id
        if f_id and m_id:
            marriage_id = '{}+{}'.format(family.father.id, family.mother.id)
            dot.node(marriage_id, shape='point', width='0.01', height='0.01')

            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f_id)
                s.node(m_id)
                s.node(marriage_id)

            dot.edge(f_id, marriage_id)
            dot.edge(marriage_id, m_id)

        if family.kids:
            kids_point = ''
            for kid in family.kids:
                dot.node(str(kid.id), create_label(persons, kid.id))
                kids_point += str(kid.id) + '_'

            if len(family.kids) == 1:
                kids_point = marriage_id
            else:
                dot.node(kids_point, shape='point', width='0.01', height='0.01')
                dot.edge(marriage_id, kids_point)

            with dot.subgraph() as s:
                s.attr(rank='same')
                for kid in family.kids:
                    #prekid_point = "pre_kid_" + str(kid.id)
                    #dot.node(prekid_point, shape='point', width='0.01', height='0.01')
                    #dot.edge(kids_point, prekid_point)
                    dot.edge(kids_point, str(kid.id))
                    s.node(str(kid.id))

    dot.render('output.png')
    return dot.source

def run(input):
    persons = dict()
    records = []

    #with open('input.json') as f:
    #   records = json.load(f)

    try:
        records = json.loads(input)
    except json.decoder.JSONDecodeError as e:
        if str(e).startswith('Expecting value: line') or (
                str(e).startswith('Expecting property name enclosed in double quotes')):
            line = re.search('(\d+)(?!.*\d)', str(e))
            issue_position = int(line.group())
            if 20 < issue_position < len(str(input)) + 20:
                return False, 'Issue with input data somewhere here: >{}<'.format(input[issue_position-20:issue_position+20])
        return False, str(e)

    for record in records:
        try:
            persons[record['id']] = Person(**record)
        except TypeError as e:
            return False, str(e)

    families = create_families(persons)
    if families:
        return True, create_family_tree(persons, families)
    return False, "No families data inserted!"

if __name__ == '__main__':
    run()
