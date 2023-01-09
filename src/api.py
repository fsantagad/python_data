import json
import math
from model.person import Person, PersonSchema, Country, CountrySchema, PersonsPerCountrySchema, PersonsPerGenderSchema, db
from flask import Flask, jsonify, request
import logging

def get(id=None, page=None, per_page=None):
    """
    get Person
    """
    # set default parameters
    if page is None:
        page = 1
    if per_page is None:
        per_page = 10

    try:
        # get all persons
        if id is None:
            person = Person.query.paginate(page=page, per_page=per_page)
            person_schema =  PersonSchema(many=True)
            person_json = person_schema.jsonify(person).json
            result = {}
            result['data'] = person_json
            result['page'] = page
            result['per_page'] = per_page
            result['total_pages'] = math.ceil(Person.query.count() / per_page)
            return result, 200
        else:
            person = Person.query.filter_by(id=id).first()
            person_schema = PersonSchema()
            return person_schema.jsonify(person), 200
    except Exception as e:
        logging.error("error api: " + str(e))
        return jsonify({"error":"There was an error please contact the administrator"}), 400
        

def post():
    
    """
    Add Person
    """
    data = request.get_json()
    try:
        new_country = Country(**data['country'])
        del data['country']
        new_person = Person(**data)
        person_schema = PersonSchema()
        db.session.add(new_person)
        db.session.add(new_country)
        db.session.commit()
        return person_schema.jsonify(new_person), 201
    except Exception as e:
        logging.error("error api: " + str(e))
        if 'Duplicate entry' in str(e):
            return jsonify({"error":"Person already exists"}), 409
        return jsonify({"error":"There was an error please contact the administrator"}), 400        


def put(id):
    """
    Update person
    """
    try:
            
        data = request.get_json()
        person = Person.query.filter_by(id=id).first()
        person = Person.query.filter_by(id=id)
        person.update(data)
        db.session.commit()
                
        return jsonify(data), 200
    except Exception as e:
        logging.error("error api: " + str(e))
        return jsonify({"error":"There was an error please contact the administrator"}), 400

def get_persons_by_country(country):
    """
    Get Persons by Country
    """
    try:
        countries = Country.query.filter_by(country=country).all()
        persons_ids = [country.person_id for country in countries]
        persons = Person.query.filter(Person.id.in_(persons_ids)).all()
        persons_schema =  PersonSchema(many=True)
        return persons_schema.jsonify(persons), 200
    except Exception as e:
        logging.error("error api: " + str(e))
        return jsonify({"error":"There was an error please contact the administrator"}), 400

def count_persons_by_country():
    """
    Count Persons by Country
    """
    try:
        persons = db.func.count(Country.country).label("persons")
        q = db.session.query(
            persons,
            Country.country
        ).group_by(
            Country.country
        ).having(
            persons > 0
        ).order_by(
            persons.desc()
        )
        #print(q)

        person_country_schema =  PersonsPerCountrySchema(many=True)
        return person_country_schema.jsonify(q.all()), 200
    except Exception as e:
        logging.error("error api: " + str(e))
        return jsonify({"error":"There was an error please contact the administrator"}), 400

def convert_anything_to_int(s, default=0):
    ''' Convert any string `s` to an `int` value, return the value.

        This function returns `int(s)` into its integer value
        unless that raises a `ValueError`
        in which case it returns default.
    '''
    if not s:
        i = default
    try:
        i = int(s)
    except ValueError as e:
        warning("convert_anything_to_int: converting invalid value %r into default", s)
        i = default
    return i

def count_persons_by_gender(page=None, per_page=None):
    """
    Count and give Persons by gender
    """
    # set default parameters
    if page is None:
        page = 1
    if per_page is None:
        per_page = 10
    
    # query
    try:
        persons = db.func.count(Person.gender).label("persons")
        q = db.session.query(
            persons,
            Person.gender
        ).group_by(
            Person.gender
        ).having(
            persons > 0
        ).order_by(
            persons.desc()
        )
        #print(q)
        all_genders = q.all()
        persons_gender = [gender.gender for gender in all_genders]
        person_gender_schema =  PersonsPerGenderSchema(many=True)
        all_genders_json = person_gender_schema.jsonify(all_genders).json
        for index, gender in enumerate(persons_gender):
            qgender = db.session.query(Person).group_by(
                Person.gender,
                Person.id
            ).having(
                Person.gender==gender
            )
            #print(qgender)
            if all_genders_json[index]['gender'] == gender:
                persons_schema =  PersonSchema(many=True)
                all_genders_json[index]['count'] = all_genders_json[index]['persons']
                total_pages = math.ceil( int(all_genders_json[index]['persons']) / per_page ) 
                if page > 0 and page <= total_pages:
                    all_genders_json[index]['page'] = page
                else:
                    if page < 1:
                        page = 1  
                    else:
                        page = total_pages
                    all_genders_json[index]['page'] = page
                all_genders_json[index]['per_page'] = per_page
                all_genders_json[index]['total_pages'] = total_pages
                all_genders_json[index]['persons'] = persons_schema.jsonify(qgender.paginate(page=page, per_page=per_page).items).json

        return all_genders_json, 200
    except Exception as e:
        logging.error("error api: " + str(e))
        return jsonify({"error":"There was an error please contact the administrator"}), 400

def elaborate_ipclass_query(from_ip, to_ip, page, per_page, label):
    """
    Receive a range of IP addresses and page numbers
    """
    inet_a = db.func.inet_aton(Person.ip_address).between(db.func.inet_aton(from_ip), db.func.inet_aton(to_ip))
    q_a = db.session.query(
        Person
    ).filter(
        inet_a
    )
    #print(q_a)
    persons_schema =  PersonSchema(many=True)
    count = q_a.count()
    total_pages = math.ceil( count / per_page)
    result_json = {}
    result_json['class'] = label
    result_json['count'] = count
    result_json['persons'] = persons_schema.jsonify(q_a.paginate(page=page, per_page=per_page).items).json
    result_json['page'] = page
    result_json['per_page'] = per_page
    result_json['total_pages'] = total_pages
    return result_json

def ip_by_class(page=None, per_page=None):
    """
    Group Ip Persons by class 

    Class A 0-127.H.H.H;
    Class B 128-191.N.H.H;
    Class C 192-223.N.N.H;
    Class D 224-239.x.x.x;
    Class E 240-255.x.x.x;
    """

    # convert numeric parameters
    if page is None:
        page = 1
    if per_page is None:
        per_page = 10
    
    # query
    try:
        class_a_json = elaborate_ipclass_query("0.0.0.0","127.255.255.255", page, per_page, "Class A")
        class_b_json = elaborate_ipclass_query("128.0.0.0","191.255.255.255", page, per_page, "Class B")
        class_c_json = elaborate_ipclass_query("192.0.0.0","223.255.255.255", page, per_page, "Class C")
        class_d_json = elaborate_ipclass_query("224.0.0.0","239.255.255.255", page, per_page, "Class D")
        class_e_json = elaborate_ipclass_query("240.0.0.0","255.255.255.255", page, per_page, "Class E")

        result = []
        result.append(class_a_json) 
        result.append(class_b_json)
        result.append(class_c_json) 
        result.append(class_d_json) 
        result.append(class_e_json) 

        return result, 200
    except Exception as e:
        logging.error("error api: " + str(e))
        return jsonify({"error":"There was an error please contact the administrator"}), 400