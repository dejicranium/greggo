import re
from greggo.config import REDIS_SERVER
from greggo.storage.redis.voters_gender_storage import PollVotersGenderStorage
from greggo.storage.redis.voters_age_storage import PollVotersAgeStorage

def get_overall_gender_distribution(poll_id):
    pass

class MetricsObject:
    """This refers to non-demographic objects we can get insights into:
        
        Option
        Poll
        Options
    """

    OPTION = "option"
    POLL = "poll"
    OPTIONS = 'options'
    

class DemographObject:
    """Demograhic Object that we can gain insights into
        GENDER
        AGE
        LOCATION
    """
    GENDER = "option"
    AGE = "age"
    LOCATION = "location"


class MetricsAggregator:
    """
    This class affords a Pozeet client insight into metrics associated with a poll.

    Noteworthy is that these metrics can be diverse. Say a poll like the below exists:

    Who is going to win the 2019 presidential elections?
    -Buhari
    -Atiku
    -Durotoye

    To view insights, a user would have to choose a 'main-focus' and a 'sub-focus' when intending to view metrics.

    Example 1: a 'main focus' could be the Poll itself, and the subfocus might be 'gender'. That is:
        main_focus  = "Poll" 
        sub_focus = "Gender"

        Interpretation: the user wishes to see the gender distribution of the respondents of that poll. (She wants to know how many men
        compared to women voted in that poll)

    Example 2: the 'main focus' could be an Option, and the subfocust might be a demographic attribute such as 'age': That is:
        main_focus = 'Option:{option_id here}"
        sub_focus = 'Gender'

        So, using the above poll as an example, a user can decide to view metrics on the option "Buhari" by requesting insights to how many people within
        the age of 18-30 as compared to users within the ages groups: 31-40 and 41-50 who voted the option "Buhari"
    
    Example 3: the 'main_focus' could be a demographic criterion such as locatoin and the 'sub focus' SHALL BE 'options'. Using the example poll, 
        a user could decide to see how many people in Lagos who voted Buhari as compared to the number of people in Lagos who will vote Buhari and Durotoye
    

    This is so much fun if you ask me, :-)
    
    """

    def __init__(self, main_focus, main_focus_objects, sub_focus, sub_focus_objects, poll_id):
        #see explanations above
        self.main_focus = main_focus
        self.sub_focus = sub_focus
        self.main_focus_objects = main_focus_objects
        self.sub_focus_objects = sub_focus_objects
        self.poll_id = poll_id

    #this is the publicly accessible method
    def get_metrics(self, source_store, redis_server=None):
        metrics = {}
        if self.main_focus == 'gender':
            metrics = self._get_gender_metrics(
                True,
                self.poll_id, 
                self.main_focus_objects, 
                self.sub_focus, 
                self.sub_focus_objects, 
                source_store,
                redis_server
                )

        elif (self.main_focus =='option' or self.main_focus == 'options') and self.sub_focus == 'gender':
            metrics = self._get_gender_metrics(
                False,
                self.poll_id,
                self.sub_focus_objects,
                self.main_focus,
                self.main_focus_objects,
                source_store,
                redis_server
            )

        elif self.main_focus == 'age' and (self.sub_focus =='option' or self.sub_focus == 'options'):
            metrics = self.get_age_metrics(
                True, 
                self.poll_id, 
                self.main_focus_objects, 
                self.sub_focus, 
                self.sub_focus_objects, 
                source_store,
                redis_server
            )

        elif self.main_focus == 'age_range' and (self.sub_focus == 'option' or self.sub_focus=='options' or self.sub_focus=='poll'):
            metrics = self.get_age_range_metrics(
                True,
                self.poll_id,
                self.main_focus_objects,
                self.sub_focus,
                self.sub_focus_objects,
                source_store,
                redis_server
            )
        
        return metrics


    def _get_gender_metrics(self, is_main_focus, poll_id, gender_objects, peer, peer_object, source_store, redis_server=None):

        """
            Here are things to note:
                1. if GENDER is not main focus, then it is a sub focus
                2. The metrics_object is talking about the id of the object which is either the main_focus or sub_focus of the metric 
                3. Source_store is where we are getting the data from
                4, gender_objects look like this: ['M', 'F'], ['F', 'M'], ['M'], ['F']

        """        
        gender_votes_mapping = {}

        if is_main_focus == True: 
            sub_focus = peer

            if sub_focus == 'poll':
            #remember on our Voters Gender Storage, data is stored like this: GENDER::OPTION: NumberOfVotes
            #Since the sub_focus is POLL, it means we are only concerned with how many men as compared to women voted in a poll
            #thus:
                poll_id = peer_object
                storage = source_store(poll_id, redis_server)
                votes_data = storage.get_gender_votes()  #this will return a dictionary (data is stored in a RedisHash)

                for gender, votes in votes_data.items():
                    match = re.match("(\w+)::(\w+)", gender.decode('utf-8'))
                    sex = match.group(1)
                    num_of_votes = votes.decode('utf-8')
                    gender_votes_mapping[sex] = {'votes': num_of_votes}
                keys = gender_votes_mapping.keys()

                
                if 'M' not in gender_votes_mapping.keys():
                        gender_votes_mapping['M'] = {'votes': 0}
                elif 'F' not in gender_votes_mapping.keys(): 
                    gender_votes_mapping['F'] = {'votes': 0}

                return gender_votes_mapping

            elif sub_focus == 'option':
                option_id = peer_object
                storage =  source_store(poll_id, redis_server)
                votes_data = storage.get_gender_votes()
                for gender, votes in votes_data.items():
                    match = re.match("(\w+)::(\w+)", gender.decode('utf-8'))
                    sex = match.group(1)
                    option = match.group(2)
                    num_of_votes = votes.decode('utf-8')
                    if int(option) == option_id:
                        gender_votes_mapping[sex] = {'votes': num_of_votes}

                keys = gender_votes_mapping.keys()


                if 'M' not in keys:
                    gender_votes_mapping['M'] = {'votes':0}
                if 'F' not in keys: 
                    gender_votes_mapping['F'] = {'votes':0}

                return gender_votes_mapping

            
            elif sub_focus == 'options':
                option_ids = peer_object
                gender_votes_mapping = {
                    'M': {str(option): {} for i, option in enumerate(option_ids)}, 
                    'F': {str(option): {} for i, option in enumerate(option_ids)},
                    }

                storage = source_store(poll_id, redis_server)
                votes_data = storage.get_gender_votes()

                for option in option_ids:
                    for gender, votes in votes_data.items():
                        match = re.match("(\w+)::(\w+)", gender.decode('utf-8'))
                        sex = match.group(1)
                        current_option = match.group(2)
                        if current_option == str(option):
                            num_of_votes = votes.decode('utf-8')
                            gender_votes_mapping[sex][str(option)]['votes'] = num_of_votes
                
                #if a particular gender has not voted in a poll, default to 0
                for gender in gender_votes_mapping.keys():
                    options = gender_votes_mapping[gender].keys()
                    for option in options:
                        if gender_votes_mapping[gender][option] == {}:
                            gender_votes_mapping[gender][option] = {'votes': 0}  

                
                return gender_votes_mapping



            #if a particular gender at 0. We should default Male and Female in our redis store
            #but we wish to save space, sorry.

        

        #the peer is the main_focus
        #here a, a single option is what we won't to get gender metrics for
        elif peer == 'option':
            #automatically, the sub_focus is DemographObject.Gender
            
            poll_id = poll_id
            option_id = peer_object
            gender_votes_mapping[str(option_id)] = {'F':{}, 'M':{}}
            storage = source_store(poll_id, redis_server)
            votes_data = storage.get_gender_votes()

            for gender, votes in votes_data.items():
                match = re.match("(\w+)::(\w+)", gender.decode('utf-8'))
                sex = match.group(1)
                option = match.group(2)
                if option == str(option_id):
                    num_of_votes = votes.decode('utf-8')
                    gender_votes_mapping[option][sex] = {'votes': num_of_votes}
            return gender_votes_mapping
        

        elif peer == 'options':
            option_ids = peer_object
            gender_votes_mapping = {str(option): {'M':{}, 'F':{}} for i, option in enumerate(option_ids)}
            storage = source_store(poll_id, redis_server)
            votes_data = storage.get_gender_votes()

            for option in option_ids:
                for gender, votes in votes_data.items():
                    match = re.match("(\w+)::(\w+)", gender.decode('utf-8'))
                    sex = match.group(1)
                    current_option = match.group(2)
                    if current_option == str(option):
                        num_of_votes = votes.decode('utf-8')
                        gender_votes_mapping[str(option)][sex] = {'votes': num_of_votes}
            
            for option in gender_votes_mapping.keys():
                genders = gender_votes_mapping[option].keys()
                for gender in genders:
                    if gender_votes_mapping[option][gender] == {}:
                        gender_votes_mapping[option][gender] = {'votes': 0}
         
            return gender_votes_mapping

            
    def get_age_range_metrics(self, is_main_focus, poll_id, age_range_string, peer, peer_object, source_store, redis_server=None):
        #get ages under age_range_string
        lower_bound, upper_bound = age_range_string.split('-')
        lower_bound, upper_bound = int(lower_bound), int(upper_bound)
        required_ages = []

        for i in range(lower_bound, upper_bound+1):
            required_ages.append(i)
       
        if peer == 'option':
            option_id = peer_object
            voters_age_range_mapping = {str(k): {'votes': ''} for k in required_ages}
            storage = source_store(poll_id, redis_server)
            votes_data = storage.get_ages()

            for age_and_option, votes in votes_data.items():
                match = re.match('(\w+)::(\w+)', age_and_option.decode('utf-8'))
                age = match.group(1)
                if age != "None":
                    age = int(age)
                option = match.group(2)
                
                if age in required_ages and int(option) == int(option_id): 
                    num_of_votes = int(votes.decode('utf-8'))
                    voters_age_range_mapping[str(age)]['votes'] = num_of_votes
                
                for key in voters_age_range_mapping.keys():
                    if voters_age_range_mapping[key]['votes'] == '':
                        voters_age_range_mapping[key]['votes'] = 0
                    
            return voters_age_range_mapping

        elif peer == 'options':
            option_ids = peer_object
            voters_age_range_mapping = {str(k): {str(option): {} for option in option_ids} for k in required_ages}
            store  = source_store(poll_id, redis_server)
            votes_data = store.get_ages()

            for option_id in option_ids: 
                for age_option, votes in votes_data.items():
                    match = re.match("(\w+)::(\w+)", age_option.decode('utf-8'))
                    age = match.group(1)
                    option = match.group(2)
                    
                    if int(age) in required_ages and str(option) == str(option_id): 
                        num_of_votes = int(votes.decode('utf-8'))
                        
                        if str(option) == "None" or str(option) != "'None'":
                            voters_age_range_mapping[str(age)][str(option)]['votes'] = num_of_votes
            
            for key in voters_age_range_mapping.keys():
                for i_key in voters_age_range_mapping[key].keys(): #i_key means inner key
                    if voters_age_range_mapping[key][i_key] == {}:
                        voters_age_range_mapping[key][i_key] = {'votes': 0}

        elif peer == 'poll':
            #there is no need to check for a peer object, it is our poll id

            voters_age_range_mapping = {str(age): {'votes': ''} for age in required_ages}
            store = source_store(poll_id, redis_server)  
            votes_data = store.get_ages()

            for age_and_option, votes in votes_data.items():
                match = re.match('(\w+)::(\w+)', age_and_option.decode('utf-8'))
                age = match.group(1)
                
                if int(age) in required_ages:
                    option = match.group(2)
                    num_of_votes = votes.decode('utf-8')
                    
                    voters_age_range_mapping[age] = {'votes': num_of_votes}
            
            for key in voters_age_range_mapping.keys():
                if voters_age_range_mapping[key]['votes'] == '':
                    voters_age_range_mapping[key] = 0
                

                          
            
        
        return voters_age_range_mapping





        

    def get_age_metrics(self, is_main_focus, poll_id, age_string, peer, peer_object, source_store, redis_server=None):
        #age string will look like this: "12,32,34,21,23"
        # so let's look for age one by one
        age_string = age_string
        storage = source_store(poll_id, redis_server)
        votes_data = storage.get_ages()


        if self.sub_focus == 'option':
            option_id = peer_object
            voters_age_mapping= {str(age_string): {'votes': ''}}
            
            for age_option, votes in votes_data.items():
                match = re.match("(\w+)::(\w+)", age_option.decode('utf-8'))
                
                age = match.group(1)
                option = match.group(2)
                
                if age == age_string and option == str(option_id):
                    num_of_votes = votes.decode('utf-8')
                    voters_age_mapping[str(age_string)]['votes'] = num_of_votes
                    break
                if voters_age_mapping[str(age_string)]['votes'] == '':
                    voters_age_mapping[str(age_string)]['votes'] =0
            
            
            return voters_age_mapping


        elif self.sub_focus == 'options':
            option_ids = peer_object
            voters_age_mapping = {str(age_string): {str(option): {}} for option in option_ids}            
            
            for age_option, votes in votes_data.items():
                match = re.match("(\w+)::(\w+)",  age_option.decode('utf-8'))
                age = match.group(1)
                option = match.group(2)

                if age == age_string and int(option) in option_ids:
                    num_of_votes = votes.decode('utf-8')
                    voters_age_mapping[age][option] = {'votes': num_of_votes}

            
            for key in voters_age_mapping.keys():
                for i_key in voters_age_mapping[key]:
                    if voters_age_mapping[key][i_key] == {}:
                        voters_age_mapping[key][i_key] = {'votes': 0}
            return voters_age_mapping


        

if __name__ == '__main__':
    #t = PollVotersAgeStorage(1, REDIS_SERVER)
    #print(t.get_ages())

    metrics = MetricsAggregator('age', '22', "option", 1, 1)
    print(metrics.get_metrics(PollVotersAgeStorage, REDIS_SERVER))

    t = PollVotersAgeStorage(1, REDIS_SERVER)

    
