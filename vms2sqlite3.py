import re, os, sqlite3, time



def testRun():

    sourceFile      = loadFile('Directory Listings/DIR_LISTING.TXT')

    directoryList   = firstSplit(sourceFile)
    fileObjectList  = getFileObjects(directoryList)

    makeDB(fileObjectList)



def loadFile(fileName):
    """Load a file into a string."""

    try:
        if os.path.isfile(fileName):
            directoryListing = open(fileName)
            fileString = directoryListing.read()

            return fileString

        else:
            print("Not a valid filename")

    except (OSError, IOError) as e:
        print(e.errno)
        print(e.filename)
        print(e.strerror)



def firstSplit(fileString):
    """Given a big string directory listing, split it into lists representative of single directories."""

    listOfChunks = []

    chunkPattern = re.compile(r'Directory ([\S]*)(?=\s)\s+(.*?)\s+(?=Total)', flags=re.DOTALL)

    for match in re.finditer(chunkPattern, fileString):
        listOfChunks.append([match.group(1), match.group(2)])   # group(1) represents the directory,
                                                                # and group(2) its contents.
    return listOfChunks



def getIsoTimeStamp(dateString, timeString):
    """Convert time match to sqlite3 compatible ISO format.

    Source dateString format:   'DD-MMM-YYYY'
    Source timeString format:   'HH:MM:SS.SS'
    Target ISO format:          'YYYY-MM-DDTHH:MM:SS.SSS'

    """

    dateRegex = re.compile(r'([\d]{1,2})-([A-Z]{3,3})-([\d]{4,4})') # DD, MMM, YYYY
    timeRegex = re.compile(r'([\d]{2,2})[:]([\d]{2,2})[:]([\d]{2,2})[\.]([\d]{2,2})') # HH, MM, SS, mm

    dateMatchObject = dateRegex.match(dateString)
    day     = str(dateMatchObject.group(1))
    month   = str(time.strptime(dateMatchObject.group(2), "%b").tm_mon) # Cast text month to number
    year    = str(dateMatchObject.group(3))

    timeMatchObject = timeRegex.match(timeString)
    hour    = str(timeMatchObject.group(1))
    minute  = str(timeMatchObject.group(2))
    second  = str(timeMatchObject.group(3))
    mSecond = str(timeMatchObject.group(4) + '0')    # VMS only provides 2 digit precision.

    ISODATE = year + '-' + month + '-' + day + 'T' + hour + ':' + minute + ':' + second + ':' + mSecond

    return ISODATE



class FileObject:

    def __init__(self, attributes, path):
        """Represents a list of file attributes for a given file specification."""

        self.path       = path
        self.name       = attributes.group(1)
        self.extension  = attributes.group(2)
        self.version    = attributes.group(3)
        self.size       = attributes.group(4)
        self.dateRaw    = attributes.group(5)
        self.timeRaw    = attributes.group(6)
        self.group      = attributes.group(7)
        self.owner      = attributes.group(8)
        self.sysPriv    = attributes.group(9)
        self.ownPriv    = attributes.group(10)
        self.grpPriv    = attributes.group(11)
        self.wrldPriv   = attributes.group(12)



def getFileObjects(listOfChunks):
    """Given a list of directory listings, return a list of all FileObjects."""

    files = []                                              # MatchObject.group(#):
    regex = re.compile(r'([\$A-Z0-9_]+)'  # <-------------------------------------- 1.      Name
                       r'[\.]'
                       r'([\$A-Z0-9_]+)'   # <------------------------------------- 2.      Extension
                       r'[;]'
                       r'([0-9]+)'  # <-------------------------------------------- 3.      Version
                       r'\s+'
                       r'([0-9]+)'  # <-------------------------------------------- 4.      Size
                       r'\s+'
                       r'([1-3]?[0-9]-[A-Z]{3,3}-[0-9]{4,4})'  # <----------------- 5.      Date
                       r'\s+'
                       r'([0-2][0-9]:[0-9][0-9]:[0-9]{2,2}[\.][0-9]{2,2})'  # <---- 6.      Time
                       r'\s+[\[]'
                       r'([A-Z0-9]+)[,]?([A-Z0-9]*]?)'  # <------------------------ 7., 8.  Group, Owner
                       r'[\]]\s+[\(]'
                       r'([RWED]{0,4})'  # <--------------------------------------- 9.      SysPriv
                       r'[,]'
                       r'([RWED]{0,4})'  # <--------------------------------------- 10.     OwnPriv
                       r'[,]'
                       r'([RWED]{0,4})'  # <--------------------------------------- 11.     GrpPriv
                       r'[,]'
                       r'([RWED]{0,4})'  # <--------------------------------------- 12.     WrldPriv
                       r'[\)]', re.X)

    for list in listOfChunks:
        for match in re.finditer(regex, list[1]):
            files.append(FileObject(match, list[0]))

    return files



def makeDB(objList):
    """Given a list of file objects, make a database of file specifications"""

    connection = sqlite3.connect("DIRINFO.db")
    cursor = connection.cursor()
    cursor.execute("create table FILES (" + "path text, " +
                                            "name text, " +
                                            "extension text, " +
                                            "version integer, " +
                                            "size integer, " +
                                            "dateRaw text, " +
                                            "timeRaw text, " +
                                            "groupowner text, " +
                                            "owner text, " +
                                            "sysPriv text, " +
                                            "ownPriv text, " +
                                            "grpPriv text, " +
                                            "wrldPriv text, " +
                                            "fullpath text);" )

    for object in objList:

        cursor.execute("insert into FILES" +
                        " values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (object.path,
                        object.name,
                        object.extension,
                        object.version,
                        object.size,
                        object.dateRaw,
                        object.timeRaw,
                        object.group,
                        object.owner,
                        object.sysPriv,
                        object.ownPriv,
                        object.grpPriv,
                        object.wrldPriv,
                        object.path + object.name + '.' + object.extension + ';' + object.version)) #full path

    connection.commit()

if __name__ == '__main__':
    testRun()
