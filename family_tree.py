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

def get_marriage_id(fam_or_not, families=None):
    if type(fam_or_not) is Family:
        f_id = fam_or_not.father.id if fam_or_not.father else None
        m_id = fam_or_not.mother.id if fam_or_not.mother else None
        if f_id and m_id:
            marriage_id = '{}+{}'.format(fam_or_not.father.id, fam_or_not.mother.id)
        elif f_id:
            marriage_id = f_id
        elif m_id:
            marriage_id = m_id
        return marriage_id
    elif type(fam_or_not) is Person:
        for family in families:
            family = families[family]
            if family.father == fam_or_not or family.mother == fam_or_not:
                return get_marriage_id(family)
    return None

def has_ancestors(family):
    father = family.father
    mother = family.mother
    if father:
        if father.f_id or father.m_id:
            return True
    if mother:
        if mother.f_id or mother.m_id:
            return True
    return False

def create_family_graph(dot, family, persons):
    marriage_id = get_marriage_id(family)
    f_id = family.father.id if family.father else None
    m_id = family.mother.id if family.mother else None
    if f_id and m_id:
        with dot.subgraph(name=marriage_id) as s:
            s.attr(rank='same')
            s.node(f_id, create_label(persons, family.father.id))
            s.node(m_id, create_label(persons, family.mother.id))
            s.node(marriage_id, shape='point', width='0', style='invis')
            s.edges([(f_id, marriage_id), (marriage_id, m_id)])
    elif f_id:
        dot.node(f_id, create_label(persons, family.father.id))
    elif m_id:
        dot.node(m_id, create_label(persons, family.mother.id))

def create_family_tree(persons, families):
    dot = Graph(edge_attr={'arrowhead': 'none'},
                graph_attr={'splines':'ortho',
                            }, node_attr={'shape': 'box'})

    # create origins parents and marriages
    for family_id in families:
        family = families[family_id]
        if not has_ancestors(family):
            create_family_graph(dot, family, persons)

    # create kids
    for family_id in families:
        family = families[family_id]
        if family.kids:
            kids_point = ''
            for kid in family.kids:
                kids_point += kid.id + '_'

            with dot.subgraph(name=kids_point) as s:
                s.attr(rank='same')
                counter = 0
                previous_pre = None
                for kid in family.kids:
                    counter += 1
                    pre_point = "pre_" + kid.id
                    pre_point_s = ""
                    s.node(pre_point, shape='point', width='0', style='invis')
                    if kid.s_id:
                        pre_point_s = "pre_" + kid.s_id
                        pre_point_w = "pre_" + get_marriage_id(kid, families)
                        s.node(pre_point_s, shape='point', width='0', style='invis')
                        s.node(pre_point_w, shape='point', width='0', style='invis')
                    if len(family.kids) % 2 == 0:
                        if counter == len(family.kids) / 2:
                            s.node(kids_point, shape='point', width='0', style='invis')
                            if len(family.kids) > 2:
                                if kid.s_id:
                                    dot.edge(previous_pre, kids_point)
                                    if kid.sex == 'M':
                                        dot.edge(kids_point, pre_point_s)
                                        dot.edge(pre_point_s, pre_point_w)
                                        dot.edge(pre_point_w, pre_point)
                                    else:
                                        dot.edge(kids_point, pre_point)
                                        dot.edge(pre_point, pre_point_w)
                                        dot.edge(pre_point_w, pre_point_s)
                                else:
                                    dot.edge(previous_pre, kids_point)
                                    dot.edge(kids_point, pre_point)
                                previous_pre = None
                            else:
                                if kid.s_id:
                                    if kid.sex == 'M':
                                        dot.edge(pre_point, pre_point_w)
                                        dot.edge(pre_point_w, pre_point_s)
                                        dot.edge(pre_point_s, kids_point)
                                    else:
                                        dot.edge(pre_point_s, pre_point_w, style='invis')
                                        dot.edge(pre_point_w, pre_point, style='invis')
                                        dot.edge(pre_point, kids_point)
                                else:
                                    dot.edge(pre_point, kids_point)
                                kid_2 = family.kids[1]
                                pre_point_2 = "pre_" + kid_2.id
                                s.node(pre_point_2, shape='point', width='0', style='invis')
                                if kid_2.s_id:
                                    pre_point_s_2 = "pre_" + kid_2.s_id
                                    pre_point_w_2 = "pre_" + get_marriage_id(kid_2, families)
                                    s.node(pre_point_s_2, shape='point', width='0', style='invis')
                                    s.node(pre_point_w_2, shape='point', width='0', style='invis')
                                    if kid_2.sex == 'M':
                                        dot.edge(kids_point, pre_point_2)
                                        dot.edge(pre_point_2, pre_point_w_2, style='invis')
                                        dot.edge(pre_point_w_2, pre_point_s_2, style='invis')
                                    else:
                                        dot.edge(kids_point, pre_point_s_2)
                                        dot.edge(pre_point_s_2, pre_point_w_2)
                                        dot.edge(pre_point_w_2, pre_point_2)
                                else:
                                    dot.edge(kids_point, pre_point_2)
                                break
                    if previous_pre:
                        if kid.s_id:
                            if kid.sex == 'M':
                                dot.edge(previous_pre, pre_point)
                                if counter == len(family.kids):
                                    dot.edge(pre_point, pre_point_w, style='invis')
                                    dot.edge(pre_point_w, pre_point_s, style='invis')
                                else:
                                    dot.edge(pre_point, pre_point_w)
                                    dot.edge(pre_point_w, pre_point_s)
                                pre_point = pre_point_s
                            else:
                                dot.edge(previous_pre, pre_point_s)
                                dot.edge(pre_point_s, pre_point_w)
                                dot.edge(pre_point_w, pre_point)
                        else:
                            dot.edge(previous_pre, pre_point)
                    else:
                        if kid.s_id:
                            if kid.sex == 'M':
                                dot.edge(pre_point, pre_point_w)
                                dot.edge(pre_point_w, pre_point_s)
                                pre_point = pre_point_s
                            else:
                                dot.edge(pre_point_s, pre_point_w, style='invis')
                                dot.edge(pre_point_w, pre_point, style='invis')
                    previous_pre = pre_point

    # create marriages and kids points connection
    for family_id in families:
        family = families[family_id]
        marriage_id = get_marriage_id(family)
        if family.kids:
            kids_point = ''
            for kid in family.kids:
                kids_point += kid.id + '_'
            if len(family.kids) % 2 == 1:
                kids_point = "pre_" +  family.kids[math.ceil(len(family.kids)/2)-1].id
            dot.edge(marriage_id, kids_point)

    # create kids and kids points connection
    for family_id in families:
        family = families[family_id]
        if family.kids:
            with dot.subgraph() as s:
                s.attr(rank='same')
                for kid in family.kids:
                    counter += 1
                    pre_point = "pre_" + kid.id
                    s.node(kid.id, create_label(persons, kid.id))
                    dot.edge(pre_point, kid.id)
                    if kid.s_id:
                        marriage_id = get_marriage_id(kid, families)
                        pre_point_s = "pre_" + kid.s_id
                        pre_point_w = "pre_" + marriage_id
                        s.node(kid.s_id, create_label(persons, kid.s_id))
                        s.node(marriage_id, shape='point', width='0', style='invis')
                        dot.edge(pre_point_s, kid.s_id, style='invis')
                        dot.edge(pre_point_w, marriage_id, style='invis')
                        if kid.sex == 'M':
                            dot.edges([(kid.id, marriage_id), (marriage_id, kid.s_id)])
                        else:
                            dot.edges([(kid.s_id, marriage_id), (marriage_id, kid.id)])

    dot.render('output.png')
    print(dot.source)
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
