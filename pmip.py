# -*- coding: utf-8 -*-

import os

class Processing(object):
    """docstring for Processing"""

    def __init__(self, _specimen):
        self.specimen = _specimen.replace('.', '_')
        self.basedir = '/mnt/reconstruction'
        self.scriptBaseDir = '/home/ubuntu/pmip/fijiscript/'

        self.dirs = {}
        self.dirs['spec'] =  os.path.join(self.basedir, 'specimens', self.specimen)
        self.dirs['raw'] =  os.path.join(self.dirs['spec'], 'raw')
        self.dirs['log'] = os.path.join(self.dirs['spec'], 'log')
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

        print 'directorys for %s created' % self.specimen


    def initEnv(self): 

        if self._validateEnvironment():
            print 'environment ready, continuing'
        else:
            print 'environment not complete, please check configuration'
            return

        self._buildDirectoryStructure()


    def generateFramesForImageList(self, imageList):
    
        import aibs
        reload(aibs)
        api = aibs.api()
        
        # download downsampled images
        api.getDSImagesFromListToPath(imageList, self.dirs['raw'])

        # get list of ds images
        import glob 
        dsImageList = glob.glob(os.path.join(self.dirs['raw'], '*-DSx4.jpg'))
        dsImageList.sort()

        # generate contrast image
        self._executeFIJIScript('REG-filter.jim', dsImageList)                    


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

            



    def clearRawDirectory(self):
        ''' deletes all files downloaded to or copied to the raw directory '''
        import os
        os.popen('sudo rm -rvf %s/*' % self.dirs['raw'])



    def registerFramesForList(self):
        pass



