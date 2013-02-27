# -*- coding: utf-8 -*-

class SectionImage(object):
    """docstring for SectionImage"""

    def __init__(self, _tag):
        self.tag =  _tag
        self.metadata = {}
        self.section_number = -1

        # not really sure how to break these up
        self.TILE_baseURL = '''http://human.brain-map.org/tiles//'''
        self.TILE_thumbnail = '''/TileGroup/0-0-0.jpg'''
        self.API_imageServiceBase = '''http://api.brain-map.org/cgi-bin/imageservice?path='''

        #print 'Initialized as SectionImage (tag: %s)' % (self.tag)

    def __str__(self):
        return '%s - [ %s x %s ]' % (self.tag, self.metadata['width'], self.metadata['height'])

    def __repr__(self):
        return '%s - [ %s x %s ]' % (self.tag, self.metadata['width'], self.metadata['height'])
        

    def generateThumbnailURL(self):
        returnStr = self.TILE_baseURL + self.metadata['path'] + self.TILE_thumbnail
        returnStr += '?siTop=' + self.metadata['y']
        returnStr += '&siLeft=' + self.metadata['x']
        returnStr += '&siWidth=' + self.metadata['width']
        returnStr += '&siHeight=' + self.metadata['height']
        return returnStr

    
    def generateDownSampleURL(self, downsample):
        import math
        returnStr = self.API_imageServiceBase + self.metadata['path']
        returnStr += '&top=' + str(int(self.metadata['y'] / math.pow(2,downsample))) 
        returnStr += '&left=' + str(int(self.metadata['x'] / math.pow(2,downsample))) 
        returnStr += '&width=' + str(int(self.metadata['width'] / math.pow(2,downsample))) 
        returnStr += '&height=' + str(int(self.metadata['height'] / math.pow(2,downsample))) 
        returnStr += '&downsample=' + str(downsample)
        return returnStr






class Specimen(object):
    ''' the generic AIBS specimen object'''

    def __init__(self, remote=True, subjectName='undefined'):

        self.subjectName = subjectName
        self.remoteSpecimen = True
        self.metadata = {}
        self.sectionImageList = []

        self.markersOfInterest = []
        self.allMarkers = []
        self.filteredMarkers = []

       # print 'Initialized a new specimen: %s (remote: %s)' % (self.subjectName, str(self.remoteSpecimen))


    def getListOfAvailableMarkers(self):

        if self.remoteSpecimen:

            import requests
            API_baseDetailString = '''http://human.brain-map.org/api/v2/data/Specimen/%d.json?wrap=true&include=donor(age,conditions),data_sets(products[id$in9,10,11,26,27],genes,treatments),specimen_images,specimen_types,well_known_files,structure'''
            specimenDetailJSON = API_baseDetailString % self.metadata['id']
            d = requests.get(specimenDetailJSON)

            if d.status_code == 200:
                if type(d.json) == type(dict()):
                    if d.json['num_rows'] > 0:
                        return d.json['msg'][0]['data_sets']
                else:
                    if d.json()['num_rows'] > 0:
                        return d.json()['msg'][0]['data_sets']
            else:
                return []

        else:
            print 'not implemented yet'


    def getMarkerList(self, verbose=True):
        ''' returns marker list, filtered if wanted'''

        details = self.getListOfAvailableMarkers()
        if type(details) == type(None):
            if verbose:
                print 'no markers found'
            return

        specimenMarkerSet = []
        specimenFilteredMarkerSet = []

        for ds in details:
            
            geneSingle = {}
            
            if ds['treatments'][0]['tags'] == 'histology':
                if verbose:
                    print '%d - HIS: %s' % (ds['id'], ds['treatments'][0]['name'])
                
                geneSingle['id'] = ds['id']
                geneSingle['type'] = 'HIS'
                geneSingle['name'] = ds['treatments'][0]['name']
                
            elif ds['treatments'][0]['tags'] == 'In Situ Hybridization histology':
                
                for gene in ds['genes']:
                    if verbose:
                        print '%d - ISH: %s - %s' % (ds['id'], gene['acronym'], gene['name']) 
                    
                    geneSingle['id'] = ds['id']
                    geneSingle['type'] = 'ISH'
                    geneSingle['name'] = gene['acronym']
            
            specimenMarkerSet.append(geneSingle)

            if geneSingle['name'] in self.markersOfInterest:
                specimenFilteredMarkerSet.append(geneSingle)

            self.filteredMarkers = specimenFilteredMarkerSet
            self.allMarkers = specimenMarkerSet
            
            
            # what do i need to do next???


    def getSectionImages(self, onlyFiltered=True):
        self.sectionImageList = []
        
        list_to_use = []
        if onlyFiltered:
            list_to_use = self.filteredMarkers
        else:
            list_to_use = self.allMarkers

        for sds in list_to_use:
            import aibs
            api = aibs.api()

            imageList = api.getSectionImagesForID(sds['id'])
            self.sectionImageList += imageList

        return self.sectionImageList            


    def getSortedImageList(self):
        import operator
        list_to_sort = self.sectionImageList
        list_to_sort.sort(key=operator.attrgetter('section_number'))
        return list_to_sort


    def printSpecimenDetails(self):

        import pprint
        print('all markers')
        pprint.pprint(self.allMarkers)

        print('filtered markers')
        pprint.pprint(self.filteredMarkers)

        print('section image list')
        pprint.pprint(self.sectionImageList)


        








import requests

class api(object):

    def __init__(self):
        self.API_listOfSpecimens = '''http://api.brain-map.org/api/v2/data/query.json?criteria=model::Specimen,rma::criteria,donor(products[abbreviation$eqHumanASD]),rma::options[num_rows$eq100]'''
        self.API_baseDetailString = '''http://human.brain-map.org/api/v2/data/Specimen/%d.json?wrap=true&include=donor(age,conditions),data_sets(products[id$in9,10,11,26,27],genes,treatments),specimen_images,specimen_types,well_known_files,structure'''
        self.API_listOfImages = '''http://api.brain-map.org/api/v2/data/SectionDataSet/%d.json?include=section_images'''
        self.TILE_baseURL = '''http://human.brain-map.org/tiles//'''
        self.TILE_thumbnail = '''/TileGroup/0-0-0.jpg'''
        self.API_imageServiceBase = '''http://api.brain-map.org/cgi-bin/imageservice?path='''



    def getSpecimensWithName(self, sname):

        specimen_of_interest = []

        for specimenToCopy in self._getListOfAutism():
            if sname in specimenToCopy['name']:
                s = Specimen(remote=True, subjectName=sname)
                s.metadata = specimenToCopy
                specimen_of_interest.append(s)

        return specimen_of_interest

    def getValidSpecimentsWithName(self, sname):

        speclist = self.getSpecimensWithName(sname);

        explist = []
        for s in speclist:
            s.getMarkerList(verbose=False)
            if len(s.allMarkers) > 0:
                explist.append(s)

        return explist


    def _getListOfAutism(self):
        import requests
        r = requests.get(self.API_listOfSpecimens)
        if r.status_code == 200:
            return self._jsonhelper(r)

    def _jsonhelper(self, resp):
        list_to_return = []
        if type(resp.json) == type(dict()):
            if resp.json['num_rows'] > 0:
                list_to_return = resp.json['msg']
        else:
            if resp.json()['num_rows'] > 0:
                list_to_return = resp.json()['msg']
        return list_to_return
    


    def getImageListForID(self, series_id):
        requestURL = self.API_listOfImages % series_id
        r = requests.get(requestURL)

        seriesImageData = []
        if r.status_code == 200:
            seriesImageData = self._jsonhelper(r)


        if(type(seriesImageData) == type(list())):
            seriesImageData = seriesImageData[0]

        return seriesImageData


    def getSectionImagesForID(self, series_id, sorted=True):

        list_to_return = []

        sds = self.getImageListForID(series_id)
        sectionList = sds['section_images']

        if sorted == True:
            import operator
            sectionList.sort(key=operator.itemgetter('section_number'))


        for si in sectionList:
            tag = '%03d-%s' % (si['section_number'], series_id)

            s = SectionImage(tag)
            s.metadata = si
            s.section_number = si['section_number']

            list_to_return.append(s)

        return list_to_return


    def getDSImagesFromListToPath(self, imageList, _path, ds=5, redownload=False):
        import urllib, os

        for img in imageList:
            dsurl =  img.generateDownSampleURL(ds)
            outputname = '%s/%s-%s-DSx%d.jpg' % (_path, img.tag, img.metadata['id'], ds)
            if not os.path.exists(outputname) or redownload:
                urllib.urlretrieve(dsurl, outputname)
                #print 'downloaded: %s to %s' % (dsurl, outputname)
            else:
                #print 'exists  : %s' % (outputname)
                pass

    



    #    rawImageList.append(outputname)
    
#    if not os.path.exists(outputname):
    
 #       
        





        #print 'found %d sectionImages' % len(sectionList['section_images'])


            
        # for seriesImg in series_image_list:
            
        #     _siTop = str(seriesImg['y'])
        #     _siLeft = str(seriesImg['x'])
        #     _siHeight = str(seriesImg['height'])
        #     _siWidth = str(seriesImg['width'])
        #     _path = seriesImg['path']
        #     thumbnail = self.generateThumbnailURL(_path, _siTop, _siLeft, _siWidth, _siHeight)
        #     sec_num = seriesImg['section_number']
            
        #     imgstr = '''<div style="float:left; height:140px;"><div>Section number: <strong>%d</strong></div><img style="border:1px solid #333; margin:5px; width:128px;" src='%s'/></div>''' % (sec_num, thumbnail)
        #     gallery_str += imgstr
            
        # return gallery_str






# specimen (global class)
#    image list
#    metadata dictionary

# image list
#   list of section images

# section image 
#   init as local resource
#   init as remote resource

