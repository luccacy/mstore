'''
Created on 2013-9-12

@author: zhouyu
'''
'''
Created on 2013-9-12

@author: zhouyu
'''
def split_hex(num):
    
    if num < 0:
        raise
    else:
        high = (num/16 + 0x30) if (num/16 < 10) else (num/16%9 + 0x40)
        low = (num%16 + 0x30) if (num%16 < 10) else (num%16%9 + 0x40)
        return high,low
        

def encode_cmd(cmd, addr=None):
    
    CR = 0x0d
    LF = 0x0a
    send_flag = 0x3a
    recv_flag = 0x21
    cmd_str = ''
    recv_str = ''
    
    
    addr_high,addr_low = split_hex(addr)
    
    if cmd == 'sample1':
        sample1_code = 0x61
        sample1_high = 0x36
        sample1_low = 0x31
        
#         sample1_code = 0x46
#         sample1_high = 0x34
#         sample1_low = 0x36
        
        sum = addr + sample1_code#0x61
        
        lrc = (((~sum) + 1) & 0xFF)
        lrc_high,lrc_low = split_hex(lrc)
        
        cmd_code = (send_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)
        recv_code = (recv_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)      
        cmd_str = ''.join([chr(x) for x in cmd_code])
        recv_str = ''.join([chr(x) for x in recv_code])
        
    elif cmd == 'sample2':
        
        sample1_code = 0x62
        sample1_high = 0x36
        sample1_low = 0x32
        
        sum = addr + sample1_code#0x61
        
        lrc = (((~sum) + 1) & 0xFF)
        lrc_high,lrc_low = split_hex(lrc)
        
        cmd_code = (send_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)      
        recv_code = (recv_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)      
        cmd_str = ''.join([chr(x) for x in cmd_code])
        recv_str = ''.join([chr(x) for x in recv_code])
        
    elif cmd == 'transport':
        
        sample1_code = 0x63
        sample1_high = 0x36
        sample1_low = 0x33
        
        sum = addr + sample1_code#0x61
        
        lrc = (((~sum) + 1) & 0xFF)
        lrc_high,lrc_low = split_hex(lrc)
        
        cmd_code = (send_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)      
              
        cmd_str = ''.join([chr(x) for x in cmd_code])
        
        
    elif cmd == 'ext_life':
        sample1_code = 0x64
        sample1_high = 0x36
        sample1_low = 0x34
        
        sum = addr + sample1_code#0x61
        
        lrc = (((~sum) + 1) & 0xFF)
        lrc_high,lrc_low = split_hex(lrc)
        
        cmd_code = (send_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)      
              
        cmd_str = ''.join([chr(x) for x in cmd_code])
            
    else:
        raise
    
    return cmd_str, recv_str

def convert_to_decimal(data_str):
    if len(data_str) != 4:
        return 
    
    high = data_str[0:2]
    low = data_str[2:4]
    
    value = int(high, 16)*256 + int(low, 16)
    return value
     

#cmd_str = encode_cmd('sample1', addr=0x03)
'''get all values except temperature'''
def get_common_values(data):
    '''1'''
    addr = -1 
    '''2'''
    elec = -1
    '''16'''
    inners = []
    '''16'''
    volts = []
    '''16'''
    hinners = []
    '''8 option'''
    temps = []
    '''1'''
    lrc = -1
    
    if len(data) < 104:
        raise
    else:
        '''addr : 1 byte'''
        addr = int(data[0:2], 16)
        
        '''elec : 2 byte '''
        '''AAA'''
        elec_str = data[2:6]
        if 'xx' not in elec_str:
            elec = convert_to_decimal(elec_str) * 0.1
        else:
            elec = -1
        
        '''inner : 16 bytes'''
        start = 6
        inner_strs = []
        
        for i in range(8):
            inner_strs.append( data[start:start+4] )
            start += 4
        
        '''mmm'''
        for inner_str in inner_strs:
            
            if 'xx' not in inner_str:
                inner_hex = convert_to_decimal(inner_str) * 0.001
            else:
                inner_hex = -1
            inners.append(inner_hex)
        
        '''voltage : 16 bytes'''
        start = 38
        volt_strs = []
        
        for i in range(8):
            volt_strs.append( data[start:start+4] )
            start += 4
        
        '''VVV'''
        for volt_str in volt_strs:
            
            if 'xx' not in volt_str:
                volt_hex = convert_to_decimal(volt_str) * 0.001
            else:
                volt_hex = -1
            volts.append(volt_hex)
            
        '''hinner: 16 bytes'''
        start = 70
        hinner_strs = []
        for i in range(8):
            hinner_strs.append( data[start:start+4] )
            start += 4
        
        '''mmm'''
        for hinner_str in hinner_strs:
            
            if 'xx' not in hinner_str:
                hinner_hex = convert_to_decimal(hinner_str) * 0.001
            else:
                hinner_hex = -1
            hinners.append(hinner_hex)
                   
        '''lrc : 1 bytes'''

        lrc = int(data[-2:],16)
        
    return addr,elec,inners,volts,hinners,lrc
 
    '''9 bytes : !0346B7\t\n 
       55 bytes : !data\t\n
       63 bytes : !data\t\n'''    
def decode_result(input_data):
    '''1'''
    addr = -1 
    '''2'''
    elec = -1
    '''16'''
    inners = []
    '''16'''
    volts = []
    '''16'''
    hinners = []
    '''8 option'''
    temps = []
    '''1'''
    lrc = -1
    
    status = -1
    
    result = {}
    
    print('input_data : %s, len : %d' % (input_data, len(input_data)))
    if len(input_data) < 9:
        status = -1
        result['status'] = status  
        result['data'] =  '-1' 
        return result
         
    data = input_data[1:-2]
    
    if len(data) == 6:  
        result['status'] = status
        result['data'] =  input_data 
        return result
    
    elif len(data) == 104:
            
        addr, elec, inners, volts, hinners, lrc =  get_common_values(data)
        
    elif len(data) == 120:
        '''temprature : 8 bytes'''
        start = 102
        temp_strs = []
        for i in range(8):
            temp_strs.append( data[start:start+2] )
            start += 2
            
        for temp_str in temp_strs:
            if 'xx' not in temp_str:
                temp_hex = int(temp_str, 16) * 0.2
            else:
                tempr_hex = -1
            temps.append(temp_hex)
        addr, elec, inners, volts, hinners,lrc= get_common_values(data)
        
    else:
        raise
    
    status = 0
    result['addr'] = addr
    result['elec'] = elec
    result['inners'] = inners
    result['volts'] = volts
    result['hinners'] = hinners
    result['temps'] = temps
    result['lrc'] = lrc
    result['status'] = status
    result['data'] =  '0' 

    
    return result
    
    
# cmd_str, recv_str = encode_cmd('sample1', 3)
# print cmd_str
# print hex(ord(cmd_str[4]))
# print recv_str
'''    
result = '03xxxx3B383AB23B113B5E3B383B\
11xxxxxxxx0F440F570F390F3F0F\
530F57xxxxxxxx003AD83AC53B4B\
3AEB3A8C3Axxxxxxxx27'


addr, elec, inners, volts, hinners, lrc = decode_result(result)
print('addr: %x' % addr)
print('elec: %x' % elec)
for inner in inners:
    print('inner: %x' % inner)
for volt in volts:
    print('volt: %x' % volt)
for hinner in hinners:
    print('hinner : %x' % hinner)
print('lrc : %x' % lrc)


ids = '1,2,3,4,5,7'
idlist = ids.split(',')
for id in idlist:
    print id

test_str = '!12345\t\n'
print test_str
print test_str[1:-2]
'''


