from flask import Flask, render_template, request, Markup, redirect, url_for, flash, Response
from flask_table import Table, Col
import table
import access_manager as cred
import string
import re
from flask_bootstrap import Bootstrap
import auth
import datetime
import calendar

def create_app():
	app = Flask(__name__)
	Bootstrap(app)
	return app

app = create_app()
app.secret_key = "don't tell anyone"
mac_regex = re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

@app.route('/')
@auth.requires_auth
def home():
	cred.read_file()
	update_date_arr = cred.get_date()
	today_day = datetime.date.today().day

	invalid_entry = False
	for i in update_date_arr:
		if i == ('Day' or 'Minute' or 'Hour'):
			invalid_entry = True

	if not invalid_entry:
		if(today_day <= int(update_date_arr[0])):
			month = calendar.month_name[datetime.date.today().month]
		else:
			month = calendar.month_name[(datetime.date.today().month+1)%12]

	if update_date_arr and not invalid_entry:
		update_date_str = month + ' ' + str(update_date_arr[0]) + " at " + str(update_date_arr[1]) + ":" + str(update_date_arr[2])
	else: 
		update_date_str = "No update time set, be sure to set all values"
	return render_template('index.html', user_table=Markup(table.generate_table().__html__()), update_time = update_date_str)

@app.route('/add/', methods = ['POST', 'GET'])
def add():
	name = ''
	mac_address = ''
	try:
		name = request.args.get('name')
		mac_address = request.args.get('macaddress')
	except:
		print("\n no credentials found \n")

	if name:
		#if the user is already in the system, don't add
		if cred.users.has_key(name):
			flash('Device with this name ({device_name}) already exists. Try again.'.format(device_name=name), 'add_fail')

		#if the user isn't already in the system, come here
		else:
			try:
				"""
				if mac_address matches regex, then check if it already exists
				if it does exist, prompt user to try again
				if it does not exist, then add it to list of trusted users and prompt user of success
				"""
				if mac_address == mac_regex.match(mac_address).group():
					mac_exists = False
					for i in cred.users.values():
						if i == mac_address.lower():
							mac_exists = True

					if not mac_exists:
						cred.users[name] = mac_address.lower()
						cred.write_to_file()
						flash("Successfully added trusted device ({device_name}, {device_mac}).".format(device_name=name, device_mac=mac_address.lower()), 'add_success')
						return redirect(url_for('home')+"#trusted")
					else:
						flash("Device with this MAC Address ({device_mac}) already exists. Try again.".format(device_mac=mac_address.lower()), 'add_fail')
			except AttributeError:
					"""
					alert user invalid mac
					#regex.match throws attribute error if the user enters invalid mac
					"""
					flash("Invalid MAC Address, must be in format: AA:BB:CC:DD:EE:FF", 'add_fail')
	else:
		"""
		alert user no name
		"""
		flash("Must enter a name for the device", 'add_fail')

	return redirect(url_for('home')+"#acl")

@app.route('/remove/', methods = ['POST'])
def remove():
	entry_to_remove = request.args.get('key')
	cred.remove_entry(entry_to_remove)
	return redirect(url_for('home')+"#trusted")

@app.route('/update/', methods = ['POST', 'GET'])
def update():
	day = request.args.get('day')
	hour = request.args.get('hour')
	minute = request.args.get('minute')

	error = False

	try:
		if(int(day) > 31 or int(day) < 0):
			flash('Day must be between 0 and 31. Try again.', 'update_fail')
			error = True
		if(int(hour) > 23 or int(hour) < 0):
			flash('Hour must be between 0 and 23. Try again.', 'update_fail')
			error = True
		if(int(minute) > 59 or int(minute) < 0):
			flash('Minute must be between 0 and 59. Try again.', 'update_fail')
			error = True
	except:
		flash('All values must be numbers. Try again.', 'update_fail')
		error = True

	if minute == u'0':
		minute = u'00'

	if not error:
		cred.update_date(day, hour, minute)
		flash('Update date successfully updated.', 'update_success')

	return redirect(url_for('home'))

@app.route('/update_password/', methods = ['POST', 'GET'])
def update_password():
	new_password = request.args.get('new_password')
	current_password = request.args.get('current_password')
	verify_new_pw = request.args.get('verify')

	status = ''

	if auth._verify(current_password):
		if(new_password == current_password):
			flash('New password and current password must not be the same', 'auth_fail')
		elif new_password != verify_new_pw:
			flash('New password and verify password do not match', 'auth_fail')
		else:
			auth.set_password(new_password)
			flash('Password updated', 'auth_success')
	else:
		flash('You entered the wrong password', 'auth_fail')

	return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)