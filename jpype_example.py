#
# Example python program using Phon's API via JPype
#
# Requirements:
#   * Install latest version of Phon (https://www.phon.ca) API docs available at https://phon.ca/apidocs/
#   * Java 17 or later must be installed and available in the system path (recommended: https://adoptium.net/)
#   * Install JPype (https://jpype.readthedocs.io/en/latest/index.html) (e.g., pip install JPype1)
#
# This program will use Phon's IPADictionary to find transcriptions for a list of english words
# and will create a file 'syllables.csv' which contains a breakdown of syllable types in each word
#
import platform
import csv

import jpype.imports
from jpype import *

# Setup location of Phon installation
PHON_HOME = "C:\\Program Files\\Phon" if platform.system() == "Windows" else "/Applications/Phon.app"
PHON_LIB = PHON_HOME + ("\\lib" if platform.system() == "Windows" else "/Contents/Resources/app/lib")

# list of english words
wordList = ["hello", "world", "goodbye", "sanity"]
tableHeader = ["Orthography", "IPA", "V", "CV", "VC", "CVC", "Other"]

# Start new JVM instance with Phon classpath
jpype.startJVM("-Dfile.encoding=UTF-8", classpath=[PHON_LIB + "/*"], convertStrings=True)
if jpype.isJVMStarted():
    # load english IPA dictionary
    IPADictionaryLibrary = JClass("ca.phon.ipadictionary.IPADictionaryLibrary")
    engDict = IPADictionaryLibrary.getInstance().dictionariesForLanguage("eng").get(0)

    # load english syllabifier
    SyllabifierLibrary = JClass("ca.phon.syllabifier.SyllabifierLibrary")
    engSyllabifier = SyllabifierLibrary.getInstance().getSyllabifierForLanguage("eng-simple")

    IPATranscript = JClass("ca.phon.ipa.IPATranscript")
    with open('syllables.csv', 'w', newline='', encoding="UTF-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tableHeader)
        for word in wordList:
            # Lookup list of available IPA transcription in our dictionary
            options = engDict.lookup(word)
            for option in options:
                # Parse transcription
                ipa = IPATranscript.parseIPATranscript(option)
                # Add syllable information
                engSyllabifier.syllabify(ipa.toList())

                # setup syllable lists
                v = ""
                cv = ""
                vc = ""
                cvc = ""
                other = ""
                # Break syllables into categories
                for syllable in ipa.syllables():
                    if syllable.matches("\\s?\\v"):
                        v += (" " if len(v) > 0 else "") + syllable.toString()
                    elif syllable.matches("\\s?\\c\\v"):
                        cv += (" " if len(cv) > 0 else "") + syllable.toString()
                    elif syllable.matches("\\s?\\v\\c"):
                        vc += (" " if len(vc) > 0 else "") + syllable.toString()
                    elif syllable.matches("\\s?\\c\\v\\c"):
                        cvc += (" " if len(cvc) > 0 else "") + syllable.toString()
                    else:
                        other += (" " if len(other) > 0 else "") + syllable.toString()

                row = [word, option, v, cv, vc, cvc, other]
                writer.writerow(row)

    jpype.shutdownJVM()
else:
    print("Unable to start JVM")
