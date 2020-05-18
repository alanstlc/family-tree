import json
import math
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
        # look for father and mother
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
    if person.b_date and person.b_date != 'null':
        label += "\n*{}".format(person.b_date)
    if person.d_date or person.d_date == 'null':
        label += "\n+{}".format(person.d_date)
    return label

def get_marriage_id(family):
    f_id = family.father.id
    m_id = family.mother.id
    if f_id and m_id:
        marriage_id = '{}+{}'.format(family.father.id, family.mother.id)
    elif f_id:
        marriage_id = f_id
    elif m_id:
        marriage_id = m_id
    return marriage_id

def create_family_graph(dot, family, persons):
    marriage_id = get_marriage_id(family)
    f_id = family.father.id
    m_id = family.mother.id
    if f_id and m_id:
        with dot.subgraph() as s:
            s.attr(rank='same')
            s.node(f_id, create_label(persons, family.father.id))
            s.node(marriage_id, shape='point', width='0', style='invis')
            s.node(m_id, create_label(persons, family.mother.id))
            s.edges([(f_id, marriage_id), (marriage_id, m_id)])
    elif f_id:
        dot.node(f_id, create_label(persons, family.father.id))
    elif m_id:
        dot.node(m_id, create_label(persons, family.mother.id))

def create_family_tree(persons, families):
    dot = Graph(edge_attr={'arrowhead': 'none'},
                graph_attr={'splines':'ortho' #'rankdir': 'LR',
                            }, node_attr={'shape': 'box'})

    # create kids
    for family_id in families:
        family = families[family_id]
        marriage_id = get_marriage_id(family)
        if family.kids:
            kids_point = ''
            for kid in family.kids:
                #dot.node(kid.id, create_label(persons, kid.id))
                kids_point += kid.id + '_'

            with dot.subgraph() as s:
                s.attr(rank='same')
                counter = 0
                previous_pre_kid = None
                for kid in family.kids:
                    counter += 1
                    prekid_point = "pre_kid_" + kid.id
                    if len(family.kids) % 2 == 1:
                        if counter == math.ceil(len(family.kids) / 2):
                            kids_point = prekid_point
                        s.node(prekid_point, shape='point', width='0', style='invis')
                    if len(family.kids) % 2 == 0:
                        s.node(prekid_point, shape='point', width='0', style='invis')
                        if counter == len(family.kids) / 2:
                            if len(family.kids) > 2:
                                s.node(kids_point, shape='point', width='0', style='invis')
                                dot.edge(previous_pre_kid, kids_point)
                                dot.edge(kids_point, prekid_point)
                                previous_pre_kid = None
                            else:
                                s.node(kids_point, shape='point', width='0', style='invis')
                                dot.edge(prekid_point, kids_point)
                                prekid_point_2 = "pre_kid_" + family.kids[1].id
                                s.node(prekid_point_2, shape='point', width='0', style='invis')
                                dot.edge(kids_point, prekid_point_2)
                                break
                    if previous_pre_kid:
                        dot.edge(previous_pre_kid, prekid_point)
                    previous_pre_kid = prekid_point

            for kid in family.kids:
                prekid_point = "pre_kid_" + kid.id
                if kid.s_id:
                    dot.node(kid.id, create_label(persons, kid.id))
                else:
                    dot.node(kid.id, create_label(persons, kid.id))
                dot.edge(prekid_point, kid.id)

    for family_id in families:
        family = families[family_id]
        marriage_id = get_marriage_id(family)
        if family.kids:
            kids_point = ''
            for kid in family.kids:
                kids_point += kid.id + '_'
            if len(family.kids) > 1 and len(family.kids) % 2 == 1:
                kids_point = "pre_kid_" +  family.kids[math.ceil(len(family.kids)/2)-1].id
            dot.edge(marriage_id, kids_point)

    # create parents and marriages
    for family_id in families:
        family = families[family_id]
        create_family_graph(dot, family, persons)

    dot.render('output.png')
    #print(dot.source)
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
            persons[str(record['id'])] = Person(**record)
        except TypeError as e:
            return False, str(e)

    families = create_families(persons)
    if families:
        return True, create_family_tree(persons, families)
    return False, "No families data inserted!"

if __name__ == '__main__':
    run()
