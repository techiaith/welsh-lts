#!/usr/bin/env python
#encoding: UTF-8

import zipfile, re
import usenetToUnicode

def getSentences():
	allText = []
	f = zipfile.ZipFile("asc.zip")
	for filename in f.namelist():
		usenetText = f.read(filename).decode('ISO-8859-1')
		text = usenetToUnicode.convert(usenetText)
		text = re.sub(ur'\r', '', text)
		paras = re.split(ur'\n\s*\n+', text)
		for para in paras:
			para = re.sub(ur'\s+', u' ', para.strip())
			for sentence in splitSentences(para):
				yield sentence

def splitSentences(para):
	parts = re.split(u"""(?!^)([.!?]['”"’]?)(?=\s+\W*[A-Z])""", para, re.UNICODE)
	for text, end in zip(parts[::2], parts[1::2]):
		yield (text + end).strip()
