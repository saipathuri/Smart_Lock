# import things
from flask_table import Table, Col, ButtonCol
import access_manager as cred

# Declare your table
class ItemTable(Table):
    name = Col('Name')
    description = Col('MAC Address')
    classes=['table']
    remove = ButtonCol('Remove', 'remove', url_kwargs=dict(key='name'), button_attrs={'class':'btn btn-primary'})

# Get some objects
class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description


def generate_table():
	try:
		items = [Item(i, cred.users[i]) for i in cred.users]
	except:
		items = [Item('No Users', '')]

	# Populate the table
	populated_table = ItemTable(items)
	return populated_table