from flask import Flask, render_template, request, Markup, redirect, url_for, flash
from flask_table import Table, Col
import table
import access_manager as cred
import string
import re

app = Flask(__name__)
app.secret_key = "don't tell anyone"

mac_regex = re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

@app.route('/')
def index():
	return redirect(url_for('home'))

# @app.route('/#')
# def tab_fix():
# 	return redirect(url_for('home'))

@app.route('/home/')
def home():
	cred.read_file()
	update_date = cred.get_date()
	if update_date:
		update_date = "Day " + str(update_date[0]) + " at " + str(update_date[1]) + ":" + str(update_date[2])
	else: 
		update_date = "No update date set"
	return render_template('index.html', user_table=Markup(table.generate_table().__html__()), update_time = update_date)

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
				flash("Invalid MAC Address, must be in format: AA:BB:CC:DD:EE:FF")
	else:
		"""
		alert user no name
		"""
		flash("Must enter a name for the device")

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
	cred.update_date(day, hour, minute)
	return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)