# BinanceSMS
Monitor market movements, program trades, and be notified via SMS/Email along the way with BinanceSMS
# How to run the bot
In order for everything to work, you will need to setup a few things...

Python 3 is needed
Pip3 is needed
```
sudo apt install python3-pip
```    
When Python3 and pip3 are installed, you need to install python-binance
```
pip3 install python-binance
``` 
Now you need to do is set up a GMail account specifically for this bot. You
do not want to use your regualar email because we will be forwarding all emails
to a phone number.

So setup a new GMail account and make sure to allow less secure apps. It will not
work otherwise.
    https://myaccount.google.com/lesssecureapps

Once you have that setup, if you want to receive notifications to your phone,
you will need to figure out what your phone's carrier email address is. You will
have to do some Googling for this as I only know that for T-Mobile, your email
address would be YOUR_NUMBER@tmomail.net. So figure out what your phone's email
address is and log in to your new GMail account.

Go to Settings>Forwarding and POP/IMAP>Forwarding:
and enter in your phone's email address and verify it. Then you will have to set
what you want GMail to do with the emails.
I have it set to forward a copy of incoming mail to my phone's email and 
delete GMail's copy.

You will also need your API Key and secret from Binance.
    https://www.binance.com/userCenter/createApi.html
    
Last thing, I reccommend using screen when running the python script. It will
keep the script running when you logout of your machine. I run my python script
on a Raspberry Pi that I keep running 24/7. I set my router up to forward port 22
to the Raspberry Pi so I can log into it from anywhere. You can also use Amazon
AWS, but free tier only covers 700 hours a month and then you have to start paying.
    sudo apt install screen

Screen instructions:
Create a new screen:
```
screen -S screenName
```
Exit screen: 
```
Ctrl + a + d
```
Switch to screen: screen -r screenName

HOW TO RUN THE BOT:
Make sure you have changed all the values in the config.py file and have all the
files downloaded in the same location.
Start a new screen and attach to it.
(When you first create a screen, you are automatically attached to it)
```
screen -S screenName
python3 startBot.py
```
That's it. Now the bot will start running 24/7. You can detatch from the screen
using Ctrl + a + d without stopping the script.   
