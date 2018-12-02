import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import User
from ..models import APIRelease
from ..models.main_models import *


COUNTRIES_FILE = '/home/deji/countries.txt'
GHANA_FILE = '/home/deji/ghana_regions.txt'
ENGLAND_FILE = '/home/deji/england_counties.txt'
INDIAN_FILE = '/home/deji/indian_states.txt'
KENYA_FILE = '/home/deji/kenya_counties.txt'
NIGERIA_FILE = '/home/deji/nigeria_states.txt'
SOUTH_AFRICAN_FILE = '/home/deji/south_african_states.txt'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        from passlib.apps import custom_app_context
        admin = User(first_name='Deji', 
            last_name='Atoyebi',
            email='itisdeji@gmail.com', 
            password=custom_app_context.encrypt('int'),
            sex='Male',
            birth_date=26,
            birth_month="September",
            birth_year=1998,
            username='cranium',
            slug='deji-atoyebi'
            )

        grace = User(first_name='Grace', 
            last_name='Ogido',
            email='grace@gmail.com',
            password=custom_app_context.encrypt('int'),
            sex='Female',
            username='graiyce',
            birth_date=26,
            birth_month="September",
            birth_year=1998,
            slug='grace-ogido'

            )

        lara = User(first_name='Lara',
            last_name='Atoyebi',
            email='lara@gmail.com',
            password=custom_app_context.encrypt('int'),
            username='larrich',
            sex='Female',
            birth_date=26,
            birth_month="September",
            birth_year=1998        ,
            slug='lara-atoyebi'
            )


        with open(COUNTRIES_FILE, 'r') as countries:
            line = countries.readline()
            line = line.strip('\n')
            while line:
                if line != '\n':
                    country = Country()
                    country.name = line
                    dbsession.add(country)
            
                line = countries.readline()
        

        countries = dbsession.query(Country)
        _file = None
        for country in countries:
            

            if country.id == 2:
                _file = GHANA_FILE

            elif country.id == 1:
                _file =  ENGLAND_FILE
            elif country.id == 3:
                _file = INDIAN_FILE
            elif country.id == 5:
                _file = NIGERIA_FILE
            elif country.id == 6:
                _file  = SOUTH_AFRICAN_FILE
            elif country.id == 4:
                _file = KENYA_FILE
            
            with open(_file, 'r') as fl: 
                line = fl.readline()
                line = line.strip()
                while line:
                    if line != '\n': 
                        sub_national = SubNational()
                        sub_national.name = line
                        sub_national.country_id = country.id

                        dbsession.add(sub_national)

                    line = fl.readline()
                    
            

        dbsession.add_all([admin, grace, lara])
