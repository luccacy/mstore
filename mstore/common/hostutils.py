import os
import sys

def get_hosts():

    host_conf_file = '/etc/hosts'
    host_list = []

    with open(host_conf_file, 'r') as fp:
        while True:
            line = fp.readline()
            if not line:
                break

            #print("line : \n%s" % line)
            if line.find(' ') > 0:
                pl = line.split(' ')
            elif line.find('\t') > 0:
                pl = line.split('\t')

            params = list(set(pl))
            params.sort(key = pl.index)
            for item in params:
                if item == '' or len(item) == 0:
                    params.remove(item)

            if len(params) == 2 :
                host_dict = {}
                host_dict[params[0]] = params[1][:-1]
                host_list.append(host_dict)

    return host_list
