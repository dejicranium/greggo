
class Criterion:
    """This is meant to be the Base Criterion
        Use it to check that a class is a Criterion
    """
    def __init__(self, sample_size):
        self.sample_size = sample_size
        self.sub_criteria = []

    def add_sub_criterion(self, criterion):
        self.sub_criteria.append(criterion)

    def add_sub_criteria(self, criteria):
        self.sub_criteria = criteria

    def get_type(self):
        return str(self.__class__.__name__)

    def get_sample_size(self):
        return self.sample_size

    def has_sub_criteria(self):
        return len(self.sub_criteria) > 0

    def get_sub_criteria(self):
        return self.sub_criteria
