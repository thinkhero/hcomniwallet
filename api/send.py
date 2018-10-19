import urlparse
import os, sys, json
#tools_dir = os.environ.get('TOOLSDIR')
#lib_path = os.path.abspath(tools_dir)
#sys.path.append(lib_path)
#from msc_utils_parsing import *
from common_utils import *
from blockchain_utils import *
from msc_apps import *
import random

max_currency_value=21000000
dust_limit=5757

def send_form_response(response_dict):
    print "send form response dict"
    print response_dict

    expected_fields=['from_address', 'to_address', 'amount', 'currency', 'fee']
    # if marker is True, send dust to marker (for payments of sells)
    for field in expected_fields:
        if not response_dict.has_key(field):
            info('No field '+field+' in response dict '+str(response_dict))
            return (None, 'No field '+field+' in response dict '+str(response_dict))
        if len(response_dict[field]) != 1:
            info('Multiple values for field '+field)
            return (None, 'Multiple values for field '+field)
          
    # return unspent utxo
    from_addr=response_dict['from_address'][0]
    amount=response_dict['amount'][0]
    dirty_txes = hc_getunspentutxo(from_addr, float(amount))
    if dirty_txes["error"] != "none":
        return (None, dirty_txes["error"])
    else:
        return (json.dumps({"status":"OK", "utxos":dirty_txes["utxos"]}), None)

    if 'testnet' in response_dict and ( response_dict['testnet'][0] in ['true', 'True'] ):
        testnet =True
        magicbyte = 111
    else:
        testnet = False
        magicbyte = 0

    if response_dict.has_key( 'pubKey' ): #and is_pubkey_valid( response_dict['pubKey'][0]):
        pubkey = response_dict['pubKey'][0]
        response_status='OK'
    else:
        response_status='invalid pubkey'
        pubkey=None
    #max btc amount
  
    from_addr=response_dict['from_address'][0]
    #if not is_valid_bitcoin_address_or_pubkey(from_addr):
    #    return (None, 'From address is neither bitcoin address nor pubkey')
    to_addr=response_dict['to_address'][0]
    #if not is_valid_bitcoin_address(to_addr):
    #    return (None, 'To address is not a bitcoin address')
    amount=response_dict['amount'][0]
    if float(amount)<0 or float( from_satoshi(amount))>max_currency_value:
        return (None, 'Invalid amount: ' + str( from_satoshi( amount )) + ', max: ' + str( max_currency_value ))
    btc_fee=response_dict['fee'][0]
    if float(btc_fee)<0 or float( btc_fee )>max_currency_value:
        return (None, 'Invalid fee: ' + str( btc_fee ) + ', max: ' + str( max_currency_value ))
    currency=response_dict['currency'][0]
    if currency=='OMNI':
        currency_id=1
    else:
        if currency=='T-OMNI':
            currency_id=2
        else:
            if currency=='BTC':
                currency_id=0
            else:
                if currency[:2] == 'SP':
                    currency_id=int(currency[2:])
                else:
                    return (None, 'Invalid currency')

    marker_addr=None
    try:
        marker=response_dict['marker'][0]
        if marker.lower()=='true':
            marker_addr=exodus_address
    except KeyError:
        # if no marker, marker_addr stays None
        pass

    if pubkey == None:
        tx_to_sign_dict={'transaction':'','sourceScript':''}
        l=len(from_addr)
        if l == 66 or l == 130: # probably pubkey
            #if is_pubkey_valid(from_addr):
                pubkey=from_addr
                response_status='OK'
            #else:
            #    response_status='invalid pubkey'
        else:   
            #if not is_valid_bitcoin_address(from_addr):
            #    response_status='invalid address'
            #else:
                from_pubkey=bc_getpubkey(from_addr)
                #if not is_pubkey_valid(from_pubkey):
                #    response_status='missing pubkey'
                #else:
                pubkey=from_pubkey
                response_status='OK'

    try:
      if pubkey != None:
          tx_to_sign_dict=prepare_send_tx_for_signing( pubkey, to_addr, marker_addr, currency_id, amount, to_satoshi(btc_fee), magicbyte)
      else:
          # hack to show error on page
          tx_to_sign_dict['sourceScript']=response_status

      response='{"status":"'+response_status+'", "transaction":"'+tx_to_sign_dict['transaction']+'", "sourceScript":"'+tx_to_sign_dict['sourceScript']+'"}'
      print "Sending unsigned tx to user for signing", response
      return (response, None)
    except Exception as e:
      print "error creating unsigned tx", e
      return (None, str(e))


# simple send and bitcoin send (with or without marker)
def prepare_send_tx_for_signing(from_address, to_address, marker_address, currency_id, amount, btc_fee=500000, magicbyte=0):
    print '*** send.py tx for signing: from_address, to_address, marker_address, currency_id, amount, btc_fee, magicbyte'
    print from_address, to_address, marker_address, currency_id, amount, btc_fee, magicbyte

    # consider a more general func that covers also sell offer and sell accept

    # check if address or pubkey was given as from address
    if from_address.startswith('0'): # a pubkey was given
        from_address_pub=from_address
        from_address=pybitcointools.pubkey_to_address(from_address,magicbyte)
    else: # address was given
        from_address_pub=addrPub=bc_getpubkey(from_address)
        from_address_pub=from_address_pub.strip()

    # set change address to from address
    change_address_pub=from_address_pub
    changeAddress=from_address
  
    satoshi_amount=int( amount )
    fee=int( btc_fee )

    # differ bitcoin send and other currencies
    if currency_id == 0: # bitcoin
        # normal bitcoin send
        required_value=satoshi_amount
        # if marker is needed, allocate dust for the marker
        if marker_address != None:
            required_value+=1*dust_limit
    else:
        #tx_type=0 # only simple send is supported
        #required_value=4*dust_limit
        raise Exception({ "status": "NOT OK", "error": "Deprecated. Please use /v1/transaction/getunsigned" })
 
    #------------------------------------------- New utxo calls
    fee_total_satoshi=required_value+fee
    dirty_txes = bc_getutxo( from_address, fee_total_satoshi )

    if (dirty_txes['error'][:3]=='Con'):
        raise Exception({ "status": "NOT OK", "error": "Could not get list of unspent txs. Response Code: " + str(dirty_txes['code']) })

    if (dirty_txes['error'][:3]=='Low'):
        raise Exception({ "status": "NOT OK", "error": "Not enough funds, for " + str(from_address) + ". Needed: " + str(fee_total_satoshi) + " but Have: " + str(dirty_txes['avail'])  })

    inputs_total_value = dirty_txes['avail']
    inputs = dirty_txes['utxos']

    #------------------------------------------- Old utxo calls
    # get utxo required for the tx
    #utxo_all=get_utxo(from_address, required_value+fee)

    #utxo_split=utxo_all.split()
    #inputs_number=len(utxo_split)/12
    #inputs=[]
    #inputs_total_value=0

    #if inputs_number < 1:
    #    info('Error not enough BTC to generate tx - no inputs')
    #    raise Exception('This address must have enough BTC for protocol transaction fees and miner fees')
    #for i in range(inputs_number):
    #    inputs.append(utxo_split[i*12+3])
    #    try:
    #        inputs_total_value += int(utxo_split[i*12+7])
    #    except ValueError:
    #        info('Error parsing utxo, '+ str(utxo_split) )
    #        raise Exception('Error: parsing inputs was invalid, do you have enough BTC?')

    #inputs_outputs='/dev/stdout'
    #for i in inputs:
    #    inputs_outputs+=' -i '+i
    #---------------------------------------------- End Old utxo calls

    inputs_outputs='/dev/stdout'
    ins=[]
    outs=[]
    for i in inputs:
        inhash=str(i[0])+':'+str(i[1])
        inputs_outputs+=' -i '+inhash
        ins.append(inhash)


    # calculate change
    change_value=inputs_total_value-required_value-fee
    if change_value < 0:
        info('Error not enough BTC to generate tx - negative change')
        raise Exception('This address must have enough BTC for miner fees and protocol transaction fees')

    if currency_id == 0: # bitcoin
        # create a normal bitcoin transaction (not mastercoin)
        # dust to marker if required
        # amount to to_address
        # change to change

        if marker_address != None:
            inputs_outputs+=' -o '+marker_address+':'+str(dust_limit)
            outs.append(marker_address+':'+str(dust_limit))
        inputs_outputs+=' -o '+to_address+':'+str(satoshi_amount)
        outs.append(to_address+':'+str(satoshi_amount))
        
    else:
        #DEPRECATED - ALL OMNI TX Created by tx_generate_service - 
        raise Exception({ "status": "NOT OK", "error": "Deprecated. Please use /v1/transaction/getunsigned" })


    if change_value >= dust_limit:
        inputs_outputs+=' -o '+changeAddress+':'+str(change_value)
        outs.append(changeAddress+':'+str(change_value))
    else:
        # under dust limit leave all remaining as fees
        pass

    #tx=mktx(inputs_outputs)
    info('inputs_outputs are '+str(ins)+' '+str(outs))
    try:
      tx=pybitcointools.mktx(ins,outs)
    except:
      raise Exception({ "status": "NOT OK", "error": "Invalid Bitcoin address, please check and try again" })

    #info('inputs_outputs are '+inputs_outputs)
    info('tx is '+str(tx))

    hash160=bc_address_to_hash_160(from_address).encode('hex_codec')
    prevout_script='OP_DUP OP_HASH160 ' + hash160 + ' OP_EQUALVERIFY OP_CHECKSIG'

    # tx, inputs
    return_dict={'transaction':tx, 'sourceScript':prevout_script}
    return return_dict

def send_handler(environ, start_response):
    return general_handler(environ, start_response, send_form_response)

