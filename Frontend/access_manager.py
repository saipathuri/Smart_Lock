users = {}
acl_location = '/Smart_Lock/Frontend/acl.txt'
update_location = '/Smart_Lock/Frontend/update.txt'

def remove_entry(key):
	del users[key]
	write_to_file()

def write_to_file():

	file = open(acl_location, 'w')

	for key in users:
		file.write(key + "\t:\t" + users[key])
		file.write("\n")
	file.close()

def read_file():
	try:
		file = open(acl_location)
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
	except:
		write_to_file()

def update_date(day, hour, minute):
	file = open(update_location, 'w')
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
	file = open(update_location, 'w')
	file.write(day + '\n')
	file.write(hour + '\n')
	file.write(minute)
	file.close()

def get_date():
	update_date_arr = None
	file = None
	try:
		file = open(update_location)
		file_contents = file.read()
		file_by_line = file_contents.split("\n")
		update_date_arr = [i for i in file_by_line]
		file.close()
	except:
		update_date('1','1','00')
		file = open(update_location)
		file_contents = file.read()
		file_by_line = file_contents.split("\n")
		update_date_arr = [i for i in file_by_line]
		file.close()

	return update_date_arr

