import math

from graphviz import Graph

from models import Family, Person


def create_label(persons, person_id):
    person = persons[person_id]
    label = person.name
    if person.b_date and person.b_date != 'null':
        label += "\n*{}".format(person.b_date)
    if person.d_date or person.d_date == 'null':
        label += "\n+{}".format(person.d_date)
    return label

def edges_invisible(dot, points):
    for i in range(len(points) - 1):
        dot.edge(points[i], points[i + 1], style='invis')

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
                                        dot.edges([
                                            (kids_point, pre_point_s),
                                            (pre_point_s, pre_point_w),
                                            (pre_point_w, pre_point),
                                        ])
                                    else:
                                        dot.edges([
                                            (kids_point, pre_point),
                                            (pre_point, pre_point_w),
                                            (pre_point_w, pre_point_s),
                                        ])
                                else:
                                    dot.edges([
                                        (previous_pre, kids_point),
                                        (kids_point, pre_point),
                                    ])
                                previous_pre = None
                            else:
                                if kid.s_id:
                                    if kid.sex == 'M':
                                        dot.edges([
                                            (pre_point, pre_point_w),
                                            (pre_point_w, pre_point_s),
                                            (pre_point_s, kids_point)
                                        ])
                                    else:
                                        edges_invisible(dot, [pre_point_s, pre_point_w, pre_point])
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
                                        edges_invisible(dot, [pre_point_2, pre_point_w_2, pre_point_s_2])
                                    else:
                                        dot.edges([
                                            (kids_point, pre_point_s_2),
                                            (pre_point_s_2, pre_point_w_2),
                                            (pre_point_w_2, pre_point_2),
                                        ])
                                else:
                                    dot.edge(kids_point, pre_point_2)
                                break
                    if previous_pre:
                        if kid.s_id:
                            if kid.sex == 'M':
                                dot.edge(previous_pre, pre_point)
                                if counter == len(family.kids):
                                    edges_invisible(dot, [pre_point, pre_point_w, pre_point_s])
                                else:
                                    dot.edges([
                                        (pre_point, pre_point_w),
                                        (pre_point_w, pre_point_s),
                                    ])
                                pre_point = pre_point_s
                            else:
                                dot.edges([
                                    (previous_pre, pre_point_s),
                                    (pre_point_s, pre_point_w),
                                    (pre_point_w, pre_point)
                                ])
                        else:
                            dot.edge(previous_pre, pre_point)
                    else:
                        if kid.s_id:
                            if kid.sex == 'M':
                                if len(family.kids) == 1:
                                    edges_invisible(dot, [pre_point, pre_point_w, pre_point_s])
                                else:
                                    dot.edges([
                                        (pre_point, pre_point_w),
                                        (pre_point_w, pre_point_s)
                                    ])
                                pre_point = pre_point_s
                            else:
                                edges_invisible(dot, [pre_point_s, pre_point_w, pre_point])
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
    return dot.source
