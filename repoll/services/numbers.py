cdfile = '/home/cranium/agric_numbers.txt'
write_file = '/home/cranium/new_agric_numbers.csv'
names_file = '/home/cranium/new_agric_names_number_file.csv'

integer = 1
#file_to_write = open(write_file, 'w')
file_to_write = open(names_file, 'w')
count = 0
with open(file) as f:
    line = f.readline()
    while line:
        file_to_write.write("0{}".format(line))
        line = f.readline()


the_relationship_between_us = ther_is_no