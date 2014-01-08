import http
import json

#glance api

endpoint = 'http://10.12.13.16:7878'
kwargs = {'ssl_compression': True, 'cert_file': None,
        'token':'8ba9eb7c22934f26bd21ee77e4b86a3c', 'timeout': 600, 'cacert': '', 'key_file': None, 'insecure': False}
client = http.HTTPClient(endpoint, **kwargs)

#restore
'''
url = "/v1/images/01ffdbc2-5a64-44ab-8cf6-0a1a0a196a70/restore"
body = {"location" : "/var/lib/glance/backups", "name": "back0"}
resp, body = client.json_request('POST', url, body=body)
print resp
print body
'''

#backup
'''
url = "/v1/images/01ffdbc2-5a64-44ab-8cf6-0a1a0a196a70/backup"
body = {"location" : "/var/lib/glance/backups", "name": "back0"}
resp, body = client.json_request('POST', url, body=body)
print resp
print body
'''
#unbackup
'''
url = "/v1/images/84ecae2a-e113-46d3-b4b7-a8bae33f0be7/unbackup"
body = {"location" : "/var/lib/glance/backups", "name": "back0"}
resp, body = client.json_request('POST', url, body=body)
print resp
print body
'''

#metadata api test
'''
url = "/v1/images/metadata"
body = {"image_meta":
        {"status":
            "active", "name": "cir", "container_format": "ovf", "disk_format":
            "qcow2", "protected": False, "is_public":  True, "checksum":
            "8abc2460f14e009d13d9861f10f5efac", "size": 11141121}}
resp, body = client.json_request('POST', url, body=body)
print resp
print body
'''

#test for get data
url = "1/2/3/4"
resp, body = client.raw_request('GET', url)
print resp
print body

file = 'new.py'
image = open(file, 'wb')
for chunk in body:
    image.write(chunk)
image.close()


#download image 
'''
url = "/v2/images/17910877-f1ce-4b91-a303-b6bdc2da64b5/file"
resp, body = client.raw_request('GET', url)

file = 'test.img'
image = open(file, 'wb')
for chunk in body:
    image.write(chunk)
image.close()
'''

#upload image
'''
headers={}
headers['Transfer-Encoding']='chunked'
url="1/2/test1/cirros.img"

with open('cirros.img', 'rb') as image_file:
    resp,body=client.raw_request('POST',url, headers=headers, body=image_file)
#print resp
#print body
file = 'resp.img'
image = open(file, 'wb')
for chunk in body:
    image.write(chunk)
image.close()
'''
#upload image
'''
headers={}
headers['Accept-Encoding']='identity'
headers['Transfer-Encoding']='chunked'
headers['x-image-meta-container_format']='ovf'
headers['x-image-meta-protected']=False
headers['x-image-meta-min_disk']=0
headers['x-image-meta-size']=23872
headers['x-image-meta-is_public']=True
headers['x-image-meta-min_ram']=0
headers['X-Auth-Token']='8ba9eb7c22934f26bd21ee77e4b86a3c'
headers['x-image-meta-disk_format']='raw'
headers['x-image-meta-name']='new_client'
url = "v2vs"
with open('readme', 'rb') as image_file:
    resp,body=client.raw_request('POST',url, headers=headers, body=image_file)
print resp
print body
'''
