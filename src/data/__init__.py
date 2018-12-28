import re


class JavData:

    def __init__(self):
        self.id = -1
        self.url = ''
        self.title = ''
        self.postDate = None
        self.package = ''
        self.thumbnail = ''
        self.sellDate = None
        self.actress = ''
        self.maker = ''
        self.label = ''
        self.downloadLinks = ''
        self.downloadFiles = ''
        self.productNumber = ''
        self.isSelection = False
        self.isParse2 = False
        self.makersId = 0
        self.rating = 0
        self.isSite = 0
        self.searchResult = ''
        self.detail = ''
        self.createdAt = None
        self.updatedAt = None

    def get_date(self, line=''):
        arr = line.split('：')
        if len(arr) >= 2:
            result = re.search(".*[/-].*/.*", arr[1].strip())
            if result:
                return arr[1].strip()

        return ''

    def get_text(self, line=''):
        arr = line.split('：')
        if len(arr) >= 2:
            return arr[1].strip()

        return ''

    def print(self):
        print('【' + self.title + '】')
        print('  date     [' + str(self.sellDate) + ']')
        print('  actress  [' + self.actress + ']')
        print('  maker    [' + self.maker + ']')
        print('  label    [' + self.label + ']')
        print('  post     [' + str(self.postDate) + ']')
        print('  url      [' + self.url + ']')
        if self.productNumber:
            print('  p_number [' + self.productNumber + ']')
        else:
            print('  p_number is None')
        print(' ')


class Jav2Data:

    def __init__(self):
        self.id = -1
        self.title = ''
        self.downloadLinks = ''
        self.kind = ''
        self.url = ''
        self.detail = ''
        self.createdAt = None
        self.updatedAt = None


class BjData:

    def __init__(self):
        self.id = -1
        self.title = ''
        self.postDate = None
        self.thumbnails = ''
        self.thumbnailsCount = 0
        self.downloadLink = ''
        self.url = ''
        self.postedIn = ''
        self.isDownloads = 0
        self.isSelection = 0
        self.createdAt = None
        self.updatedAt = None

    def print(self):
        print('【' + self.title + '】')
        print('  post_data     [' + str(self.postDate) + ']')
        print('  th count      [' + str(self.thumbnailsCount) + '] ' + self.thumbnails)
        print('  download_link [' + self.downloadLink + ']')
        print('  posted_in     [' + self.postedIn + ']')
        print('  url           [' + self.url + ']')
        print(' ')


class MakerData:

    def __init__(self):
        self.id = -1
        self.name = ''
        self.matchName = ''
        self.label = ''
        self.kind = 0
        self.matchStr = ''
        self.matchProductNumber = ''
        self.siteKind = 0
        self.replaceWords = ''
        self.pNumberGen = 0
        self.registeredBy = ''
        self.createdAt = None
        self.updatedAt = None

    def get_maker(self, javLabel):

        if self.id == 835:
            return self.name + '：' + javLabel

        if not self.label or len(self.label) <= 0:
            return self.name

        return self.name + '：' + self.label

    def get_print_list(self, indent: str = ''):

        print_list = []

        print_list.append(indent + '【' + self.name + ':' + self.label + '】')
        print_list.append(indent + '  id       [' + str(self.id) + ']')
        print_list.append(indent + '  kind     [' + str(self.kind) + ']')
        print_list.append(indent + '  matchNam [' + self.matchName + ']')
        print_list.append(indent + '  matchStr [' + self.matchStr + ']')
        print_list.append(indent + '  matchPNum[' + self.matchProductNumber + ']')
        print_list.append(indent + '  siteKind [' + str(self.siteKind) + ']')
        print_list.append(indent + '  reWords  [' + str(self.replaceWords) + ']')
        print_list.append(indent + '  pNumGen  [' + str(self.pNumberGen) + ']')
        print_list.append(indent + '  regBy    [' + str(self.registeredBy) + ']')
        print_list.append(indent + '  created  [' + str(self.createdAt) + ']')
        print_list.append(indent + '  updated  [' + str(self.updatedAt) + ']')

        return print_list

    def print(self, indent: str = ''):

        print_list = self.get_print_list(indent)
        print('\n'.join(print_list))
        print(' ')


class ImportData:

    def __init__(self):
        self.id = -1
        self.copy_text = ''
        self.kind = 0
        self.matchStr = ''
        self.productNumber = ''
        self.sellDate = None
        self.maker = ''
        self.title = ''
        self.actress = ''
        self.isRar = False
        self.tag = False
        self.filename = ''
        self.hd_kind = 0
        self.movieFileId = 0
        self.isSplit = False
        self.isNameOnly = False
        self.package = ''
        self.thumbnail = ''
        self.downloadFiles = ''
        self.searchResult = ''
        self.detail = ''
        self.url = ''
        self.postDate = None
        self.rating = 0
        self.size = 0


class ReplaceInfoData:

    def __init__(self):

        self.id = -1
        self.type = ''
        self.source = ''
        self.destination = ''
        self.sourceType = ''
        self.createdAt = None
        self.updatedAt = None


class SiteData:

    def __init__(self):

        self.name = ''
        self.title = ''
        self.actress = ''
        self.maker = ''
        self.duration = ''
        self.productNumber = ''
        self.streamDate = ''
        self.sellDate = ''
        self.series = ''
        self.label = ''

    def get_detail(self):
        return self.streamDate + '、' + self.sellDate + '、' + self.actress + '、' + self.title

    def get_print_list(self, indent: str = ''):

        print_list = []

        print_list.append(indent + '【' + self.name + '】')
        print_list.append(indent + '  title      [' + self.title + ']')
        print_list.append(indent + '  actress    [' + self.actress + ']')
        print_list.append(indent + '  maker      [' + self.maker + ']')
        print_list.append(indent + '  duration   [' + self.duration + ']')
        print_list.append(indent + '  pNumber    [' + self.productNumber + ']')
        print_list.append(indent + '  streamDate [' + self.streamDate + ']')
        print_list.append(indent + '  sellDate   [' + self.sellDate + ']')
        print_list.append(indent + '  series     [' + self.series + ']')

        return print_list

    def print(self, indent: str = ''):

        print_list = self.get_print_list(indent)
        print('\n'.join(print_list))
        print(' ')

