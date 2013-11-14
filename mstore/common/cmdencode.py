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
        

def format_command_str(cmd, addr=None):
    
    CR = 0x0d
    LF = 0x0a
    send_flag = 0x3a
    cmd_str = ''
    
    addr_high,addr_low = split_hex(addr)
    
    if cmd == 'sample1':
#         sample1_code = 0x61
#         sample1_high = 0x36
#         sample1_low = 0x31
        
        sample1_code = 0x46
        sample1_high = 0x34
        sample1_low = 0x36
        
        sum = addr + sample1_code#0x61
        
        lrc = (((~sum) + 1) & 0xFF)
        lrc_high,lrc_low = split_hex(lrc)
        
        cmd_code = (send_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)      
        cmd_str = ''.join([chr(x) for x in cmd_code])
        
    elif cmd == 'sample2':
        
        sample1_code = 0x62
        sample1_high = 0x36
        sample1_low = 0x32
        
        sum = addr + sample1_code#0x61
        
        lrc = (((~sum) + 1) & 0xFF)
        lrc_high,lrc_low = split_hex(lrc)
        
        cmd_code = (send_flag, addr_high, addr_low, sample1_high, sample1_low, lrc_high, lrc_low, CR, LF)      
        cmd_str = ''.join([chr(x) for x in cmd_code])
        
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
    
    print('cmd_str : %s' % (cmd_str))
    
    return cmd_str



cmd_str = format_command_str('sample1', addr=0x03)




