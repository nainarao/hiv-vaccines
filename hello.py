from rwslib import RWSConnection
from rwslib.builders import *
from rwslib.rws_requests import MetadataStudiesRequest, VersionRequest, DiagnosticsRequest, ClinicalStudiesRequest, StudySubjectsRequest, StudyDatasetRequest, SubjectDatasetRequest, PostDataRequest
import xml.dom.minidom
import os
import re
import glob
from xml.dom import minidom
from time import strftime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

project_name = "Mediflex"
enviro_name = "DEV"
location_oid = "BWH0001"
study_name = project_name + " " + enviro_name
ET.register_namespace("", "http://www.cdisc.org/ns/odm/v1.3")

def testConnection():
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

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8', method="xml")
    reparsed = minidom.parseString(rough_string)
    print reparsed.toprettyxml(indent=" ")

def printDataset():
    clinical_xml = rws.send_request(StudyDatasetRequest('Mediflex', 'DEV')).encode('utf-8').strip()
    formatted_xml = clinical_xml[clinical_xml.find('<'):]

    tree = ET.fromstring(formatted_xml)
    print "All Subjects Tree: \n", tree
    prettify(tree)

def printSubjectData(pt_key):
    pt_xml = rws.send_request(SubjectDatasetRequest(project_name, enviro_name, pt_key)).encode('utf-8').strip()
    pt_xml =pt_xml[pt_xml.find('<'):]

    tree = ET.fromstring(pt_xml)
    print "Patient Tree: \n", tree
    prettify(tree)

def printAllSubjects():
    subject_list = rws.send_request(StudySubjectsRequest(project_name, enviro_name))
    print "Subjects in Study: "
    for subject in subject_list:
        print "Name: %s (%s)" % (subject.subject_name, subject.subjectkey)

def addNewSubject(sub_initals, sub_id):
    print "add new subject original"
    odm = ODM("test system")(
        ClinicalData(project_name, enviro_name)(
            SubjectData(location_oid,"New Subject", "Insert")(
                StudyEventData("Subject")(
                    FormData("EN", transaction_type="Update")(
                        ItemGroupData()(
                            ItemData("SUBJID",sub_id),
                            ItemData("SUBJINIT",sub_initals)
                        )
                    )
                )
            )
        )
    )
    print(str(odm))
    resp = rws.send_request(PostDataRequest(str(odm)))
    print "Addition Successful: ", resp.istransactionsuccessful
    print "Fields Changed: \n", str(resp)

def addNewSubject1():
    print "add new subject1"
    data = """<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" ODMVersion="1.3" FileType="Transactional" FileOID="Example-1" CreationDateTime="2008-01-01T00:00:00"> <ClinicalData StudyOID="Mediflex (Dev)" MetaDataVersionOID="1"><SubjectData SubjectKey="123 ABC" TransactionType="Insert"><SiteRef LocationOID="BWH0001"/></SubjectData></ClinicalData></ODM>"""
    # data = """<?xml version="1.0" encoding="utf-8" ?><ODM CreationDateTime="2013-06-17T17:03:29" FileOID="3b9fea8b-e825-4e5f-bdc8-1464bdd7a664" FileType="Transactional" ODMVersion="1.3" Originator="test system" xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"><ClinicalData MetaDataVersionOID="1" StudyOID="Mediflex (Dev)"> <SubjectData SubjectKey="New Subject" TransactionType="Insert"> <SiteRef LocationOID="MDSOL" /> <StudyEventData StudyEventOID="SUBJECT"> <FormData FormOID="EN" FormRepeatKey="1" TransactionType="Update"> <ItemGroupData ItemGroupOID="EN" mdsol:Submission="SpecifiedItemsOnly"> <ItemData ItemOID="SUBJID" Value="1" /> <ItemData ItemOID="SUBJINIT" Value="AAA" /> </ItemGroupData> </FormData> </StudyEventData> </SubjectData> </ClinicalData> </ODM>"""
    print data
    resp = rws.send_request(PostDataRequest(data))
    print "Addition Successful: ", resp.istransactionsuccessful
    print "Fields Changed: \n", str(resp)

def makeODM():
    print "make ODM: "
    # Make a root ODM element with originator system
    odm = ODM("test system")

    # Study and environment
    clinical_data = ClinicalData("Mediflex", "DEV")

    # Subject Site, Subject Name and the transaction type
    subject_data = SubjectData("MDSOL", "New Subject", "Insert")

    # The special "SUBJECT" event represents subject-level forms
    event_data = StudyEventData("SUBJECT")

    # We want to update this form that will be created automatically when subject created
    form_data = FormData("EN", transaction_type="Update")

    # We need an ItemGroupData element
    itemgroup = ItemGroupData()

    # Push itemdata elements into the itemgroup
    itemgroup << ItemData("SUBJINIT","AAA")
    itemgroup << ItemData("SUBJID",001)

    # Now we put it all together
    odm << clinical_data << subject_data << event_data << form_data << itemgroup

    # Get an lxml document from the ODM object for further manipulation
    root = odm.getroot()

    # Print a string representation of the ODM document
    print(str(odm))

app_id = '635r8aib-21e9-6b5f-867e-bk2358ub2784'
key = open('keypair_dir/vaccines_mauth.priv.key','r').read()

rws = RWSConnection('https://innovate.mdsol.com', "nrao1","H4Vaccine!")

#testConnection()
#printSubjectData("123")
printAllSubjects()
# addNewSubject("ABC", 003)
addNewSubject1()
printAllSubjects()

#printDataset()
#printSubjectData('1')
