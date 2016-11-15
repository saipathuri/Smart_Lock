users = {}
ACL_file_location = 'ACL.txt'
update_file_location = 'updateTime.txt'

def remove_entry(key):
	del users[key]
	write_to_file()
	print users

def write_to_file():
	file = open(ACL_file_location, 'w')
	for key in users:
		file.write(key + "\t:\t" + users[key])
		file.write("\n")
	file.close()

def read_file():
	file = open(ACL_file_location)
	file_contents = file.read()
	file_by_line = file_contents.split("\n")
	file_by_tab = []
	for i in file_by_line:
		file_by_tab.append(i.split("\t"))
	
	for i in file_by_tab:
		try:
			users[i[0]] = i[2]
		except:
			pass
	file.close()

def update_date(day, hour, minute):
	file = open(update_file_location, 'w')
	file.write(day + '\n')
	file.write(hour + '\n')
	file.write(minute)
	file.close()

def get_date():
	file = open(update_file_location)
	file_contents = file.read()
	file_by_line = file_contents.split("\n")
	update_date = [i for i in file_by_line]
	file.close()
	return update_date
