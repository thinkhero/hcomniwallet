RECAPTCHA_PRIVATE = None #replace private key text here
ADMINEMAIL = None #admin email
DOMAIN = 'testnet-hcomni-wallet.h.cash'   #Replace with domain to override email domain lookup, otherwise system hostname is used
EMAILFROM = 'hcomniwallet@h.cash'  #Is set to None, use noreply@domain
SMTPUSER = 'hcomniwallet@h.cash'   #If your smtp server requires authentication define it here
SMTPPASS = 'Bn7B4FP4VgXaZZ83'   #If your smtp server requires authentication define it here
SMTPDOMAIN ='smtp.mxhichina.com'  #smtp server to use for sending, default    'localhost'
SMTPPORT =465      #smtp port,  default 25
SMTPSTARTTLS = True  # Use starttls before SMTP login
WELCOMECID = None #mailgun campaign id for welcome email stats

#For wallets and session store you can switch between disk and the database
LOCALDEVBYPASSDB = 0    #Set to 1 to use local storage/file system, Set to 0 to use database

#Used to generate challange/response hash
SERVER_SECRET = 'SoSecret!'
SESSION_SECRET = 'SuperSecretSessionStuff'
WEBSOCKET_SECRET = 'SocketSecret!'

#used for encrypting/decrypting secure values. 
#NOTE: If these values change, anything previously encrypted with them will need to be updated / encrypted with the new values
AESKEY='0604b0ffa093258c'
AESIV='4b763e6e77c3db01'

#Donation Address Pubkey  (We need the pubkey so that if an address hasn't sent a tx before we don't need the private key to get the pubkey)
D_PUBKEY = '04ec31f456cc70a60793ff2033d9d2094541a5de8cac67ab1e5b1441187c6bed1601dc64c447244618268af0bd449d90d2ce71816efc69dc7921a226ed60fe926b'

#Blocktrail API Key (used for lookups of utxo's)
BTAPIKEY = None

#Redis Connection Info
REDIS_HOST='localhost'
REDIS_PORT=6379
REDIS_DB=0
#Use if you want custom address namespace (multiple servers on same box)
#Must prefix custom name with :  example ":stage"
REDIS_ADDRSPACE=""
#How long, in seconds, to cache BTC balance info for new addresses, Default 2min (120)
BTCBAL_CACHE=120

