#!/usr/bin/env python3

import requests
import urllib.parse
import tornado.httpclient
import logging as log
import configparser
import brokerutils
import simplejson as json

log = brokerutils.setup_logging(__name__)

class AsterixQueryManager():
    asterixInstance = None

    @classmethod
    def getInstance(cls):
        if AsterixQueryManager.asterixInstance is None:
            config = configparser.ConfigParser()
            config.read('brokerconfig.ini')
            asterix_server = 'localhost'
            asterix_port = 19002

            if config.has_section('Asterix'):
                asterix_server = config.get('Asterix', 'server')
                asterix_port = config.getint('Asterix', 'port')

            AsterixQueryManager.asterixInstance = AsterixQueryManager(asterix_server, asterix_port)

        return AsterixQueryManager.asterixInstance

    def __init__(self, asterix_server, asterix_port):
        self.asterix_server = asterix_server
        self.asterix_port = asterix_port
        self.asterixBaseURL = 'http://' + asterix_server + ':' + str(asterix_port)
        self.queryString = ""
        self.dataverseName = None

    def setDataverseName(self, dataverseName):
        self.dataverseName = dataverseName
        return self
                            
    def forClause(self, clause):
        if self.dataverseName is None:
            raise Exception('No dataverse name set')
            
        self.queryString = self.queryString + " for  " + clause
        return self
        
    def letClause(self, clause):
        if self.dataverseName is None:
            raise Exception('No dataverse name set')

        if len(self.queryString) == 0:
            raise Exception("LET cannot start a query")
        else:
            self.queryString = self.queryString + " let  " + clause
        return self
     
    def whereClause(self, clause):
        if self.dataverseName is None:
            raise Exception('No dataverse name set')

        if len(self.queryString) == 0:
            raise Exception("WHERE cann't start a query")
        else:
            self.queryString = self.queryString + " where  " + clause
            
        return self

    def orderByClause(self, clause):
        if self.dataverseName is None:
            raise Exception('No dataverse name set')

        if len(self.queryString) == 0:
            raise Exception("ORDER BY cannot start a query")
        else:
            self.queryString = self.queryString + " order by  " + clause
        
        return self
     
    def groupByClause(self, clause):
        if self.dataverseName is None:
            raise Exception('No dataverse name set')

        if len(self.queryString) == 0:
            raise Exception("GROUP BY cannot start a query")
        else:
            self.queryString = self.queryString + " group by " + clause
        
        return self

    def returnClause(self, clause):
        if self.dataverseName is None:
            raise Exception('No dataverse name set')

        if len(self.queryString) == 0:
            raise Exception("GROUP BY cannot start a query")
        else:
            self.queryString = self.queryString + " return " + clause
        
        return self
     
    def getQueryString(self):
        return self.queryString

    def reset(self):
        self.queryString = ''

    def execute(self):
        if self.asterixBaseURL is None:
            raise Exception('Query Manager is NOT setup well!!!')
        else:            
            if len(self.queryString) > 0:
                request_url = self.asterixBaseURL + "/" + "query"
                query = "use dataverse " + self.dataverseName + "; " + self.queryString + ";"    
                log.info('Executing... ', query)
                                
                response = requests.get(request_url, params={"query": query})
                
                # response = requests.get(request_url, params = {"query" : query, "mode": "asynchronous"})
                # response = requests.get(request_url +"/result", params = {"handle" : "\"handle\":\"[59, 0]\""})

                # print(response.url)
                # print(response.status_code)
                # print(response.text)
                
                return response.status_code, response.text    

    @tornado.gen.coroutine
    def executeQuery(self, dataverseName, queryStatment):
        response = yield self.executeSQLPP(dataverseName, queryStatment)
        return response

    @tornado.gen.coroutine
    def executeUpdate(self, dataverseName, query):
        response = yield self.executeSQLPP(dataverseName, query)
        return response

    @tornado.gen.coroutine
    def executeDDL(self, dataverseName, ddlStatement):
        response = yield self.executeSQLPP(dataverseName, ddlStatement)
        return response

    @tornado.gen.coroutine
    def executeSQLPP(self, dataverseName, query):
        request_url = self.asterixBaseURL + '/' + 'query/service'
        if dataverseName:
            query = 'use ' + dataverseName + '; ' + query

        query += ';'

        log.debug(query)

        #request_url = request_url + "?" + urllib.parse.urlencode(params)
        # response = requests.get(request_url, params = {"aql": query, 'output': 'json'})

        httpclient = tornado.httpclient.AsyncHTTPClient()
        try:
            request = tornado.httpclient.HTTPRequest(request_url, method='POST', body=query)
            response = yield httpclient.fetch(request)
            log.debug(response.body)

            result = json.loads(str(response.body, encoding='utf-8'))
            if result['status'] == 'success':
                if 'results' in result:
                    return 200, json.dumps(result['results'])
                else:
                    return 200, ''
            else:
                return 500, json.dumps(response['errors'])
        except tornado.httpclient.HTTPError as e:
            log.error('Error ' + str(e))
            log.debug(e.response)
            if e.response and len(e.response.body) > 0:
                log.debug(e.response.body)
                errorResponse = json.loads(str(e.response.body, 'utf-8'))
                log.debug(errorResponse['errors'])
                errorMessage = errorResponse['errors']['msg'] if 'msg' in errorResponse['errors'] else 'Unknown error'
            else:
                errorMessage = str(e)

        return 500, 'Query failed ' + str(errorMessage)
