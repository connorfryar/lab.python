import re

strRegex = '^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$'
strSourceDataFileName = "EmailData.txt"
strValidDataFileName = "ValidEmailData.txt"
strInvalidDataFileName = "InvalidEmailData.txt"

# open files for writing
objValidDataStream = open(strValidDataFileName, 'w')
objInvalidDataStream = open(strInvalidDataFileName, 'w')

# read a line of text from the source file
objSourceDataStream = open(strSourceDataFileName, 'r')

strHeaderRow = objSourceDataStream.readline()
objValidDataStream.write(strHeaderRow)
objInvalidDataStream.write(strHeaderRow)

# read all the other lines of text from the source file

for strLine in objSourceDataStream:
    if(re.search(strRegex, strLine)):
        print('Valid')
        objValidDataStream.write(strLine)
    else:
        print('Invalid')
        objInvalidDataStream.write(strLine)

objSourceDataStream.close()
objValidDataStream.close()
