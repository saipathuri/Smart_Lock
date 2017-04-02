#!/bin/bash

createChartFile ()
{
	ACLFile="$1"
	rawChartDataFile="$2"
	# if rawChartData.txt doesn't already exist, create it with the first line being `mm/dd/yyyy`
	# or if rawChartData.txt is not data of the same day
        if [ ! -f $rawChartDataFile ] || [ $(date +%x) != $(head -n 1 $rawChartDataFile) ]
        then
                echo "$(date +%x)" > $rawChartDataFile

		# for each user in ACL.txt, add their name and hourly data into rawChartData.txt
                echo "$(cut -d$'\t' -f1 $ACLFile)" | ( while read username
                do
                        echo -e "$username\t000000000000000000000000" >> $rawChartDataFile
                done
                )
	fi

	# (assuming rawChartData.txt is populated)
	# the number of users in ACL.txt is different that the number of users in rawChartData.txt
	if [[ $(cat $ACLFile | wc -l) > $(($(cat $rawChartDataFile | wc -l) - 1)) ]]
	then
		# if user from ACL.txt does not exist in rawChartData.txt, add the user to rawChartData.txt
		echo "$(cut -d$'\t' -f1 $ACLFile)" | (while read usernameACL
		do
			isInRaw=false
			# once it finds a username in rawChartData.txt that matches the ACL.txt username,
			# the while loop is broken
			echo "$(tail -n +2 $rawChartDataFile | cut -d$'\t' -f1)" | (while read usernameRaw
			do
				if [[ $usernameRaw == $usernameACL ]]
				then
					isInRaw=true
					break
				fi
			done

			# if every username in rawChartData.txt is searched and none match the ACL.txt
			# username, that ACL.txt username is added to the end of rawChartData.txt
			if [[ $isInRaw == false ]]
			then
				echo -e "$usernameACL\t000000000000000000000000" >> $rawChartDataFile
			fi
			)
		done
		)
	elif [[ $(cat $ACLFile | wc -l) < $(($(cat $rawChartDataFile | wc -l) - 1)) ]]
	then
		# if user from rawChartData.txt does not exist in ACL.txt, remove the user from rawChartData.txt
		echo "$(tail -n +2 $rawChartDataFile | cut -d$'\t' -f1)" | (while read usernameRaw
		do
			isInACL=false
			# once it finds a username in ACL.txt that matches the rawChartData.txt username,
			# the while loop is broken
			echo "$(cut -d$'\t' -f1 $ACLFile)" | (while read usernameACL
			do
				if [[ $usernameACL == $usernameRaw ]]
				then
					isInACL=true
					break
				fi
			done

			# if every username in ACL.txt is searched and none match the rawChartData.txt
			# username, that rawChartData.txt username is removed from the file
			if [[ $isInACL == false ]]
			then
				sed -i "/$usernameRaw\t/d" $rawChartDataFile
			fi
			)
		done
		)
	fi
}

createTableFile ()
{
	numberToUserTableFile="$1"
	rm $numberToUserTableFile
	count=1
	echo "$(cut -d$'\t' -f1 $ACLFile)" | (while read usernameACL
        do
		echo "$count:$usernameACL" >> $numberToUserTableFile
		count=$(($count + 1))
	done
	)
}

outputToChart ()
{
	rawChartDataFile="$1"
	numberToUserTableFile="$2"
	chartDataFile="$3"
	str="chartData = '{\"labels\":[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], \"series\":["

	cat $numberToUserTableFile | (while read line
	do
		num=$(echo $line | cut -d':' -f1)
		name=$(echo $line | cut -d':' -f2)
		userData=$(echo -e "$(grep -P ^"${name}\t" $rawChartDataFile)" | cut -d$'\t' -f2)

		arr="["
		for ((i=0; i<${#userData}; i++ ))
		do
			if [[ ${userData:$i:1} == 0 ]]
			then
				arr="${arr}null, "
			else
				arr="${arr}${num}, "
			fi
		done
		arr="${arr:0:-2}], "
		str="${str}${arr}"
	done

	str="${str:0:-2}]}';"

	echo $str > $chartDataFile
	)
}

scan ()
{
	# 0 -> locked
	# 1 -> unlocked
	prevState="$1"

	macAddrFile="$2"
	ACLFile="$3"
	rawChartDataFile="$4"
	chartDataFile="$5"
	numberToUserTableFile="$6"
	servo="$7"

	if ! nc -zw1 google.com 443 2>/dev/null
	then
		echo "Error! Not connected to wireless network"
		sleep 2
	else
		echo "Scanning all devices on local network."

		# Output all device information on local network, file is created if it doesn't already exist
		arp-scan -l > $macAddrFile

		# Keep only lines containing IP and MAC addresses
		numLines=$(cat $macAddrFile | wc -l)
		if [ $numLines != 0 ] && [ $numLines != 1 ] && [ $numLines != 2 ]
		then
			echo "$(sed -n "3,$(($numLines - 3))p" $macAddrFile)" > $macAddrFile
		fi

		# Extract IP and MAC addresses
		addresses=
		cat $macAddrFile | ( while read line
		do
			addresses+="\n$(echo ${line} | cut -d ' ' -f2)"
		done
		echo -e "$addresses" > $macAddrFile
		sed -i '1d' $macAddrFile
		)

		# Removes duplicate lines
		echo "$(sort $macAddrFile | uniq)" > $macAddrFile

		echo " $(cat $macAddrFile | wc -l) device(s) have been found."
		echo "Comparing devices on network with ACL."

		createChartFile $ACLFile $rawChartDataFile
		createTableFile $numberToUserTableFile

		# Unlocks door only if a device that is on the ACL is on the network
		currState=0
		cat $macAddrFile | ( while read line
		do
			if grep -q "${line}" $ACLFile
			then
				name=$(grep "${line}" $ACLFile | cut -d$'\t' -f1)
				mac=$(grep "${line}" $ACLFile | cut -d$'\t' -f3)
				echo " $mac is an approved device, $name has unlocked the door."
				#echo "${line} has unlocked the door."
				currState=1

				hour=$(date +%H)
				userData=$(echo -e "$(grep -P "${name}\t" $rawChartDataFile)" | cut -d$'\t' -f2)
				userData="${userData:0:$hour}1${userData:$(($hour + 1))}"
				oldUserLine=$(echo -e "$(grep -P "${name}\t" $rawChartDataFile)")
				sed -i "s/$oldUserLine/$name\t$userData/g" $rawChartDataFile
			else
				echo " ${line} is not an approved device."
			fi
		done

		outputToChart $rawChartDataFile $numberToUserTableFile $chartDataFile

		if [ $prevState == 0 ] && [ $currState == 0 ]
		then
			echo "Door remains locked."
			return 0
		elif [ $prevState == 1 ] && [ $currState == 1 ]
		then
			echo "Door remains unlocked."
			return 1
		elif [ $prevState == 1 ] && [ $currState == 0 ]
		then
			echo "Door is now locked."
			python $servo l u
			return 0
		else
			echo "Door is now unlocked."
			python $servo u l
			return 1
		fi )
	fi
}

monthlyUpdate ()
{
	echo "Performing monthly updates."

	echo "Fetching the list of available updates."
	apt-get update -y -qq
	echo "Fetching complete."

	sleep 1

	echo "Upgrading current packages."
	apt-get upgrade -y -qq
	echo "Upgrading complete."

	sleep 1

	echo "Installing new updates."
	apt-get dist-upgrade -y -qq
	echo "Installing complete."

	sleep 1

	echo "Cleaning up partial packages."
	apt-get autoclean -y -qq
	echo "Cleaning up apt cache."
	apt-get clean -y -qq
	echo "Cleaning up unused dependencies."
	apt-get autoremove -y -qq
	echo "Cleaning complete."

	sleep 1

	echo "Updating time zone."
	easy_install -q pip
	if pip search tzupdate | grep -q "INSTALLED"
	then
		pip install -U tzupdate
	fi
	tzupdate > /dev/null
	str=$(tzupdate -p)
	echo "Timezone is set to" ${str:20}

	sleep 1

	echo "Rebooting."
	echo -e "//////////////////////////////////////////////////\n"
	reboot
}









# function main

prevState=0

# infinite loop
while [ true ]
do
	year=$(date +%Y)
	month=$(date +%m)
	day=$(date +%d)
	hour=$(date +%H)

	logFile="/Smart_Lock/logs/$year/$month/$day/$hour.txt"
	macAddrFile="/Smart_Lock/macAddresses.txt"
	ACLFile="/Smart_Lock/Frontend/acl.txt"
	updateTimeFile="/Smart_Lock/Frontend/update.txt"
	rawChartDataFile="/Smart_Lock/Frontend/static/rawChartData.txt"
	chartDataFile="/Smart_Lock/Frontend/static/chartData.json"
	numberToUserTableFile="/Smart_Lock/Frontend/static/numberToUserTable.txt"
	servo="/Smart_Lock/servo.py"

	if [ ! -d /Smart_Lock/logs/$year/$month/$day ]
	then
		mkdir -p /Smart_Lock/logs/$year/$month/$day/
	fi

	if [ ! -f $logFile ]
	then
		touch $logFile
		echo -e "Created log on $(date "+%m/%d/%Y %r")\n" >> $logFile
	fi

	echo -e "//////////    $(date "+%m/%d/%Y %r")    //////////" >> $logFile

	# Only runs the monthly update once a month on a set day, hour, and minute
	#		day								hour							minute
	if [ "$day" == "$(sed '1q;d' $updateTimeFile)" ] && [ "$(date +%k)" == "$(sed '2q;d' $updateTimeFile)" ] && [ "$(date +%M)" == "$(sed '3q;d' $updateTimeFile)" ]
	then
		monthlyUpdate >> $logFile
	fi

	oldPrevState=$prevState
	scan $prevState $macAddrFile $ACLFile $rawChartDataFile $chartDataFile $numberToUserTableFile $servo >> $logFile 2>&1
	prevState=$?

	echo -e "//////////////////////////////////////////////////\n" >> $logFile

	if [ $oldPrevState != $prevState ]
	then
		sleep 3
	fi
done