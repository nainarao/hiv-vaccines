from rwslib import RWSConnection
from rwslib.rws_requests import MetadataStudiesRequest
from rwslib.rws_requests import VersionRequest, DiagnosticsRequest,  ClinicalStudiesRequest


app_id = '635r8aib-21e9-6b5f-867e-bk2358ub2784'
key = open('keypair_dir/vaccines_mauth.priv.key','r').read()

#rws = RWSConnection('innovate', "nrao1","H4Vaccine!")
rws = RWSConnection('scharp', "nrao1","H4Vaccine!")


#rws.send_request(MetadataStudiesRequest())


print rws.send_request(VersionRequest())
print "url: ", rws.last_result.url
print "Status code: ", rws.last_result.status_code
print "diagnostics: ", rws.send_request(DiagnosticsRequest())

studies = rws.send_request(ClinicalStudiesRequest())
print studies.ODMVersion
print studies.creationdatetime
print "num studies: ", len(studies)

for study in studies:
    print "OID",study.oid
    print "Name",study.studyname
    print "protocolname",study.protocolname
    print "IsProd?",study.isProd()
