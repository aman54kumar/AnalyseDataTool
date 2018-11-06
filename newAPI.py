"""
API operations on a history.
.. seealso:: :class:`galaxy.model.History`
"""

# from sqlalchemy import true, false
import json
from operator import itemgetter

# from gold.application.HBAPI import doAnalysis
from galaxy import exceptions
from galaxy.web import _future_expose_api as expose_api
from galaxy.web import _future_expose_api_anonymous as expose_api_anonymous
from galaxy.web import _future_expose_api_anonymous_and_sessionless as expose_api_anonymous_and_sessionless
from galaxy.web import _future_expose_api_raw as expose_api_raw

from galaxy.web.base.controller import BaseAPIController
from gold.statistic.CountSegmentStat import CountSegmentStat
from quick.application.ExternalTrackManager import ExternalTrackManager
from galaxy.managers import histories, citations, users
from quick.util.GenomeInfo import GenomeInfo
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.track.Track import Track
from gold.application.StatRunner import AnalysisDefJob
from quick.application.UserBinSource import UserBinSource
from gold.statistic.CountStat import CountStat
from gold.statistic.RawOverlapStat import RawOverlapStat
from quick.util import TrackReportCommon
from quick.statistic.AvgSegLenStat import AvgSegLenStat
from quick.statistic.StartEndStat import StartEndStat
import ast
import logging
log = logging.getLogger( __name__ )
import itertools
import re
import numpy as np
from quick.statistic.SegmentDistancesStat import SegmentDistancesStat
from gold.statistic.SegmentLengthsStat import SegmentLengthsStat
from gold.statistic.ProportionCountStat import ProportionCountStat
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.util.CommonFunctions import ensurePathExists
from collections import OrderedDict
from third_party.alphanum import alphanum

class VisualisationController( BaseAPIController):

    def __init__( self, app ):
        super( VisualisationController, self ).__init__( app )
        self.citations_manager = citations.CitationsManager( app )
        self.user_manager = users.UserManager( app )


# ************* Generic Methods*************
    @staticmethod
    def getQueryTrack(trackName):
        trackTemp = json.loads(trackName)
        return [Track(trackTemp)]

    @classmethod
    def yieldDictElements(cls, mydict):
        for key, val in mydict.iteritems():
            yield key, val

    @classmethod
    def yieldListElements(cls, mylist):
        for i, val in enumerate(mylist):
            yield i, val

    @classmethod
    def replaceItem(cls, mydictorlist):
        from copy import copy
        retdictorlist = copy(mydictorlist)
        if isinstance(mydictorlist, dict):
            yieldFunc = cls.yieldDictElements
        elif isinstance(mydictorlist, list):
            yieldFunc = cls.yieldListElements
        else:
            raise TypeError('Not list or dict')

        for key, val in yieldFunc(mydictorlist):
            if isinstance(val, list) or isinstance(val, dict):
                retdictorlist[key] = cls.replaceItem(val)
            elif isinstance(val, np.ndarray):
                retdictorlist[key] = np.nan_to_num(val).tolist()

        return retdictorlist

    @classmethod
    def replaceItem1(cls, mydict):
        from copy import copy
        retdict = copy(mydict)
        for key, val in mydict.iteritems():
            if isinstance(val, dict):
                retdict[key] = cls.replaceItem(val)
            elif isinstance(val, np.ndarray):
                retdict[key] = np.nan_to_num(val).tolist()
        return retdict

    @classmethod
    def doAnalysisFromDef(cls, trackNames, analysisDef, regSpec, binSpec, genome, flag):
        userBinSource = UserBinSource(regSpec, binSpec, genome)
        job = AnalysisDefJob(analysisDef.getDefAfterChoices(), trackNames[0].trackName, None, userBinSource,
                             galaxyFn=None)
        result = job.run()
        unorderedResults = [(str(key), result[key]) for key in result.getAllRegionKeys()]
        return cls.sortDictionaries(unorderedResults, flag)

    @classmethod
    def sortDictionaries(cls, unorderedResults, flag):
        if flag == 0:
            return dict(unorderedResults)
        elif flag == 1:
            return list(sorted(unorderedResults, cmp=alphanum, key=itemgetter(0)))
        else:
            return "assign flag value"

    @staticmethod
    def getAnalysisDefFromStat(stat):
        if stat == 'CountStat':
            return (AnalysisSpec(CountStat), 1)
        elif stat == 'StartEndStat':
            return (AnalysisSpec(StartEndStat), 1)
        elif stat == 'SegmentDistancesStat':
            return (AnalysisSpec(SegmentDistancesStat), 0)
        elif stat == 'SegmentLengthsStat':
            return (AnalysisSpec(SegmentLengthsStat), 0)
        elif stat == 'AvgSegLenStat':
            return (AnalysisSpec(AvgSegLenStat), 0)
        elif stat == 'CountSegmentStat':
            return (AnalysisSpec(CountSegmentStat), 1)
        elif stat == 'ProportionCountStat':
            return (AnalysisSpec(ProportionCountStat), 1)
        elif stat == 'RawOverlapStat':
            return (AnalysisSpec(RawOverlapStat), 1)
        else:
            return "Something went wrong"

    @classmethod
    def getBinSize(cls, binS, **kwd):
        if binS:
            return binS
        else:
            if (kwd.get('reg')).find(chr) == 1:
                return '1m'
            else:
                return kwd.get('bin')

    @classmethod
    def getRegSize(cls, **kwd):
        return kwd.get('reg')


    @classmethod
    def initializeValues(cls, **kwd):
        binS = kwd.get('bin')
        genome = kwd.get('genome')
        firstTrack = kwd.get('firstTrack')
        stat = kwd.get('stat')
        regSpec = cls.getRegSize(**kwd)
        binSpec = cls.getBinSize(binS, **kwd)
        secondDataset = ''
        track1 = cls.getQueryTrack(firstTrack)
        if stat!='RawOverlapStat':
            tracks = track1

        else:
            secondTrack = kwd.get('secondTrack')
            track2 = cls.getQueryTrack(secondTrack)
            tracks = track1 + track2

        myList = []
        for var in [tracks, regSpec, binSpec, genome]:
            myList.append(var)
        return myList


    @classmethod
    def getAnalysisResults(cls, list, stat):
        if stat!='RawOverlapStat':
            analysisDef, flag = cls.getAnalysisDefFromStat(stat)
            analysisResults = cls.doAnalysisFromDef(list[0], analysisDef, list[1], list[2], list[3], flag)
            return analysisResults
        else:
            analysisDef, flag = cls.getAnalysisDefFromStat(stat)
            analysisResults = cls.doAnalysisFromDefTwo(list[0], analysisDef, list[1], list[2], list[3], flag)
            return analysisResults

    @classmethod
    def getOverlapResults(cls, intResults):

        resultsBoth = dict()
        resultsNone = dict()
        resultsOnlyone = dict()
        resultsOnlytwo = dict()
        processedResults = OrderedDict()
        for refTrackName, refTrackResults in intResults:
            processedResults[refTrackName] = []
            both = int(refTrackResults['Both'])
            query = int(refTrackResults['Only1']) + both
            processedResults[refTrackName].append(both)
            processedResults[refTrackName].append(query)
        return cls.sortDictionaries(processedResults, 1)

    @classmethod
    def resultRunAnalysis(cls, **kwd):
        varList = cls.initializeValues(**kwd)
        stat = kwd.get('stat')
        if stat != 'RawOverlapStat':
            analysisResult = cls.getAnalysisResults(varList, stat)
            if stat == 'StartEndStat':
                newDict = cls.mergeKeysValuesListsStartEndStat(cls, analysisResult)
                return cls.getResultFromDict(cls, newDict)
            elif stat == 'CountStat':
                return cls.mergeKeysValuesListsCountStat2(cls, analysisResult)
            elif stat == 'SegmentDistancesStat':
                return cls.mergeKeysValuesListsSegmentDistancesStat(cls, analysisResult)
            elif stat == 'SegmentLengthsStat':
                return cls.mergeKeysValuesListsSegmentLengthsStat(cls, analysisResult)
            elif stat == 'AvgSegLenStat':
                return cls.mergeKeysValuesListsCountStat(cls, analysisResult)
            elif stat == 'CountSegmentStat':
                return cls.mergeKeysValuesListsCountStat2(cls, analysisResult)
            elif stat == 'ProportionCountStat':
                return cls.mergeKeysValuesListsCountStat2(cls, analysisResult)
            else:
                return "Something went wrong in ResultRunAnalysis method"
        else:
            analysisResult = cls.getAnalysisResults(varList, stat)
            result = cls.overlapResultsInLists(analysisResult)
            return result




# ************* General Methods End*************

# ************* CountStat Start*************
    @staticmethod
    def makeDictToList(dict):
        '''Making Lists from the Track data in Dictionary form'''
        list = [[k, v] for k, v in dict.items()]
        return list

    @staticmethod
    def separateResultValues(list):
        '''Taking out result values from the Track List'''
        results = []
        for i in range(len(list)):
            results.append(list[i][1])
        return results

    @staticmethod
    def makeListofCountValues(results):
        '''Making a list of CountStat results'''
        resultV = []
        for d in results:
            for key in d:
                resultV.append(d[key])
        return resultV


    # ************* CountStat End*************


    # ************* StartEndStat Start*************
    @staticmethod
    def makeListofStartEndValues(results):
        '''Making a list of StartEndStat results'''
        resultV = []
        for d in results:
            for key in d:
                resultV.append(d[key])
        return resultV

    @staticmethod
    def makeListofKeys(list):
        ''' Take keys from the Track list in a list '''
        resultK = []
        for i in list:
            resultK.append(i[0])
        return resultK

    @staticmethod
    def extractChrStartFromKeys(stringKey):
        startNum = stringKey.split(':')
        startNum = startNum[1].split('-')
        return int(startNum[0]) - 1

    @staticmethod
    def clearNaNFromList(listInput, older, newer):
        listInput[:] = [newer if x == older else x for x in listInput]
        return listInput


    @staticmethod
    def mergeKeysValuesListsCountStat(cls, data):
        result = cls.replaceItem1(data)
        return result


    @staticmethod
    def extractChrNameFromKey(name):
        return name.split(':')[0]

    @staticmethod
    def hasNumbers(inputString):
        return bool(re.search(r'\d', inputString))


    @staticmethod
    def distributeListsChrStartEnd(self, newData):
        keyList = [value for key,value in enumerate(newData) if key%2==0]
        resultList = [value for key, value in enumerate(newData) if key%2!=0]
        totalList = [keyList, resultList]
        return totalList

    @staticmethod
    def flattenListEachChr(myList):
        return list(itertools.chain.from_iterable(myList))

    @staticmethod
    def mergeKeysValuesListsStartEndStat(cls, data):
        newData = cls.flattenListEachChr(data)
        newDict = cls.distributeListsChrStartEnd(cls, newData)
        return newDict


    @staticmethod
    def getResultFromDict(cls, newDict):
        chrNames = []
        myResult = ""
        for keys, values in itertools.izip(newDict[0], newDict[1]):
            for start, end in itertools.izip(values["Result"][0], values["Result"][1]):
                myResult += "{'x':" + str(start) + ", 'x2': " + \
                        str(end) + ", 'y': " +str(newDict[0].index(keys))  + "},"

            chrNames.append(cls.extractChrNameFromKey(keys))
        finalResult = list([(ast.literal_eval(myResult))] + [chrNames])
        return finalResult


    # ************* StartEndStat End*************

    # ************* RawOverlapStat Start*************

    @classmethod
    def doAnalysisFromDefTwo(cls, tracks, analysisDef, regSpec, binSpec, genome, flag):
        userBinSource = UserBinSource(regSpec, binSpec, genome)
        job = AnalysisDefJob(analysisDef.getDefAfterChoices(), tracks[0].trackName, tracks[1].trackName, userBinSource,
                             galaxyFn=None)
        result = job.run()
        unorderedResults = [(str(key), result[key]) for key in result.getAllRegionKeys()]
        return list(cls.sortDictionaries(unorderedResults, flag))

    @classmethod
    def overlapResultsInLists(cls, inputList):
        dictInput = cls.flattenListEachChr(inputList)
        result = cls.getUsefulResult(dictInput)
        return result

    @classmethod
    def getUsefulResult(cls, inputList):
        keyList = [value for key, value in enumerate(inputList) if key%2==0]
        bothList = [value['Both'] for key, value in enumerate(inputList) if key%2!=0]
        only1List = [value['Only1'] for key, value in enumerate(inputList) if key%2!=0]
        totalList = [keyList, bothList, only1List]
        return totalList


    # ************* RawOverlapStat End *************


    # ************* SegmentDistancesStat Start ***************
    @classmethod
    def removeUnwantedTypes(cls, data):
        a = []
        b = []
        for keys in data:
            a.append(keys)
            b.append(data[keys]['Result'])
        newDict = dict(zip(a,b))

        return newDict

    @staticmethod
    def mergeKeysValuesListsSegmentDistancesStat(cls, data ):
        data1 = cls.removeUnwantedTypes(data)
        results1 = cls.replaceItem(data1)
        list = cls.makeDictToList(results1)
        results = cls.separateResultValues(list)
        return cls.flattenListEachChr(results)

    # ************* SegmentDistancesStat End ***************


    @staticmethod
    def mergeKeysValuesListsSegmentLengthsStat(cls, data):
        data1 = cls.removeUnwantedTypes(data)
        results1 = cls.replaceItem(data1)
        list = cls.makeDictToList(results1)
        results = cls.separateResultValues(list)
        return cls.flattenListEachChr(results)


    @staticmethod
    def mergeKeysValuesListsCountStat2(cls, data):
        return data


    @staticmethod
    def mergeKeysValuesListsCountSegmentStat(cls, data):
        results = cls.replaceItem(data)
        return results

    @expose_api_anonymous
    def selectedTrack(self, trans, **kwd):
        results = kwd.get('fired_button')
        return results

    @expose_api_anonymous
    def question(self, trans, **kwd):
        results = self.resultRunAnalysis(**kwd)
        return results




    @expose_api_anonymous
    def index( self, trans, **kwd ):
        return self.resultRunAnalysis(**kwd)
