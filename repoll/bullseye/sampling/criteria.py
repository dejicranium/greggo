from .base import Criterion

CRITERIA = frozenset(["Location", "Age", "Interest", "Profession"])

class SubCriterion:
    def __init__(self, criterion):
        self.criterion = criterion

        #we need to ha
        self.dictt = dict()
        self.flatten_to_dict()

    def get_flattened_criterion(self):
        """
        The flattened criterion, which is the dictt
        """
        return self.dictt

    def get_criterion(self):
        return self.criterion

    def flatten_to_dict(self):
        criterion = self.criterion
        dictt = self.dictt
        dictt['type'] = criterion.get_type()
        criterion_type = dictt['type']
        if criterion_type == 'Location':
            dictt['place'] = criterion.get_place()
        dictt['sample_size'] = criterion.get_sample_size()


class Location(Criterion):
    def __init__(self, place, sample_size, *args, **kwargs):
        #location can be a list of locations
        Criterion.__init__(self, sample_size)

        self.place = place

    def add_place(self, place):
        self.place = place

    def get_place(self):
        return self.place


class Criteria:
    def __init__(self, list_of_criterion):
        self.list_of_criterion = list_of_criterion
        self.dictt = {'criteria': []}
        self.flatten()

    def add_criterion(self, criterion):
        self.list_of_criterion.append(criterion)

    def get_criteria(self):
        return self.dictt

    def flatten(self):
        for criterion in self.list_of_criterion:
            c_dict = {}
            c_type = criterion.get_type()
            if c_type == "Location":
                c_dict['type'] = c_type
                c_dict['place'] = criterion.get_place()
                c_dict['sample_size'] = criterion.get_sample_size()
                if criterion.has_sub_criteria():
                    c_dict['sub_criteria'] = []
                    for each in criterion.get_sub_criteria():
                        new_dict = {}
                        new_dict['type'] = each.get_criterion().get_type()
                        new_dict['place'] = each.get_criterion().get_place()
                        new_dict['sample_size'] = each.get_criterion().get_sample_size()
                        c_dict['sub_criteria'].append(new_dict)
            self.dictt['criteria'].append(c_dict)
