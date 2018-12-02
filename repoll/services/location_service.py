from repoll.models.main_models import Country

def insert_countries_into_db(request):
    categories_from_file = []
    file = '/home/cranium/Documents/prod/repoll/repoll/services/countries.csv'
    with open(file) as fp:
        line = fp.readline()
        while line:
            name = None
            code = None
            
            lst = line.split(",")
            if len(country_and_code_list) != 2:
                name, code = lst[0] + ", "+lst[1], lst[2]
            else:
                name, code = lst[0], lst[1]

            country = Country()
            country.name = name
            country.country_code = code

            request.dbsession.add(country)
            line = fp.readline()

if __name__ == "__main__":
    insert_countries_into_db(request)
    print("Done")
