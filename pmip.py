# -*- coding: utf-8 -*-

import os

class Processing(object):
    """docstring for Processing"""

    def __init__(self, _specimen):
        self.specimen = _specimen

    def validateEnvironment(self):


        dir_list = []
        dir_list.append('/mnt/reconstruction')
        dir_list.append('/mnt/reconstruction/specimens')
        dir_list.append('/mnt/reconstruction/tmp')
        dir_list.append('/mnt/reconstruction/video')
        dir_list.append('/mnt/reconstruction/log')

        bReturnVal = True

        for d in dir_list:
            if not os.path.exists(d):
                print 'missing : %s' % d
                bReturnVal = False
            else:
                print 'found   : %s' % d

        return bReturnVal


    def initEnv(self): 

        if self.validateEnvironment():
            print 'environment ready, continuing'
        else:
            print 'environment not complete, please check configuration'





    def generateFramesForImageList(self, imageList):
        pass


    def registerFramesForList(self):
        pass



