__author__ = 'naina'

from flask import Flask, render_template, request
import sys
from rwslib import RWSConnection
from rwslib.builders import *
from rwslib.rws_requests import MetadataStudiesRequest, VersionRequest, DiagnosticsRequest, ClinicalStudiesRequest, StudySubjectsRequest, StudyDatasetRequest, SubjectDatasetRequest, PostDataRequest
from rwslib.rwsobjects import *
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

def initialize_medidata():

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
    #print reparsed.toprettyxml(indent=" ")
    return reparsed.toprettyxml(indent=" ")

def printDataset():
    clinical_xml = rws.send_request(StudyDatasetRequest('Mediflex', 'DEV')).encode('utf-8').strip()
    formatted_xml = clinical_xml[clinical_xml.find('<'):]

    tree = ET.fromstring(formatted_xml)
    print "All Subjects Tree: \n", tree
    prettify(tree)

def printPatient(pt_key):
    pt_xml = rws.send_request(SubjectDatasetRequest(project_name, enviro_name, pt_key)).encode('utf-8').strip()
    pt_xml = pt_xml[pt_xml.find('<'):]
    pt_xml = pt_xml.replace("http://www.cdisc.org/ns/odm/v1.3", "")
    tree = ET.fromstring(pt_xml)
    for child in tree.iter("ItemData"):
        subj = child.get('ItemOID')
        if '.' in subj:
            subj = subj[subj.find('.')+1:]
        if '_' in subj:
            subj = subj[subj.rfind('_')+1 :]
        child.set('ItemOID', subj)
    items = tree.iter("ItemData")
    return items
    #return prettify(tree)

def printSubjectData(pt_key):
    pt_xml = rws.send_request(SubjectDatasetRequest(project_name, enviro_name, pt_key)).encode('utf-8').strip()
    pt_xml =pt_xml[pt_xml.find('<'):]
    #print pt_xml
    pt_xml = pt_xml.replace("http://www.cdisc.org/ns/odm/v1.3", "")

    tree = ET.fromstring(pt_xml)
    print tree.tag
    #print "Patient Tree: \n", tree
    #print tree.getroot().iter('ItemData')
    for child in tree.iter('ItemData'):
        print child.attrib
        for key, val in child.attrib.items():
            print val
    #print prettify(tree)
    return tree


def printAllSubjects():
    subject_list = rws.send_request(StudySubjectsRequest(project_name, enviro_name))
    print "Subjects in Study: "
    for subject in subject_list:
        #print "Name: %s (%s)" % (subject.subjectname, subject.subjectkey)
        print "Name: %s" % (subject.subjectkey)

def addNewSubject(sub_key, sub_id, sub_init):
    print "add new subject original"
    odm = ODM("test system")(
        ClinicalData(project_name, enviro_name)(
            SubjectData(site_location_oid=location_oid, subject_key=sub_key, transaction_type="Insert")(
                StudyEventData("SUBJECT")(
                    FormData("EN", transaction_type="Update")(
                        ItemGroupData()(
                            ItemData("SUBJID",sub_key),
                            ItemData("SUBJINIT",sub_init),
                            ItemData("USUBJID", sub_id)
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

def removeSubject(subjectID):
    data = """<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" ODMVersion="1.3" FileType="Transactional" FileOID="Example-1" CreationDateTime="2008-01-01T00:00:00"> <ClinicalData StudyOID="Mediflex (Dev)" MetaDataVersionOID="1"><SubjectData SubjectKey=\""""+subjectID +"""" TransactionType="Remove"><SiteRef LocationOID="BWH0001"/></SubjectData></ClinicalData></ODM>"""
    print data
    resp = rws.send_request(PostDataRequest(data))
    print "Addition Successful: ", resp.istransactionsuccessful

def addNewSubject1():
    print "add new subject1"

    data = """<?xml version="1.0" encoding="utf-8" ?>
    <ODM CreationDateTime="2013-06-17T17:03:29" FileOID="3b9fea8b-e825-4e5f-bdc8-1464bdd7a664"
         FileType="Transactional" ODMVersion="1.3"
         Originator="test system"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
      <ClinicalData MetaDataVersionOID="1" StudyOID="Mediflex (DEV)">
        <SubjectData SubjectKey="ABC" TransactionType="Update">
          <SiteRef LocationOID="BWH0001" />
          <StudyEventData StudyEventOID="SUBJECT">
            <FormData FormOID="EN" FormRepeatKey="1" TransactionType="Update">
              <ItemGroupData ItemGroupOID="EN" mdsol:Submission="SpecifiedItemsOnly">
                <ItemData ItemOID="SUBJID" Value="ABC"/>
                <ItemData ItemOID="SUBJINIT" Value="123ABC" />
                <ItemData ItemOID="EN.USUBJID" Value="abc"/>
              </ItemGroupData>
            </FormData>
          </StudyEventData>
        </SubjectData>
      </ClinicalData>
    </ODM>"""

    print data
    resp = rws.send_request(PostDataRequest(data))
    print "Addition Successful: ", resp.istransactionsuccessful
    print "Fields Changed: \n", str(resp)

def updateSubjectDiary(sub_id):

    data = """<?xml version="1.0" encoding="utf-8" ?> <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" ODMVersion="1.3" FileType="Transactional" FileOID="Example-7" CreationDateTime="2008-01-01T00:00:00">
 <ClinicalData StudyOID="Mediflex(Dev)" MetaDataVersionOID="1">
   <SubjectData SubjectKey=\""""+sub_id +"""" TransactionType="Update">
     <SiteRef LocationOID="BWH0001"/>
     <StudyEventData StudyEventOID="VISIT01">
       <FormData FormOID="FORM_PAIN_SI">
         <ItemGroupData ItemGroupOID="FORM_PAIN_SI_LOG_LINE" ItemGroupRepeatKey="1">
           <ItemData ItemOID="IT_DATE" Value="20 Sep 2001"/>
           <ItemData ItemOID="IT_TIME" Value="12:00:00"/>
           <ItemData ItemOID="IT_SEVERE" Value="50"/>
           <ItemData ItemOID="IT_REC_ID" Value="12345678"/>
         </ItemGroupData>
       </FormData>
     </StudyEventData>
     <StudyEventData StudyEventOID="VISIT02">
       <FormData FormOID="FORM_PAIN_SI">
         <ItemGroupData ItemGroupOID="FORM_PAIN_SI_LOG_LINE" ItemGroupRepeatKey="1">
           <ItemData ItemOID="IT_DATE" Value="45 Feb 2011"/>
           <ItemData ItemOID="IT_TIME" Value="18:00:00"/>
           <ItemData ItemOID="IT_SEVERE" Value="75"/>
           <ItemData ItemOID="IT_REC_ID" Value="12345679"/>
         </ItemGroupData>
       </FormData>
     </StudyEventData>
   </SubjectData>
 </ClinicalData>
</ODM>"""
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
    subject_data = SubjectData(site_location_oid=location_oid, subject_key="xyz", transaction_type="Insert")

    # The special "SUBJECT" event represents subject-level forms
    event_data = StudyEventData("SUBJECT")

    # We want to update this form that will be created automatically when subject created
    form_data = FormData("EN", transaction_type="Update")

    # We need an ItemGroupData element
    itemgroup = ItemGroupData()

    # Push itemdata elements into the itemgroup
    itemgroup << ItemData("SUBJINIT","AAA")
    #itemgroup << ItemData("SUBJID",001)
    itemgroup << ItemData("USUBJID", "xxx")

    # Now we put it all together
    odm << clinical_data << subject_data << event_data << form_data << itemgroup

    # Get an lxml document from the ODM object for further manipulation
    root = odm.getroot()

    # Print a string representation of the ODM document
    print(str(odm))
    resp = rws.send_request(PostDataRequest(str(odm)))
    print "Addition Successful: ", resp.istransactionsuccessful
    print "Fields Changed: \n", str(resp)

app_id = '635r8aib-21e9-6b5f-867e-bk2358ub2784'
key = open('keypair_dir/vaccines_mauth.priv.key','r').read()

rws = RWSConnection('https://innovate.mdsol.com', "nrao1","H4Vaccine!")

#initialize_medidata()
#testConnection()
#printSubjectData("123")


if len(sys.argv) > 1:
    #updateSubjectDiary(sys.argv[1])
    printSubjectData(sys.argv[1])
    #removeSubject(sys.argv[1])
#printAllSubjects()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello', methods=['POST'])
def hello():
    initialize_medidata()
    first_name = request.form['first_name']
    sub_xml = printPatient(first_name)
    print sub_xml
    #sub_xml = sub_xml.replace("\"", "\\""s")
    return render_template('displaydiary.html', root=sub_xml)
    #return 'Hello have fun learning python <br/> <xmp> %s </xmp> <a href="/">Back Home</a>' % (str(sub_xml))
