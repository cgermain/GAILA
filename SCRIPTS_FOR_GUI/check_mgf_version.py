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