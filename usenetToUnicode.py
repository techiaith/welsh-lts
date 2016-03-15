#!/usr/bin/env python
# encoding: UTF-8

import re

toChars = u"âêîôûŵŷáéíóúẃýàèìòùẁỳäëïöüẅÿÂÊÎÔÛŴŶÁÉÍÓÚẂÝÀÈÌÒÙẀỲÄËÏÖÜẄŸ"
fromChars = u"a+ e+ i+ o+ u+ w+ y+ a/ e/ i/ o/ u/ w/ y/ a\\ e\\ i\\ o\\ u\\ w\\ y\\ a% e% i% o% u% w% y% A+ E+ I+ O+ U+ W+ Y+ A/ E/ I/ O/ U/ W/ Y/ A\ E\ I\ O\ U\ W\ Y\ A% E% I% O% U% W% Y%".split()
charmap = dict(zip(fromChars, toChars))

def convert(s):
    """Converts usenet celtic strings like "gw+r" to Unicode, like u"gŵr"."""
    return re.sub(r"([aeiouwy][+/\\%])", lambda m: charmap[m.group(1)], s)

if __name__ == '__main__':
    import sys
    for line in sys.stdin:
        sys.stdout.write(convert(line.decode("ISO-8859-1")).encode('UTF-8'))
