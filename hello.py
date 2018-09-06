from rwslib import RWSConnection
from rwslib.rws_requests import MetadataStudiesRequest, VersionRequest, DiagnosticsRequest, ClinicalStudiesRequest, StudySubjectsRequest


app_id = '635r8aib-21e9-6b5f-867e-bk2358ub2784'
key = open('keypair_dir/vaccines_mauth.priv.key','r').read()

rws = RWSConnection('https://innovate.mdsol.com', "nrao1","H4Vaccine!")


#rws.send_request(MetadataStudiesRequest())

print rws.send_request(VersionRequest())
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

subject_list = rws.send_request(StudySubjectsRequest("Mediflex", "Dev"))
for subject in subject_list:
    print "Name: %s" % subject.subjectkey
