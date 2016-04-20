import re
import os


# type one
# TITLE=File28165 Spectrum2217 scans: 8056


# type two
# TITLE=File: "F:\QE\02-17-16\QE01720.raw"; SpectrumID: "2"; scans: "134"

def check_which_version(filename):
  if (filename is None) or type(filename) is not str:
    raise Exception("cannot pass '" + str(filename) + "' as a filename")
    return

  if not os.path.isfile(filename):
    raise Exception("filename1 is not a file!")
    return

  if not filename.endswith('.mgf'):
    raise Exception("filename must end in .mgf")
    return

  regex_for_type_1 = re.compile(r"^TITLE=File[^:]")
  regex_for_type_2 = re.compile(r"^TITLE=File[^\d]")

  with open(filename, 'r') as f:
    for line in f:
      if regex_for_type_1.match(line):
        return "1"

      if regex_for_type_2.match(line):
        return "2"

    print "Cannot figure out mgf file version, even after reading the ENTIRE file!"
    raise Exception("Cannot figure out mgf file version, even after reading the ENTIRE file!")


if __name__ == '__main__':
  print "should print 1"
  print check_which_version('/Users/samlobel/Code/DAD/filesforSam/OldMGFformat/PD1ShortQE01720.mgf')

  print "should print 2"
  print check_which_version('/Users/samlobel/Code/DAD/filesforSam/NewMGFformat/PD2shortQE01720_0.mgf')

  try:
    print "should print out empty file exception"
    print check_which_version(None)
  except Exception as e:
    print str(e)
    print '\n'

  try:
    print "should print out 'is not a file'"
    print check_which_version("/asdf/asdf/asdf")
  except Exception as e:
    print str(e)
    print '\n'

  try:
    print "should print that it doesnt end in mgf"
    print check_which_version('/Users/samlobel/Code/DAD/filesforSam/NewMGFformat/GPM33300000085.xml')
  except Exception as e:
    print str(e)
