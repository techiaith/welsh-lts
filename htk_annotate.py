import sys, re, traceback
from llef import get_stressed_phones

MAX_PHONE = 6

nphoneCounts = {} #  (nphone): count

seen = set()
n = 0
f = sys.stdin

for word in f.read().decode('UTF-8').strip().split('\n'):

	if re.search(ur'\d', word): continue
	if word.lower() in seen: continue
	seen.add(word.lower())
	try:
		stressed_phones = get_stressed_phones(word)
	except (ValueError, TypeError):
		#print 'Bad word ==== "%s"' % word.encode('UTF-8')
		#traceback.print_exc(file=sys.stdout)
		#print '============='
		#badwords.add(word)
		continue

	lexiconword=word

	if lexiconword.startswith("'"): lexiconword=lexiconword[1:]
	if '/' in lexiconword: continue
	if '\\' in lexiconword: continue

	if 'tsh' in stressed_phones:
		#print 'Ignored because of unsupported phone: %s' % lexiconword
                continue;
	
	phones = ' '.join(stressed_phones).encode('UTF-8')
	phones = phones.replace('1','X')
	phones = phones.replace('X','')
	phones = phones.replace('i','I')
	phones = phones.replace('o','O')


	print ("{0:30}{1:30}{2:30}".format(lexiconword.upper().encode('UTF-8'), '[' + word.upper().encode('UTF-8') + ']', phones))
