import client

#test_client = client.HTTPClient('127.0.0.1','8888')
test_client = client.HTTPClient()
test_client.set_management_url('http://10.12.13.11:9898')

#create fixed ip
'''
body = {"network_uuid" : "9aaefa42-db20-4cec-92b6-40d6ba9ebb39"}
resp,body=test_client.post("/v2/bd57dcc44a3c4e809b312ec757622583/os-fixed-ips", body=body)
print("%s" % resp)
print("%s" % body)
'''

#list float ip pools
'''
resp,body=test_client.get("/v2/bd57dcc44a3c4e809b312ec757622583/os-floating-ip-pools")
print("%s" % resp)
print("%s" % body)
'''

#alloc ip pools
'''
body = {"pool" : "p1"}
resp,body=test_client.post("/v2/a74e49362968459cb4f51bdb4bc3c2f9/os-floating-ip-pools",body=body)
print("%s" % resp)
print("%s" % body)
'''
#create ip bulk
'''
body = {"floating_ips_bulk_create": {"interface": "eth1", "ip_start":
    "10.12.13.100","ip_end":"10.12.13.110", "pool": "out"}}
resp,body =test_client.post("/v2/bd57dcc44a3c4e809b312ec757622583/os-floating-ips-bulk", body=body)
print("%s" % resp)
print("%s" % body)
'''

#delete bulk
'''
body = {"floating_ips_bulk_delete": {"ip_start":
    "10.12.13.100","ip_end":"10.12.13.110"}}
resp,body=test_client.put("/v2/bd57dcc44a3c4e809b312ec757622583/os-floating-ips-bulk/delete", body=body)
print("%s" % resp)
print("%s" % body)
'''

#best
'''
body = {"best" : None} 
vm_id = 'dd512ec4-f917-401e-a715-d3e97c09dc7b' 
resp,body=test_client.post("/v2/bd57dcc44a3c4e809b312ec757622583/servers/%s/action" % vm_id,body=body)
print("%s" % resp)
print("%s" % body)
'''
#clone

body = {"clone" : {"location": "", "name":"back1"}} 
vm_id = '030a018f-1642-4cd6-9a4e-9697cd3033ca' 
resp,body=test_client.post("/v2/9565a75896b44f7d8439d187bc6be52e/servers/%s/action" % vm_id,body=body)
print("%s" % resp)
print("%s" % body)

#recovery
'''
body = {"recovery" : {"location": "", "name":"back1"}} 
vm_id = 'e10e3312-4649-40d1-a4b0-9af7e07b98be' 
resp,body=test_client.post("/v2/bd57dcc44a3c4e809b312ec757622583/servers/%s/action" % vm_id,body=body)
print("%s" % resp)
print("%s" % body)
'''

#unclone
'''
body = {"unclone" : {"location": "", "name":"back1"}} 
vm_id = '23fe0f17-27f6-4f46-b456-6ce20007ddba' 
resp,body=test_client.post("/v2/bd57dcc44a3c4e809b312ec757622583/servers/%s/action" % vm_id,body=body)
print("%s" % resp)
print("%s" % body)
'''

#list vm
'''
resp, body=test_client.get("/servers/detail")
print("%s" % resp)
print("%s" % body)

#create secgroup
body={"security_group": {"name": "test_group", 'description': 'dest'}}
resp,body=test_client.post("/os-security-groups", body=body)
print("%s" % resp)
print("%s" % body)
#delete secgroup
resp,body=test_client.delete("/os-security-groups/4")
print("%s" % resp)
print("%s" % body)
#list secgroup
resp,body=test_client.get("/os-security-groups")
print("%s" % resp)
print("%s" % body)

#update quota
body={'quota_set':{'instances': '15'}}
resp,body=test_client.put("/os-quota-sets/%s" % 'admin', body=body)
'''
