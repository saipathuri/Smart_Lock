#!/bin/bash

scan ()
{
	# 0 -> locked
	# 1 -> unlocked
	prevState="$1"
	
	macAddrFile="$2"
	ACLFile="$3"
	
	if [[ ! $(ifconfig | grep 'wlan0') ]] || [[ $(arp-scan -l 2>/dev/null | grep 'ioctl') ]]
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
			else
				echo " ${line} is not an approved device."
			fi
		done

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
			return 0
		else
			echo "Door is now unlocked."
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
	macAddrFile="/Smart_Lock/Frontend/macAddresses.txt"
	ACLFile="/Smart_Lock/Frontend/ACL.txt"
	updateTimeFile="/Smart_Lock/Frontend/updateTime.txt"

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
	scan $prevState $macAddrFile $ACLFile >> $logFile 2>&1
	prevState=$?

	echo -e "//////////////////////////////////////////////////\n" >> $logFile
	
	if [ $oldPrevState != $prevState ]
	then
		sleep 3
	fi
done