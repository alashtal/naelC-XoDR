#---------------------------------------------------------------------------#

# Python script to delete and create a list of deleted external users

# that were not active since May/2023 & NEVERR LOGGED IN

# Version 0.2 (LTS compatible)

# Author: Mohammed Al Ashtal

#---------------------------------------------------------------------------#

 

# Libraries or Dependencies

import sys

import dracoon_api

import csv

import os

import getpass

import time

from datetime import datetime

 

# Set up base  variables

client_id = 'X'

client_secret = 'X'

base_url = 'https://.com'

 

# Request USER credentials for login, NEEDS TO BE AN ADMIN a.k.a Andrzej, Moe or Qian

RO_user = input('Username: ')

RO_password = getpass.getpass('Password: ')

 

# Create a DRACOON API client object and set the base URL, good practice in Object Orienting Programming

my_dracoon = dracoon_api.dracoon(client_id, client_secret)

my_dracoon.set_URLs(base_url)

 

# Attempt to log in, the script will try to login to the URL based on Line 20 and check respone if 200 or not

login_response = my_dracoon.basic_auth(RO_user, RO_password)

if login_response.status_code != 200:

    print("Login failed, The script did not recieved okay (200): ", login_response.text)

    sys.exit()

 

print(f"Login is successful mate at: {time.strftime('%H:%M:%S')}, Go get coffee")

 

# Define a var with date constraints for later

date_threshold = datetime.strptime("2023-05-31", "%Y-%m-%d")

 

# Fetch user list from DRACOON, just as from DR

users = my_dracoon.get_users().json()['items']

total_users = my_dracoon.get_users().json()['range']['total']

 

# If more than 500 users, number the results in pages

if total_users > 500:

    for offset in range(500, total_users, 500):

        additional_users = my_dracoon.get_users(offset=offset).json()['items']

        users.extend(additional_users)

 

deleted_users_count = 0  # COUNTER for deleted users

# prepare for CSV export, meaning write the rows open path

csv_file_path = 'user_list.csv'

with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:

    csv_writer = csv.writer(csv_file, delimiter=';')

    csv_writer.writerow(['id', 'firstName', 'lastName', 'email', 'login', 'createdAt', 'lastLoginSuccessAt', 'expirationDate', 'isLocked', 'emailAuth', 'ADAuth', 'ADname'])

 

    # process each user, if it is roedl in the email or @alexianer then drop and ignore them

    for user in users:

        email = user.get('email', '').lower()

        if 'roedl' in email or '@alexianer' in email:

            continue

 

        user_id = user['id']

        creation_date = datetime.strptime(user['createdAt'][:10], "%Y-%m-%d")

 

        # check if user meets delete criteria, mentioned above

        if user.get('lastLoginSuccessAt') == "never logged in" and creation_date <= date_threshold:

            my_dracoon.delete_user(user_id)

            deleted_users_count += 1  # increment the counter when a user is deleted

            continue

 

        # write user details to an excel CSV file

        user_details = [user['id'], user['firstName'], user['lastName'], user['email'], user['login'], user['createdAt'], user['lastLoginSuccessAt'], user.get('expireAt', 'None'), user['isLocked'], 'False', 'False', 'None']

        csv_writer.writerow(user_details)

        print(f"Total number of deleted users: {deleted_users_count}")

#getcwd = get working dir

print(f"User report generated: {os.getcwd()}/{csv_file_path}")
