#!/usr/bin/env python
import argparse
import getpass
import yaml
import json
import requests
import sys
import pandoc

R4J_PATH = '/rest/com.easesolutions.jira.plugins.requirements/2.0'
# INSERTION_POINT_STYLE = 'Insertion Point'
# REQUIREMENTS_TAG = '<Requirements>'
JIRA_PATH = '/rest/api/latest'

# Style
TABLE_STYLE = 'Requirement_list'
REQ_TITLE_STYLE = 'Requirement Title'
REQ_STYLE = 'Requirement'


TEST = False
MDCONVERT = False

# Tools for exporting R4J requirements in word doc

def log(*args):
    print(*args, file=sys.stderr)

class JiraSearch(object):
    """ This factory will create the actual method used to fetch issues from JIRA. This is really just a closure that
        saves us having to pass a bunch of parameters all over the place all the time. """

    __base_url = None

    def __init__(self, url, auth, no_verify_ssl):
        self.__base_url = url
        self.url = url
        self.auth = auth

        self.no_verify_ssl = no_verify_ssl
        #self.fields = ','.join(['key', 'summary', 'status', 'description', 'issuetype', 'issuelinks', 'subtasks','updated'])
        self.fields = ','.join(['key', 'summary', 'description', 'updated'])

    def get(self, uri, params={}):
        headers = {'Content-Type' : 'application/json'}
        url = self.url + uri

        if isinstance(self.auth, str):
            return requests.get(url, params=params, cookies={'JSESSIONID': self.auth}, headers=headers, verify=self.no_verify_ssl)
        else:
            return requests.get(url, params=params, auth=self.auth, headers=headers, verify=(not self.no_verify_ssl))

    def get_issue(self, key):
        """ Given an issue key (i.e. JRA-9) return the JSON representation of it. This is the only place where we deal
            with JIRA's REST API. """
        log('Fetching ' + key)
        # we need to expand subtasks and links since that's what we care about here.
        response = self.get(f'{JIRA_PATH}/issue/{key}', params={'fields': self.fields})
        # Line updated for getting renderedFields (like description) in html and convert in md 
        # response = self.get(f'{JIRA_PATH}/issue/{key}', params={'fields': self.fields, 'expand':'renderedFields'})
        response.raise_for_status()
        return response.json()

    def query(self, query):
        log('Querying ' + query)
        response = self.get(f'{JIRA_PATH}/search', params={'jql': query, 'fields': self.fields})
        content = response.json()
        return content['issues']

    def list_ids(self, query):
        log('Querying ' + query)
        response = self.get(f'{JIRA_PATH}/search', params={'jql': query, 'fields': 'key', 'maxResults': 500})
        return [issue["key"] for issue in response.json()["issues"]]

    def get_issue_uri(self, issue_key):
        return self.__base_url + '/browse/' + issue_key
    
    def get_requirements_tree(self, projkey):
        if TEST:
            with open('reqSampleFolders.json') as testfile:
                return json.load(testfile)
        else:
            response = self.get(f'{R4J_PATH}/projects/{projkey}/folders', params={'plugin':'r4j'})
            return response.json()

    def get_requirements_folder(self, projkey, folderid):
        response  = self.get(f'{R4J_PATH}/projects/{projkey}/folders/{folderid}', params={'plugin':'r4j'})
        return response.json()

    def get_requirement(self, reqKey):
        return self.get_issue(reqKey)

def parse_args():
    parser = argparse.ArgumentParser(description='programm_description')
    parser.add_argument('-c, --config', dest='config', default='config.yaml', help='Configuration file. By default config.yaml file is used')
    parser.add_argument('-u', '--user', dest='user', default=None, help='Username to access JIRA. If not provided, it will have to be entered in terminal.')
    parser.add_argument('-p', '--password', dest='password', default=None, help='Password to access JIRA. If not provided, it will have to be entered in the terminal.')
    parser.add_argument('-o', '--output', dest='output',default=None, help='Output file name location to store yaml exported content. This will override value define in configuration file')
    return parser.parse_args()


def convertJira2Markdown(jira_text) -> str:
    return pandoc.write(pandoc.read(jira_text,format='jira'),format='markdown')

def exportR4JRequirements(r4jfolders, search: JiraSearch):
    def recExport(folderJson):
        log(f'Getting req from folder : {folderJson["name"]}')
        # TODO: Apply filtering (product) 
        def getReqTable(issues):
            result = {}
            for elem in issues:
                reqJson = search.get_requirement(elem['data']['key'])
                fields = reqJson['fields']

                # update req description with better Markdown output
                md_description = convertJira2Markdown(fields['description'])
                
                fields['description'] =  md_description.strip()
        
                result[elem['data']['key']] = fields
                
                
            return result

        req_section = {}
        req_section['name'] = folderJson['name']
        req_section['description'] = convertJira2Markdown(folderJson['description'])
        req_section['reqs'] = getReqTable(folderJson['issues'])
        
        req_section['sections'] = {}
        sec_number=0
        for subfolder in folderJson['folders']:
            sec_number +=1
            req_section['sections'][sec_number] = recExport(subfolder)
        
        return req_section
    
    return recExport(r4jfolders)

def main():
    options = parse_args()
    
    # 3 steps:
    # - connect Jira database specified in config
    ## get yaml measurement scenario
    try:
        file = open(options.config, 'r')
    except FileNotFoundError:
        log(f'''File {options.config} not found !!''')
        exit(-1)
    else:
        config = yaml.safe_load(file)
    #print(config)

    ## get Jira credential
    user = options.user if options.user is not None \
                else input('Username: ')
    password = options.password if options.password is not None \
                else getpass.getpass('Password: ')
    auth = (user, password)
    
    # - get requirements from the database
    jira = JiraSearch("https://%s" % config['export']['server'], auth, False)
    treeReqJson = jira.get_requirements_tree(projkey=config['export']['projkey'])

    #print(treeReqJson)
    #printFolderNames("", treeReqJson)

    # - Export requirement in word doc
    jsonReqs = {0: exportR4JRequirements(treeReqJson, jira)}
    # exportDoc.save(config['output'])

    # requirement presentation idea:
    # folder has Heading N+1 style (N = folder level)
    # 1 column table with first line
    # # Req ID + Name as specific heading style (is it possible to have it in table header)
    # # description
    # 
    #walkFolderReq(0,treeReqJson)

    log('---  Normal print ---')
    print(jsonReqs)

    log('--- json.dumps ---')
    json.dumps(jsonReqs)

    outname = 'reqs.yaml'
    if options.output is not None:
        outname = options.output
    else:
        if 'yaml_out' in config['export'].keys():
            outname = config['export']['yaml_out']

    outyaml = open(outname,'w')
    log('--- yaml.dump ---')
    yaml.dump(jsonReqs,outyaml,width=1000)


if __name__ == '__main__':
    main()