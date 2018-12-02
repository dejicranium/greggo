import datetime

MONTH_MAPPING = {'January': 1,
				'February': 2,
				'March': 3,
				'April': 4,
				'May': 5,
				'June': 6,
				'July': 7,
				'August': 8,
				'September': 9,
				'October': 10,
				'November': 11,
				'December': 12
				}

NOW = datetime.datetime.utcnow()
CURRENT_YEAR = NOW.year
CURRENT_MONTH = NOW.month
CURRENT_DAY = NOW.day

def calculate_age(day, month, year):
	age_after_year_birthday = int(CURRENT_YEAR) - int(year)  		#after a user has celebrated her birthday this year
	age_before_year_birthday = int(CURRENT_YEAR) - int(year) - 1	#before a user celebrates her birthday

	#change month string (eg. January) into corresponding month int (eg. 1, in this case)
	month = MONTH_MAPPING[month]

	if int(CURRENT_MONTH) > int(month):
		return age_after_year_birthday

	elif int(CURRENT_MONTH) < month:
		return age_before_year_birthday

	else:  									#the present month is the user's birth month
		if int(CURRENT_DAY) > int(day):				# present day is still ahead of the day the user was born
			return age_after_year_birthday	

		elif int(CURRENT_DAY) < int(day):
			return age_before_year_birthday

		else:								#else today is user's birthday. Hence, he is + 1
			return age_after_year_birthday


def unpack_date_string(date_string, to_integers=True):
	"""
	Converts date string (user's birthday) into its corresponding day, month and year.
	Our date string should always be in this format:
		"January 1 1998"
	Invoking this function will return the following if the above date string is
	input:
		1, "January", 1998
	"""
	date = date_string.split()
	month, day, year = date[0], date[1], date[2]
	if to_integers:
		month, day, year = month, int(day), int(year)
	return day, month, year


def user_is_eligible(date_string):
	day, month, year = unpack_date_string(date_string)
	age = calculate_age(day, month, year)
	return age > 13 or age == 13


if __name__ == '__main__':
	print(is_eligible("January 1 1999"))
