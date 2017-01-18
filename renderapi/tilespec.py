import time
import numpy as np


class ResolvedTileSpecMap:
    def __init__(self, tilespecs=[], transforms=[]):
        self.tilespecs = tilespecs
        self.transforms = transforms

    def to_dict(self):
        d = {}
        d['tileIdToSpecMap'] = {}
        for ts in self.tilespecs:
            d['tileIdToSpecMap'][ts.tileId] = ts.to_dict()
        d['transformIdToSpecMap'] = {}
        for tf in self.transforms:
            d['transformIdToSpecMap'][tf.transformId] = tf.to_dict()
        return d

    def from_dict(self, d):
        tsmap = d['tileIdToSpecMap']
        tfmap = d['transformIdToSpecMap']
        for tsd in tsmap.values():
            ts = TileSpec()
            ts.from_dict(tsd)
            self.tilespecs.append(ts)
        for tfd in tfmap.values():
            tf.Transform()
            tf.from_dict(tfd)
            self.transforms.append(tf)


class ResolvedTileSpecCollection:
    def __init__(self, tilespecs=[], transforms=[]):
        self.tilespecs = tilespecs
        self.transforms = transforms

    def to_dict(self):
        d = {}
        d['tileCount'] = len(self.tilespecs)
        d['tileSpecs'] = [ts.to_dict() for ts in self.tilespecs]
        d['transformCount'] = len(self.transforms)
        d['transformSpecs'] = [tf.to_dict() for tf in self.transforms]
        return d

    def from_dict(self, d):
        self.tilespecs = []
        self.transforms = []
        for i in range(d['tileCount']):
            ts = TileSpec()
            ts.from_dict(d['tileSpecs'][i])
            self.tilespecs.append(ts)
        for i in range(d['tranformCount']):
            tfd = d['transformSpecs'][i]
            if tfd['className'] is 'mpicbg.trakem2.transform.AffineModel2D':
                tf = AffineModel()
            else:
                tf = Transform()
            tf.from_dict(tfd)
            self.transforms.append(tf)


class StackVersion:
    def __init__(self, cycleNumber=1, cycleStepNumber=1, stackResolutionX=1,
                 stackResolutionY=1, stackResolutionZ=1,
                 materializedBoxRootPath=None, versionNotes="",
                 createTimestamp=None):
        self.cycleNumber = cycleNumber
        self.cycleStepNumber = cycleStepNumber
        self.stackResolutionX = stackResolutionX
        self.stackResolutionY = stackResolutionY
        self.stackResolutionZ = stackResolutionZ
        self.materializedBoxRootPath = materializedBoxRootPath
        if createTimestamp is None:
            createTimestamp = time.strftime('%Y-%M-%dT%H:%M:%S.00Z')
        self.createTimestamp = createTimestamp
        self.versionNotes = versionNotes

    def to_dict(self):
        d = {}
        d['cycleNumber'] = self.cycleNumber
        d['cycleStepNumber'] = self.cycleStepNumber
        d['stackResolutionX'] = self.stackResolutionX
        d['stackResolutionY'] = self.stackResolutionY
        d['stackResolutionZ'] = self.stackResolutionZ
        d['createTimestamp'] = self.createTimestamp
        d["materializedBoxRootPath"] = "string"
        d['mipmapPathBuilder'] = {'numberOfLevels': 0}
        d['versionNotes'] = self.versionNotes
        return d

    def from_dict(self, d):
        for key in d.keys():
            eval('self.%s=d[%s]' % (key, key))


class Filter:
    def __init__(self, classname, params={}):
        self.classname = classname
        self.params = params

    def to_dict(self):
        d = {}
        d['className'] = self.classname
        d['params'] = self.params
        return d

    def from_dict(self, d):
        self.classname = d['className']
        self.params = d['params']


class ReferenceTransform:
    def __init__(self, refId=None, json=None):
        if json is not None:
            self.from_dict(json)
        else:
            self.refId = refId

    def to_dict(self):
        d = {}
        d['type'] = 'ref'
        d['refId'] = self.refId
        return d

    def from_dict(self, d):
        self.refId = d['refId']

    def __str__(self):
        return 'ReferenceTransform(%s)' % self.refId

    def __repr__(self):
        return self.__str__()


class Transform:
    def __init__(self, className=None, dataString=None,
                 transformId=None, json=None):
        if json is not None:
            self.from_dict(json)
        else:
            self.className = className
            self.dataString = dataString
            self.transformId = transformId

    def to_dict(self):
        d = {}
        d['type'] = 'leaf'
        d['className'] = self.className
        d['dataString'] = self.dataString
        if self.transformId is not None:
            d['transformId'] = self.transformId
        return d

    def from_dict(self, d):
        self.dataString = d['dataString']
        self.className = d['className']
        self.transformId = d.get('transformId', None)

    def __str__(self):
        return 'className:%s\ndataString:%s' % (
            self.className, self.dataString)

    def __repr__(self):
        return self.__str__()


class AffineModel(Transform):
    className = 'mpicbg.trakem2.transform.AffineModel2D'

    def __init__(self, M00=1.0, M01=0.0, M10=0.0, M11=1.0, B0=0.0, B1=0.0):
        self.M00 = M00
        self.M01 = M01
        self.M10 = M10
        self.M11 = M11
        self.B0 = B0
        self.B1 = B1
        self.className = 'mpicbg.trakem2.transform.AffineModel2D'
        self.load_M()

    def load_M(self):
        self.M = np.identity(4, np.double)
        self.M[0, 0] = self.M00
        self.M[0, 1] = self.M01
        self.M[1, 0] = self.M10
        self.M[1, 1] = self.M11
        self.M[0, 3] = self.B0
        self.M[1, 3] = self.B1

    def to_dict(self):
        d = {}
        d['type'] = 'leaf'
        d['className'] = self.className
        d['dataString'] = "%f %f %f %f %f %f" % (
            self.M[0, 0], self.M[0, 1], self.M[1, 0],
            self.M[1, 1], self.M[0, 3], self.M[1, 3])
        return d

    def from_dict(self, d):
        ds = d['dataString'].split()
        (self.M00, self.M01, self.M10, self.M11, self.B0, self.B1) = map(
            float, ds)
        self.load_M()

    def invert(self):
        Ai = AffineModel()
        Ai.M = np.linalg.inv(self.M)
        return Ai

    def convert_to_point_vector(self, points):
        Np = points.shape[0]

        zerovec = np.zeros((Np, 1), np.double)
        onevec = np.ones((Np, 1), np.double)

        if points.shape[1] == 2:
            Nd = 2
            points = np.concatenate((points, zerovec), axis=1)
            points = np.concatenate((points, onevec), axis=1)
        elif points.shape[1] == 3:
            points = np.concatenate((points, onevec), axis=1)
            Nd = 3
        assert(points.shape[1] == 4)
        return points, Nd

    def convert_points_vector_to_array(self, points, Nd):
        points = points[:, 0:Nd] / np.tile(points[:, 3], (Nd, 1)).T
        return points

    def tform(self, points):
        points, Nd = self.convert_to_point_vector(points)
        pt = np.dot(self.M, points.T).T
        return self.convert_points_vector_to_array(pt, Nd)

    def inverse_tform(self, points):
        points, Nd = self.convert_to_point_vector(points)
        pt = np.dot(np.linalg.inv(self.M), points.T).T
        return self.convert_points_vector_to_array(pt, Nd)

    def __str__(self):
        return "M=[[%f,%f],[%f,%f]] B=[%f,%f]" % (
            self.M[0, 0], self.M[0, 1], self.M[1, 0],
            self.M[1, 1], self.M[0, 3], self.M[1, 3])


class Layout:
    def __init__(self, sectionId=None, scopeId=None, cameraId=None,
                 imageRow=None, imageCol=None, stageX=None, stageY=None,
                 rotation=None, pixelsize=0.100):
        self.sectionId = str(sectionId)
        self.scopeId = str(scopeId)
        self.cameraId = str(cameraId)
        self.imageRow = imageRow
        self.imageCol = imageCol
        self.stageX = stageX
        self.stageY = stageY
        self.rotation = rotation
        self.pixelsize = pixelsize

    def to_dict(self):
        d = {}
        d['sectionId'] = self.sectionId
        d['temca'] = self.scopeId
        d['camera'] = self.cameraId
        d['imageRow'] = self.imageRow
        d['imageCol'] = self.imageCol
        d['stageX'] = self.stageX
        d['stageY'] = self.stageY
        d['rotation'] = self.rotation
        d['pixelsize'] = self.pixelsize
        return d

    def from_dict(self, d):
        self.sectionId = d.get('sectionId', None)
        self.cameraId = d.get('camera', None)
        self.scopeId = d.get('temca', None)
        self.imageRow = d.get('imageRow', None)
        self.imageCol = d.get('imageCol', None)
        self.stageX = d.get('stageX', None)
        self.stageY = d.get('stageY', None)
        self.rotation = d.get('rotation', None)
        self.pixelsize = d.get('pixelsize', None)


class TileSpec:
    def __init__(self, tileId=None, z=None, width=None, height=None,
                 imageUrl=None, frameId=None, maskUrl=None,
                 minint=0, maxint=65000, layout=Layout(), tforms=[],
                 inputfilters=[], scale3Url=None, scale2Url=None,
                 scale1Url=None, json=None):
        if json is not None:
            self.from_dict(json)
        else:
            self.tileId = tileId
            self.z = z
            self.width = width
            self.height = height
            self.layout = layout
            self.imageUrl = imageUrl
            self.maskUrl = maskUrl
            self.minint = minint
            self.maxint = maxint
            self.tforms = tforms
            self.frameId = frameId
            self.layout = layout
            self.inputfilters = inputfilters
            self.scale3Url = scale3Url
            self.scale2Url = scale2Url
            self.scale1Url = scale1Url

    def to_dict(self):
        thedict = {}
        thedict['tileId'] = self.tileId
        thedict['z'] = self.z
        thedict['width'] = self.width
        thedict['height'] = self.height
        thedict['minIntensity'] = self.minint
        thedict['maxIntensity'] = self.maxint
        thedict['frameId'] = self.frameId
        if self.layout is not None:
            thedict['layout'] = self.layout.to_dict()
        mipmapdict = {}
        mipmapdict['0'] = {}
        mipmapdict['0']['imageUrl'] = self.imageUrl
        if self.scale1Url is not None:
            mipmapdict['1'] = {}
            mipmapdict['1']['imageUrl'] = self.scale1Url
        if self.scale3Url is not None:
            mipmapdict['3'] = {}
            mipmapdict['3']['imageUrl'] = self.scale3Url
        if self.scale2Url is not None:
            mipmapdict['2'] = {}
            mipmapdict['2']['imageUrl'] = self.scale2Url
        if self.maskUrl is not None:
            mipmapdict['0']['maskUrl'] = self.maskUrl
        thedict['mipmapLevels'] = mipmapdict
        thedict['transforms'] = {}
        thedict['transforms']['type'] = 'list'
        # thedict['transforms']['specList']=[t.to_dict() for t in self.tforms]
        thedict['transforms']['specList'] = []
        for t in self.tforms:
            strlist = {}
            # added by sharmi - if your speclist contains a speclist (can
            # happen if you run the optimization more than once)
            if isinstance(t, list):
                strlist['type'] = 'list'
                strlist['specList'] = [tt.to_dict() for tt in t]
                thedict['transforms']['specList'].append(strlist)
            else:
                thedict['transforms']['specList'].append(t.to_dict())

        thedict['inputfilters'] = {}
        thedict['inputfilters']['type'] = 'list'
        thedict['inputfilters']['specList'] = [f.to_dict() for f
                                               in self.inputfilters]
        return thedict

    def from_dict(self, d):
        '''Method to load tilespec from json dictionary'''
        self.tileId = d['tileId']
        self.z = d['z']
        self.width = d['width']
        self.height = d['height']
        self.minint = d['minIntensity']
        self.maxint = d['maxIntensity']
        self.frameId = d.get('frameId', None)
        self.layout = Layout()
        self.layout.from_dict(d['layout'])
        self.minX = d.get('minX', None)
        self.maxX = d.get('maxX', None)
        self.maxY = d.get('maxY', None)
        self.minY = d.get('minY', None)
        self.imageUrl = d['mipmapLevels']['0']['imageUrl']
        self.maskUrl = d['mipmapLevels']['0'].get('maskUrl', None)
        if d['mipmapLevels'].get('2', None) is not None:
            self.scale2Url = d['mipmapLevels']['2'].get('imageUrl', None)
        else:
            self.scale2Url = None
        if d['mipmapLevels'].get('1', None) is not None:
            self.scale1Url = d['mipmapLevels']['1'].get('imageUrl', None)
        else:
            self.scale1Url = None
        if d['mipmapLevels'].get('3', None) is not None:
            self.scale3Url = d['mipmapLevels']['3'].get('imageUrl', None)
        else:
            self.scale3Url = None

        self.tforms = []
        for t in d['transforms']['specList']:
            if t['type'] == 'ref':
                tf = ReferenceTransform(refId=t['refId'])
            elif t['type'] == 'leaf':
                if t['className'] == AffineModel.className:
                    tf = AffineModel()
                    tf.from_dict(t)
                else:
                    tf = Transform(json=t)
                self.tforms.append(tf)
        self.inputfilters = []
        if d.get('inputfilters', None) is not None:
            for f in d['inputfilters']['specList']:
                f['type']
                f = Filter()
                f.from_dict(f)
                self.inputfilters.append(f)
