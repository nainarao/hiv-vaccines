from rwslib import RWSConnection
from rwslib.rws_requests import MetadataStudiesRequest
from rwslib.rws_requests import VersionRequest


app_id = '635r8aib-21e9-6b5f-867e-bk2358ub2784'
key = open('keypair_dir/vaccines_mauth.priv.key','r').read()

rws = RWSConnection('https://innovate.mdsol.com', "nrao1","Resolved99!")


#rws.send_request(MetadataStudiesRequest())

print rws.send_request(VersionRequest())
