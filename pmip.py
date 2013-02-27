# -*- coding: utf-8 -*-

import os

class Processing(object):
    """docstring for Processing"""

    def __init__(self, _specimen):
        self.specimen = _specimen
        self.basedir = '/mnt/reconstruction'

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
        api.getDSImagesFromListToPath(imageList, self.dirs['raw'])




    def registerFramesForList(self):
        pass



