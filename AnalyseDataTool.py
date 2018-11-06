from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile
from quick.webtools.util.VisualizeTrackPresenceOnGenome import VisualizeTrackPresenceOnGenome
from quick.application.GalaxyInterface import GalaxyInterface
from quick.util.CommonFunctions import silenceRWarnings, extractFileSuffixFromDatasetInfo
from proto.config.Config import URL_PREFIX
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
import json
from urllib import quote
from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack


class AnalyseDataTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.
        Mandatory method for all ProTo tools.
        """
        return "Analyse Data Tool"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select Genome', 'genome'),
                ('Select Track to Visualize', 'dataset'),
                ('Do you need a second track', 'newtrack'),
                ('Select Second track', 'newdataset')]

    @classmethod
    def getOptionsBoxGenome(cls):  # Alt: getOptionsBox1()
        return '__genome__'

    @classmethod
    def getOptionsBoxDataset(cls, prevChoices):  # Alt: getOptionsBox1()
        return GeneralGuiTool.getHistorySelectionElement('bed', 'gsuite')

    @classmethod
    def getOptionsBoxNewtrack(cls, prevChoices):
        return ['No', 'Yes']

    @classmethod
    def getOptionsBoxNewdataset(cls, prevChoices):
        if prevChoices[-2] == 'Yes':
            return GeneralGuiTool.getHistorySelectionElement('bed')
        else:
            pass

    @staticmethod
    def findBinSize(data):
        first = data[0].split()[1]
        last = data[-1].split()[2]
        difference = int(last) - int(first)
        if difference >= 10000000:
            return '10m'
        elif difference > 1000000 and difference < 10000000:
            return '1m'
        else:
            return '0.1m'

    @staticmethod
    def preprocessTrack(genome, dataset):
        suffixForFile = extractFileSuffixFromDatasetInfo(dataset)

        if (suffixForFile == 'bed'):
            trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome,
                                                                              dataset,
                                                                              printErrors=False,
                                                                              printProgress=False)
            return trackName

        elif (suffixForFile == 'gsuite'):
            trackName = []
            trackTitle = []
            # l = []
            gSuite = getGSuiteFromGalaxyTN(dataset)
            for i, iTrack in enumerate(gSuite.allTracks()):
                # l = dir(iTrack)
                # if 'trackName' in l:
                #     print(iTrack.trackName)
                # else:
                #     print('not found')


                #print iTrack, iTrack.trackName, iTrack.title, '<br>'
                trackName.append(iTrack.trackName)
                trackTitle.append(iTrack.title)
            return trackName, trackTitle

    @staticmethod
    def prepareTracknameForURL(trackName):
        if any(isinstance(el, list) for el in trackName):
            trackNameAsJSON = json.dumps(trackName)
            trackNameEncoded = trackNameAsJSON.encode()
        else:
            trackNameAsJSON = json.dumps(trackName)
            trackNameEncoded = quote(trackNameAsJSON)
        return trackNameEncoded

    @classmethod
    def resultPrintGeneric(cls, genome, binSourceParam, regSourceParam, figUrl, path, firstTrack):

        print """
    <!DOCTYPE html>
    <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta charset="utf-8" />
            <title>Highcharts data from JSON Response</title>
            <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
            <script type="text/javascript" src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/modules/xrange.js"></script>
            <script src="https://code.highcharts.com/modules/histogram-bellcurve.js"></script>
            <script src="https://code.highcharts.com/modules/exporting.js"></script>
            <script src="https://code.highcharts.com/modules/offline-exporting.js"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.css"/>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.js"></script>
            <link rel="stylesheet" href='https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/scripts/usingAPIStyle.css'>
            <script type="text/javascript" src='https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/scripts/usingAPIscripts.js'></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.2/modernizr.js"></script>
            <script type="text/javascript">
            jQuery(window).load(function () {
            jQuery('#loading').hide();
            });
            </script>
        </head>
        <body>
            <!--<div id="loading">
                <img src='https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/images/loading_large_white_bg.gif' alt="Loading..." />
                static/hyperbrowser/images/loading_large_white_bg.gif
            </div>  -->
            <div id="optionsDiv">
                <input type="text" id="genome"  value='""" + genome + """'><br>
                <input type="text" id="binSize" value='""" + binSourceParam + """'><br>
                <input type="text" id="regSize" value='""" + regSourceParam + """'><br>
                <input type="text" id="imgpath" value='""" + figUrl + """'><br>
                <input type="text" id="firstTrack" value='""" + firstTrack + """'><br>
            </div>   
            <div id="enterRegionDiv">
                <form>
                    <input type="text" id="chrNr" name="region" placeholder="Enter Region to Visualize"><br />
                    <h5>Example:</h5>
                    <p> use <b>*</b> for full genome visualization, or</p>
                    <p> use <b>chr2</b> to visualize selected chromosome (in this case #2 chromosome), or </p>
                    <p> use <b>chr2:1000000-4000000</b> for visualization of selected region. </p>
                    <input type="button" id="trackButton" onclick="onClickSubmit();" value="Submit">
                </form>
            </div>
            <script>
                    function firstTrackLoad(stat, container){
                            var genome = $('#genome').val();
                            var bin = $('#binSize').val();
                            var reg = $('#regSize').val();
                            var firstTrack = $('#firstTrack').val();
                            var url_path = '""" + path + """';
                            plotFinalChart('newAPI?genome=' + genome+ '&stat='+stat+ '&bin='+bin + '&reg='+reg+ '&firstTrack='+firstTrack, url_path, container);
                        } 
            </script>
            <script>
                 function onClickSubmit(){
                     sendRequestChr("CountStat", "#fifth");
                     sendRequestChr("ProportionCountStat", "#first"); 
                     sendRequestChr("SegmentLengthsStat", "#second"); 
                     sendRequestChr("SegmentDistancesStat", "#third");
                     sendRequestChr("AvgSegLenStat", "#fourth");
                 }
            </script>
            <script>
                function sendRequestChr(stat, container) {
                        var chrNrV = $('#chrNr').val();
                        var genome = $('#genome').val();
                        var firstTrack = $('#firstTrack').val();
                        var url_path = '""" + path + """';
                        var bin;
                        if (chrNrV != '*'){
                            bin = '1m';
                            }
                        else {
                            bin = '*';
                            }
                                plotFinalChart('newAPI/question?' + 'genome=' +genome+ '&stat=' +stat + '&bin='+bin + '&reg='+chrNrV+ '&firstTrack=' +firstTrack , url_path, container);
                    }
            </script>
            <!-- <script>
                var chrNr = document.getElementById('chrNr');
                chrNr.addEventListener("keyup", function(e) {
                event.preventDefault();
                if (e.keyCode === 13) {
                    document.getElementById("trackButton").click();
                    }
                });
            </script>  -->
            <div id="mainChart"> </div>
            <div id="parentChartContainer">
                <div class="chartContainer2" id="fifth" display=none></div>
                <div class="chartContainer1" id="first"></div>
                <div id= "chartContainerFloat" class="clearfix">
                    <div class="chartContainer1" id="second"></div>    
                    <div class="chartContainer1" id="third"></div>
                </div>
                <div class="chartContainer1" id="fourth"></div>
            </div>
            <script>
            function image(thisImg) {
                var img = document.createElement("IMG");
                img.src = thisImg;
                img.setAttribute('width', '100%');
                document.getElementById('mainChart').appendChild(img);
                }
            var figUrl = '""" + str(figUrl) + """'
            if(figUrl != ''){                
                image(figUrl);
                document.getElementById('fifth').style.cssText += ';display:none !important;';
            }
            else{                
                firstTrackLoad("StartEndStat", "#mainChart")
                firstTrackLoad("CountStat", "#fifth")
            }
            </script>
             <script>
            firstTrackLoad("ProportionCountStat", "#first");
            firstTrackLoad("SegmentLengthsStat", "#second");
            firstTrackLoad("SegmentDistancesStat", "#third");
            firstTrackLoad("AvgSegLenStat", "#fourth");
            </script>
        </body>
    </html>"""

    @classmethod
    def resultPrintOverlap(cls, genome, binSourceParam, regSourceParam, path, firstTrack, secondTrack):

        print """
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <meta charset="utf-8" />
                <title>Highcharts data from JSON Response</title>
                <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                <script type="text/javascript" src="https://code.highcharts.com/highcharts.js"></script>
                <script src="https://code.highcharts.com/modules/exporting.js"></script>
                <script src="https://code.highcharts.com/modules/offline-exporting.js"></script>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.css"/>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.js"></script>
                <link rel="stylesheet" href='https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/scripts/usingAPIStyle.css'>
            <script type="text/javascript" src='https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/scripts/usingAPIscripts.js'></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.2/modernizr.js"></script>
                <script type="text/javascript">
                jQuery(window).load(function () {
                jQuery('#loading').hide();
                });
                </script>
            </head>
            <body>
                <div id="loading">
                <img src="https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/images/loading_large_white_bg.gif" alt="Loading..." />
                static/hyperbrowser/images/loading_large_white_bg.gif
            </div>
            <script>
            </script>
            <div id="optionsDiv">
                <input type="text" id="genome"  value='""" + genome + """'><br>
                <input type="text" id="firstTrack" value='""" + firstTrack + """'><br>
                <input type="text" id="secondTrack" value='""" + secondTrack + """'><br>
                <input type="text" id="binSize" value='""" + binSourceParam + """'><br>
                <input type="text" id="regSize" value='""" + regSourceParam + """'><br>
            </div>   
            <div id="enterRegionDiv">
                <input type="text" id="chrNr" name="region" placeholder="Enter Region to Visualize"/><br>
                <h5>Example:</h5>
                <p> use <b>*</b> for full genome visualization, or</p>
                <p> use <b>chr2</b> to visualize selected chromosome (in this case #2 chromosome), or </p>
                <p> use <b>chr2:1000000-4000000</b> for visualization of selected region. </p>
                <input type="button" id="trackButton" onclick="onClickSubmit();" value="Submit" >
            </div>
            <script>
                    function firstTrackLoad(stat, container){
                            var genome = $('#genome').val();
                            var firstTrack = $('#firstTrack').val();
                            var secondTrack = $('#secondTrack').val();
                            var bin = $('#binSize').val();
                            var reg = $('#regSize').val();
                            var url_path = '""" + path + """'; 
                            plotFinalChartForOverlap('newAPI?genome=' + genome+'&stat='+stat+ "&bin="+bin + "&reg="+reg+ "&firstTrack="+firstTrack +  "&secondTrack="+secondTrack, url_path, container);
                        } 
            </script>
            
            <script>
                 function onClickSubmit(){
                     sendRequestChr("RawOverlapStat", "#first");
                 }
            </script>
            <script>
                function sendRequestChr(stat, container) {
                        var chrNrV = $('#chrNr').val();
                        var genome = $('#genome').val();
                        var firstTrack = $('#firstTrack').val();
                        var secondTrack = $('#secondTrack').val();
                        var url_path = '""" + path + """';
                        var bin;
                        if (chrNrV != '*'){
                            bin = '1m';
                            }
                        else {
                            bin = '*';
                            }
                                plotFinalChartForOverlap('newAPI/question?' + 'genome=' +genome+ '&stat=' +stat + '&bin='+bin + '&reg='+chrNrV+ '&firstTrack=' +firstTrack +  "&secondTrack="+secondTrack, url_path, container);
                    }
            </script>
            <div id="parentChartContainer">
                <div class="chartContainer2" id="first" display=none></div>
                <!-- <div class="chartContainer1" id="second"></div>
                <div class="chartContainer1" id="third"></div> -->
            </div>
            <img src onerror='firstTrackLoad("RawOverlapStat", "#first")'>
            <!-- <img src onerror='firstTrackLoad("RawOverlapStat", "#second")'>
            <img src onerror='firstTrackLoad("RawOverlapStat", "#third")'> -->
        </body>
        </html>"""

    @classmethod
    def resultPrintGSuite(cls, genome, binSourceParam, regSourceParam, figUrl, path, firstTrack, trackTitle,
                          numberOfTracks):

        print """
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <meta charset="utf-8" />
                <title>Highcharts data from JSON Response</title>
                <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                <script type="text/javascript" src="https://code.highcharts.com/highcharts.js"></script>
                <script src="https://code.highcharts.com/modules/xrange.js"></script>
                <script src="https://code.highcharts.com/modules/series-label.js"></script>
                <script src="https://code.highcharts.com/modules/histogram-bellcurve.js"></script>
                <script src="https://code.highcharts.com/modules/variwide.js"></script>
                <script src="https://code.highcharts.com/modules/exporting.js"></script>
                <script src="https://code.highcharts.com/modules/offline-exporting.js"></script>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.css"/>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/1.11.8/semantic.min.js"></script>
                <link rel="stylesheet" href='https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/scripts/usingAPIStyle.css'>
                <script type="text/javascript" src='https://hyperbrowser.uio.no""" + path + """/static/hyperbrowser/scripts/usingAPIscripts.js'></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.2/modernizr.js"></script>
                <script type="text/javascript">
                jQuery(window).load(function () {
                jQuery('#loading').hide();
                });
                </script>
            </head>
            <body>
                <div id='nav-buttons'> </div>
                <div id='viz-div'>
                    <div id="enterRegionDiv">
                        <form>
                            <input type="text" id="chrNr" name="region" placeholder="Enter Region to Visualize"><br />
                            <h5>Example:</h5>
                            <p> use <b>*</b> for full genome visualization, or</p>
                            <p> use <b>chr2</b> to visualize selected chromosome (in this case #2 chromosome), or </p>
                            <p> use <b>chr2:1000000-4000000</b> for visualization of selected region. </p>
                            <input type="button" id="trackButton" onclick="onClickSubmit();" value="Submit">
                        </form>
                    </div>
                    <div id="optionsDiv">
                        <input type="text" id="genome"  value='""" + genome + """'><br>
                        <input type="text" id="binSize" value='""" + binSourceParam + """'><br>
                        <input type="text" id="regSize" value='""" + regSourceParam + """'><br>
                        <input type="text" id="imgpath" value='""" + figUrl + """'><br>
                        <input type="text" id="firstTrack" value='""" + firstTrack + """'><br>
                        <input type="text" id="trackTitle" value='""" + trackTitle + """'><br>
                        <input type="text" id="selectedOption" value=""><br>
                    </div>  
                    <div id="mainChart"> </div>
                    <div id="parentChartContainer">
                        <div class="chartContainer2" id="fifth" display=none></div>
                        <div class="chartContainer1" id="first"></div>
                        <div id= "chartContainerFloat" class="clearfix">
                            <div class="chartContainer1" id="second"></div>    
                            <div class="chartContainer1" id="third"></div>
                        </div>
                        <div class="chartContainer1" id="fourth"></div>
                    </div>
                </div>    
                <script>
                    makeButtons(""" + str(trackTitle) + """, """ + str(numberOfTracks) + """ );    
                    makeChartOnClick();
                    function buttonClicked (e){
                        document.getElementById("selectedOption").setAttribute("value", e.target.value);
                        makeChartOnClick();
                    }
                    function makeChartOnClick (){
                        var genome = $('#genome').val();
                        var bin = $('#binSize').val();
                        var reg = $('#regSize').val();
                        var firstTrackTemp = $('#firstTrack').val();
                        var firstTrack = JSON.parse(firstTrackTemp);
                        var url_path = '""" + path + """';
                        var trackTitleTemp = '""" + trackTitle + """';
                        var trackTitle = JSON.parse("[" + trackTitleTemp + "]");
                        trackTitle = trackTitle[0];
                        firstTrack = firedButton(trackTitle, firstTrack);
                        
                        firstTrackLoad("ProportionCountStat", "#first");
                        firstTrackLoad("SegmentLengthsStat", "#second");
                        firstTrackLoad("SegmentDistancesStat", "#third");
                        firstTrackLoad("AvgSegLenStat", "#fourth");
                        function image(thisImg) {
                            var img = document.createElement("IMG");
                            img.src = thisImg;
                            img.setAttribute('width', '100%');
                            document.getElementById('mainChart').appendChild(img);
                        }
                        var figUrl = '""" + str(figUrl) + """';
                        if(figUrl != ''){                
                            image(figUrl);
                            document.getElementById('fifth').style.cssText += ';display:none !important;';
                        }
                        else{                
                            firstTrackLoad("StartEndStat", "#mainChart");
                            firstTrackLoad("CountStat", "#fifth");
                        }
                        function firstTrackLoad(stat, container){
                            
                            plotFinalChart('newAPI?genome=' + genome+ '&stat='+stat+ '&bin='+bin + '&reg='+reg+ '&firstTrack='+firstTrack, url_path, container);
                        }
                        function onClickSubmit(){
                             sendRequestChr("CountStat", "#fifth");
                             sendRequestChr("ProportionCountStat", "#first"); 
                             sendRequestChr("SegmentLengthsStat", "#second"); 
                             sendRequestChr("SegmentDistancesStat", "#third");
                             sendRequestChr("AvgSegLenStat", "#fourth");
                        }
                        function sendRequestChr(stat, container) {
                        var chrNrV = $('#chrNr').val();
                        var bin;
                        if (chrNrV != '*'){
                            bin = '1m';
                            }
                        else {
                            bin = '*';
                            }
                                plotFinalChart('newAPI/question?' + 'genome=' +genome+ '&stat=' +stat + '&bin='+bin + '&reg='+chrNrV+ '&firstTrack=' +firstTrack , url_path, container);
                    }
                             }
                </script>
                <script>
                </script>
                <script>
                     function onClickSubmit(){
                         sendRequestChr("CountStat", "#fifth");
                         sendRequestChr("ProportionCountStat", "#first"); 
                         sendRequestChr("SegmentLengthsStat", "#second"); 
                         sendRequestChr("SegmentDistancesStat", "#third");
                         sendRequestChr("AvgSegLenStat", "#fourth");
                     }
                </script>
                <script>
                    function sendRequestChr(stat, container) {
                            var chrNrV = $('#chrNr').val();
                            var genome = $('#genome').val();
                            var url_path = '""" + path + """';
                            var firstTrackTemp = $('#firstTrack').val();
                            var firstTrack = JSON.parse(firstTrackTemp);
                            var bin;
                            if (chrNrV != '*'){
                                bin = '1m';
                                }
                            else {
                                bin = '*';
                                }
                                    plotFinalChart('newAPI/question?' + 'genome=' +genome+ '&stat=' +stat + '&bin='+bin + '&reg='+chrNrV+ '&firstTrack=' +firstTrack , url_path, container);
                        }
                </script>    
            </body>
        </html>"""

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        path = str(URL_PREFIX)
        dataset = choices.dataset
        genome = choices.genome
        text = choices.newtrack
        secondDataset = choices.newdataset
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(dataset), 'r')
        with inputFile as f:
            data = [x for x in f.readlines()]
        silenceRWarnings()
        binSourceParam = '*'
        regSourceParam = '*'
        trackNamePrep = cls.preprocessTrack(genome, dataset)

        if text == 'No':

            figUrl = ''
            if (len(data) > 30000):

                core = HtmlCore()
                core.styleInfoBegin(styleClass='debug')
                figImage = GalaxyRunSpecificFile(['VizTrackOnGenome.png'], galaxyFn)
                analysisDef = ' [normalizeRows=%s] [centerRows=%s]  -> RawVisualizationDataStat'

                res = GalaxyInterface.runManual([trackNamePrep], analysisDef, regSourceParam, binSourceParam, genome,
                                                username=username,
                                                printResults=False, printHtmlWarningMsgs=False)
                core.styleInfoEnd()
                core.line('')
                core.tableHeader(None)
                rScript = VisualizeTrackPresenceOnGenome.customRExecution(res, figImage.getDiskPath(ensurePath=True),
                                                                          '')
                figUrl = figImage.getURL()
                print GalaxyInterface.getHtmlEndForRuns()
                binSourceParam = '10m'
                regSourceParam = '*'
                cls.resultPrintGeneric(genome, binSourceParam, regSourceParam, figUrl, path, trackNamePrep)

            else:
                if isinstance(trackNamePrep[0], (list,)):
                    numTracks = len(trackNamePrep[0])
                    firstTrack = cls.prepareTracknameForURL(trackNamePrep[0])
                    trackTitle = json.dumps(trackNamePrep[1])
                    cls.resultPrintGSuite(genome, binSourceParam, regSourceParam, figUrl, path, firstTrack, trackTitle,
                                          numTracks)
                else:
                    firstTrack = cls.prepareTracknameForURL(trackNamePrep)
                    cls.resultPrintGeneric(genome, binSourceParam, regSourceParam, figUrl, path, firstTrack)
        else:
            trackName2 = cls.preprocessTrack(genome, secondDataset)
            firstTrack = cls.prepareTracknameForURL(trackNamePrep)
            secondTrack = cls.prepareTracknameForURL(trackName2)
            cls.resultPrintOverlap(genome, binSourceParam, regSourceParam, path, firstTrack, secondTrack)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    @classmethod
    def isPublic(cls):
        return True

    @classmethod
    def isDebugMode(cls):

        return False

    #
    @classmethod
    def getOutputFormat(cls, choices):

        return 'customhtml'
