import json
import re

from models import Family, Person

from family_tree_builder import create_family_tree


def add_new_family_record(families, family_id, parents, kid):
    if family_id in families:
        if kid:
            families[family_id].kids.append(kid)
    else:
        families[family_id] = Family(parents, [kid]) if kid else Family(parents, [])

def filter_non_existing_people(persons):
    # filter non-existing people
    for person in persons.values():
        if person.m_id is not None and person.m_id not in persons:
            person.m_id = None
        if person.f_id is not None and person.f_id not in persons:
            person.f_id = None
        if person.s_id is not None and person.s_id not in persons:
            person.s_id = None

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
                return False, 'Issue with input data somewhere here: >>>{}<<<'.format(
                    input[issue_position-20:issue_position+20])
        return False, str(e)

    for record in records:
        try:
            persons[str(record['id'])] = Person(**record)
        except TypeError as e:
            return False, str(e)

    filter_non_existing_people(persons)
    families = create_families(persons)
    if families:
        return True, create_family_tree(persons, families)
    return False, "No families data inserted!"

if __name__ == '__main__':
    run()
