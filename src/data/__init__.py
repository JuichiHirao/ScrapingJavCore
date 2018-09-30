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

