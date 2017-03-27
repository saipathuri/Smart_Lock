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
		if i == 'Choose a number':
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
	return render_template('index_new.html', user_table=Markup(table.generate_table().__html__()), update_time = update_date_str)

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
		try:
			if mac_address == mac_regex.match(mac_address).group():
				cred.users[name] = mac_address.lower()
				cred.write_to_file()
				print "\n"
				print cred.users
				print "\n"
		except AttributeError:
				"""
				alert user invalid mac
				"""
				flash("Invalid MAC Address, must be in format: AA:BB:CC:DD:EE:FF", 'add')
	else:
		"""
		alert user no name
		"""
		flash("Must enter a name for the device", 'add')

	return redirect(url_for('home'))

@app.route('/remove/', methods = ['POST'])
def remove():
	entry_to_remove = request.args.get('key')
	print entry_to_remove
	cred.remove_entry(entry_to_remove)
	return redirect(url_for('home'))

@app.route('/update/', methods = ['POST', 'GET'])
def update():
	day = request.args.get('day')
	hour = request.args.get('hour')
	minute = request.args.get('minute')
	if minute == u'0':
		minute = u'00'
	cred.update_date(day, hour, minute)
	return redirect(url_for('home'))

@app.route('/update_password/', methods = ['POST', 'GET'])
def update_password():
	new_password = request.args.get('new_password')
	current_password = request.args.get('current_password')

	status = ''

	if auth._verify(current_password):
		auth.set_password(new_password)
		flash('Password updated', 'auth')
	else:
		flash('You entered the wrong password', 'auth')

	return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)