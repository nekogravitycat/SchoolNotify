# SchoolNotify
**Grab announcements from the school website.**

## What is SchoolNotify?
SchoolNotify is an online service, automaticity collecting newest information from your school's website, then sent them into your email inbox.

## How can I use it?
You can subscribe to this service [here](https://sn.nekogc.com). Please fill out your email address and select your school. The system will send you a confirmation email, please visit the link provided within 5 minutes (or the link will be invalid and need to subscribe again.)

Please note that this service is still in an early stage of development, which means the number of supported schools is very limited and is waiting to be increased.

## When will I receive the news letters?
We will send you the news letter at 6pm on every Monday and Thursday, containing new announcements from your school.

## How can I unsubscribe from this service?
Each letter we sent to you contains a unsubscribe link at the bottom of the mail.

## Where's my information stored? Are they safe?
This service is hosted on [Heroku](https://heroku.com), and data is stored in [Redis Enterprise Cloud](https://redis.com). Only the developer of this project (me, nekogravitycat) can visit the database. We won't use or share any information anywhere.

To use this service, you only have to provide your email address, and we'll automatically generate a password stored in our database. Without the password, no one can modify your subscription status. The password will be included in the unsubscribe link we send to you, so please don't worry anything about that.

All of your information will be permanently deleted once you unsubscribe.