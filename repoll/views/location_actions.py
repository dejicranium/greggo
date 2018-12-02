from ..models.main_models import Country
from pyramid.view import view_config

@view_config(route_name='get_locations', renderer='json')
def get_location(request):
    locations = {'locations': []}
    countries = request.dbsession.query(Country)

    for country in countries: 
        country_dictt  = {'country': '', 'id': 0,  'subUnits': []}
        country_dictt['country'] = country.name
        country_dictt['id'] = country.id
        
        for subnational in country.sub_nationals:
            sub_dictt = {'id': 0, 'name': ''}
            sub_dictt['id']= subnational.id
            sub_dictt['name'] = subnational.name
        
            country_dictt['subUnits'].append(sub_dictt)

        locations['locations'].append(country_dictt)

    return locations