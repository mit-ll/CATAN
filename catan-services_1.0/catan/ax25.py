"""
    AX25 module adapted from the DIXPRS project

    (c) 2015 Massachusetts Institute of Technology
"""
####################################################
# APRS digipeater and gateway for amateur radio use
# (C) HA5DI - 2012
# http://sites.google.com/site/dixprs/
####################################################


#Constants for KISS framing
FEND  = chr(0xC0)
FESC  = chr(0xDB)
TFEND = chr(0xDC)
TFESC = chr(0xDD)

#Sending

def build_raw_msg(callfrom, callto="ALL", data='', digis=[]):
    """
        Build an AX25 message with KISS framing
    """

    msg = callsign_encode(callto) + callsign_encode(callfrom)
    
    for i in range(1, len(digis)):
        if len(digis[i]) > 1:
            msg += callsign_encode(digis[i])

    msg = msg[:-1] + chr(ord(msg[-1]) | 0x01) + chr(0x03) + chr(0xf0) + data
    return msg 

def callsign_encode(ctxt):
    """
        Encode the callsign using the AX25 format
    """

    if ctxt[-1] == '*':
        s = ctxt[:-1]
        digi = True
    else:
        s = ctxt
        digi = False
                
    ssid = 0
    w1 = s.split('-')    

    call = w1[0]
    
    while len(call) < 6:
        call += ' '
        
    r = ''
    
    for p in call:
        r += chr(ord(p) << 1)        
    
    if len(w1) != 1:
        try:
            ssid = int(w1[1])
        except ValueError:
            return ''
        
    ct = (ssid << 1) | 0x60

    if digi:
        ct |= 0x80
    
    return r + chr(ct)


def raw2kiss(raw):
    """
        Escapes special characters to make them binary transparent
    """    

    # FESC
    kiss = raw.replace(FESC, FESC + TFESC)

    # FEND
    kiss = kiss.replace(FEND, FESC + TFEND)

    return kiss

def kiss2raw(kiss):
    """
        Removes inserted escape characters
    """
    
    #FESC
    raw = kiss.replace(FESC + TFESC, FESC)

    #FEND
    raw = raw.replace(FESC + TFEND,  FEND)

    return raw


#Receiving
def parse_raw_msg(raw):
    """
        Parses the raw AX25 message and returns a tuple
        containing source, destination, data and any digipeaters
    """
    
    # Is it too short?
    if len(raw) < 16:
        return None

    i = 0
    for i in range(0, len(raw)):
        if ord(raw[i]) & 0x01:
            break
    
    # Is address field length correct?        
    if (i + 1) % 7 != 0:
        return None
                            
    
    n = (i + 1) / 7
    
    # Less than 2 callsigns?
    if n < 2 or n > 10:
        return None
        
    try:
        if ((i + 1) % 7 == 0 and n >= 2 
                             and ord(raw[i + 1]) & 0x03 == 0x03 
                             and ord(raw[i + 2]) == 0xf0):
            strinfo = raw[i + 3:]
            
            if len(strinfo) != 0:
                strto = callsign_decode(raw) 

                if strto == '':
                    return None
                             
                strfrom = callsign_decode(raw[7:])

                if strfrom == '':
                    return None
                    
                if is_invalid_call(strfrom):
                    return None

                digis = []
                for i in range(2, n):
                    s = callsign_decode(raw[i * 7:])
                    
                    if s == '':
                        return None
                        
                    digis.append(s)

                return (strfrom, strto, strinfo, digis)
    
    except IndexError:
        pass

    return None
    

def callsign_decode(rawcall):
    """
        Decodes the AX25 encoded callsign
    """

    s = ''
    
    for i in range(0, 6):
        ch = chr(ord(rawcall[i]) >> 1)
        
        if ch == ' ':
            break
            
        s += ch
                                    
    ssid = (ord(rawcall[6]) >> 1) & 0x0f
      
    if s.isalnum() == False:
        return ''
        		   
    if ssid > 0:            
        s += "-%d" % (ssid)

    return s     


def is_invalid_call(s):
    """
        Checks if a callsign is valid
    """

    w = s.split('-')

    if len(w) > 2:
        return True

    if len(w[0]) < 1 or len(w[0]) > 6:
        return True

    for p in w[0]:
        if not (p.isalpha() or p.isdigit()):
            return True        
        
    if w[0].isalpha() or w[0].isdigit():
        return True 
        
    if len(w) == 2:
        try:        
            ssid = int(w[1]) 
                
            if ssid < 0 or ssid > 15:
                return True
                        
        except ValueError:
            return True
            
    return False        


