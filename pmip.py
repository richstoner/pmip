# -*- coding: utf-8 -*-
  
import os
import workerpool

class Processing(object):
    """docstring for Processing"""

    def __init__(self, _specimen):
        #self.specimen = _specimen.replace('.', '_')

        self.s = _specimen # sending entire Specimen object

        self.specimen = self.s.subjectName.replace('.', '_')

        self.basedir = '/mnt/reconstruction'
        self.scriptBaseDir = '/home/ubuntu/pmip/fijiscript/'

        self.dirs = {}
        self.dirs['spec'] =  os.path.join(self.basedir, 'specimens', self.specimen)
        self.dirs['raw'] =  os.path.join(self.dirs['spec'], 'raw')
        self.dirs['log'] = os.path.join(self.dirs['spec'], 'log')
        self.dirs['video'] = os.path.join(self.dirs['spec'], 'video')
        self.dirs['regsource'] = os.path.join(self.dirs['spec'], 'register_source')
        self.dirs['regtarget'] = os.path.join(self.dirs['spec'], 'register_target')
        self.dirs['points'] = os.path.join(self.dirs['spec'], 'points')
        self.dirs['density'] = os.path.join(self.dirs['spec'], 'density')
        self.dirs['stack'] = os.path.join(self.dirs['spec'], 'stackdir')


    def _validateEnvironment(self):

        dir_list = []
        dir_list.append('/mnt/reconstruction')
        dir_list.append('/mnt/reconstruction/specimens')

        bReturnVal = True

        for d in dir_list:
            if not os.path.exists(d):
                print 'missing : %s' % d
                bReturnVal = False
            else:
                print 'found   : %s' % d

        return bReturnVal


    def _buildDirectoryStructure(self):

        for dd in self.dirs.keys():
            if not os.path.exists(self.dirs[dd]):
                os.makedirs(self.dirs[dd])

        print 'directories for %s created' % self.specimen


    def initEnv(self): 

        self._printTitle('initEnv')

        if self._validateEnvironment():
            print 'environment ready, continuing'
        else:
            print 'environment not complete, please check configuration'
            return

        self._buildDirectoryStructure()


    #pe.generateFramesForImageList(e.getSortedImageList())

    def collectRaw(self):
        self._printTitle('collectRaw, downsample by 2^4')
        self.collectRawGenerics(4, self.dirs['raw'])        

    def collectLargeRaw(self):
        self._printTitle('collectRaw, downsample by 2^1')
        self.collectRawGenerics(1, self.dirs['points'])

    def collectRawGenerics(self, DOWNSAMPLE, _dir):

        if self.s.remoteSpecimen == True:
        
            print '-> collecting images from remote source'
            # download downsampled images

            import aibs
            reload(aibs)
            api = aibs.api()

            api.getDSImagesFromListToPath(self.s.getSortedImageList(), _dir, downsample=DOWNSAMPLE)
            # import glob
            # print glob.glob(_dir + '/*DSx%d.jpg' % DOWNSAMPLE)

        else:

            print '-> collecting images from local source'
            self.getDSImagesFromLocalToPath(self.s.getSortedImageList(), _dir, downsample=DOWNSAMPLE)
            # import glob
            # print glob.glob(_dir + '/*DSx%d.jpg' % DOWNSAMPLE)



    def createContrast(self):

        self._printTitle('createContrast')

        # get list of ds images
        import glob 
        dsImageList = glob.glob(os.path.join(self.dirs['raw'], '*-DSx4.jpg'))
        dsImageList.sort()

        # generate contrast image
        self._executeFIJIScript('REG-filter.jim', dsImageList)                    
        #self._executeFIJIScript('REG-filter-red50.jim', dsImageList)   


    def _printTitle(self, title):
        print ''
        titlestr = '* ' + title
        print titlestr
        print '-'*80

    


    def extractPoints(self):
        self._printTitle('extractPoints')

        # get list of ds images
        import glob 
        dsImageList = glob.glob(os.path.join(self.dirs['points'], '*.jpg'))
        dsImageList.sort()

        #for n, ds in enumerate(dsImageList):




    def _executeFIJIScript(self, scriptName, fileInput, force=False):
        ''' takes the imagej script name and an array of file inputs'''
        import os

        fijiCommandString = '/home/ubuntu/external/Fiji.app/fiji-linux64 -Xms10000m -batch %s %s'        

        if not os.path.exists(os.path.join(self.scriptBaseDir,scriptName)):
            print('Script %s not found' % scriptName)
            return
        else:
            print('%s - Script found, continue' % scriptName)
            for f_to_proc in fileInput:           

                expected_out = f_to_proc.split('.')[0] + '-c.jpg'
                if not os.path.exists(expected_out) or force:
                    commandToRun = fijiCommandString % (os.path.join(os.path.abspath(self.scriptBaseDir), scriptName), f_to_proc)
                    #print(commandToRun)
                    pipe = os.popen(commandToRun)
                    for e in pipe:
                        #print(e)
                        pass

                    print 'created: %s' % expected_out
                else:
                    print 'exists : %s' % expected_out
                    pass

             


    def getDSImagesFromLocalToPath(self, imageList, path, downsample=5):

        for img in imageList:
            #print img
            img.generateDownSampleConversion(path, ds=downsample)


    def createFrames(self):

        self._printTitle('createFrames')

        import glob
        dscImageList = glob.glob(os.path.join(self.dirs['raw'], '*-c.jpg'))
        dscImageList.sort()

        import shutil

        for n, dsc in enumerate(dscImageList):
            frameName = '%s/frame%04d.jpg' % (self.dirs['regsource'], n)
            if not os.path.exists(frameName):
                shutil.copy(dsc, frameName)

        # import glob
        # print glob.glob(self.dirs['regsource'] + '/*.jpg')



    def register(self):

        self._printTitle('register')

        import glob
        files_to_use = glob.glob(self.dirs['regsource'] + '/*.jpg')
        
        #print(len(files_to_use))
        first_file = '%s/frame0000.jpg' % (self.dirs['regsource'])
        first_reg_file = '%s/register0000.jpg' % (self.dirs['regtarget'])
        cmdstr ='cp -v %s %s' % (first_file, first_reg_file)
        pipe = os.popen(cmdstr, 'r')
        for e in pipe:
            pass
         #   print(e)
            
        cmdstr = '/home/ubuntu/pmip/ImageReconstruction/bin/RigidBodyImageRegistration %s/frame%%04d.jpg %s/register%%04d.jpg %d 3' % (self.dirs['regsource'], self.dirs['regtarget'], len(files_to_use))
        #print cmdstr
        pipe = os.popen(cmdstr, 'r')
        for e in pipe:
            #print(e)
            pass

    def generateSummaryTable(self):
        import glob

        dscImageList = glob.glob(os.path.join(self.dirs['raw'], '*-DSx5.jpg'))
        dscImageList.sort()

        htmlString = ''

        for n,dsc in enumerate(dscImageList):
            htmlString += '<div>'
            basename = dsc.split('.')[0].replace('/mnt/', 'files/')

            normal = '<img style="width: 200px; margin:3px;" src="%s.jpg"/>' % basename
            contrast = '<img style="width: 200px; margin:3px;" src="%s-c.jpg"/>' % basename
            reg =   '<img style="width: 200px; margin:3px;" src="%s/register%04d.jpg"/>' % (self.dirs['regtarget'].replace('/mnt/', 'files/'), n)

            (basename.replace('raw', 'register_target'), n)
            
            htmlString += normal
            htmlString += contrast
            htmlString += reg
            htmlString += "</div>"

        return htmlString


    


    def clearRawDirectory(self):
        ''' deletes all files downloaded to or copied to the raw directory '''
        import os
        os.popen('sudo rm -rvf %s/*' % self.dirs['raw'])

    def clearSubjectDirs(self):
        ''' deletes all files downloaded to or copied to the raw directory '''
        import os
        os.popen('sudo rm -rvf %s/*' % self.dirs['spec'])

        self._buildDirectoryStructure()


    def generateSourceVideo(self):

        cmdstr = '/usr/bin/avconv -f image2 -i %s/frame%%04d.jpg -r 12 -s hd1080 %s/source.mp4' % (self.dirs['regsource'], self.dirs['video'])
        pipe = os.popen(cmdstr, 'r')
        # for p in pipe:
        #     print(p)

    def generateRegisteredVideo(self):

        cmdstr = '/usr/bin/avconv -f image2 -i %s/register%%04d.jpg -r 12 -s hd1080 %s/register.mp4' % (self.dirs['regtarget'], self.dirs['video'])
        pipe = os.popen(cmdstr, 'r')
        # for p in pipe:
        #     print(p)

    



