import sys, re, pickle, json
from llef import get_stressed_phones
import ReadCorpus

MAX_PHONE = 6

blacklist = set(u'''
	saunders james jones kibbutz thomas ein cymraeg
	gan gymraeg bois jenkins baratoir burrows
	uwchaled robert arthur ymddangos
	llinynnau rhoir jane crynhoir howsgipar
	goruwchnaturiol annynol amaethyddol
	newyddiadurwyr cristionogol barhaus parhaus
	bookings diwydiannol diwydiant rhydychen
	cydweithrediad cydymdeimlad you
	maurice parasitoid tywyllwch young
	magyariaid youenn yorath saussure
	your roberts
'''.strip().split())

whitelist = [x.split() for x in re.split(r",\s*", u'''
	lleuad, melyn, aelodau, siarad, ffordd, ymlaen, cefnogaeth, Helen,
	gwraig, oren, diwrnod, gwaith, mewn, eisteddfod, disgownt, iddo,
	oherwydd, Elliw, awdurdod, blynyddoedd, gwlad, tywysog, llyw, uwch,
	rhybuddio, Elen, uwchraddio, hwnnw, beic, cymru, rhoi, aelod,
	rhai, steroid, cefnogaeth, felen, cau, garej, angau, ymhlith,
	gwneud, iawn, un, dweud, llais, wedi, gyda, llyn,
	lliw, yng, Nghymru, gwneud, rownd, ychydig, wy, yn, llaes,
	hyn, newyddion, ar, roedd, pan, llun, melin, sychu,
	ychydig, glin, wrth, Huw, at, nhw, bod, bydd,
    yn un, er mwyn, neu ddysgu, hyd yn oed, tan, ond fe aeth, ati,
    y gymdeithas, yno yn fuan, mawr, ganrif, amser, dechrau, cyfarfod,
    prif, rhaid bod, rheini, Sadwrn, sy'n cofio, cyntaf, rhaid cael,
    dros y ffordd, gwasanaeth, byddai'r rhestr, hyd, llygaid, Lloegr,
    cefn, teulu, enwedig, ond mae, y tu, y pryd, di-hid, peth, hefyd,
    morgan, eto, yma, ddefnyddio, bach, yn wir, diwedd, llenyddiaeth,
    ym Mryste, natur, ochr, mae hi, newid, dy gymorth, nes, gwahanol,
    i ddod, cyngor, athrawon, bychan, neu, digwydd, hud, mynd i weld,
    ei gilydd, cyffredin, hunain, lle, cymdeithasol, y lle, unwaith,
    i ti, newydd, ysgrifennu, y gwaith, darllen, fyddai, addysg, daeth,
    llywodraeth, ond, hynny, esgob, cyrraedd, a bod, gwrs, ceir,
    rhaid gweld, chwarae, nad oedd, wedyn, flwyddyn, ond nid, ardal,
    buasai, hanes, ddiweddar, wedi cael, o bobl, merched, ffilm, cafodd,
    awdur, na, oedd modd, dod, yr hen, gen i, olaf, ddechrau,
    dyna, ddigon, i beidio, bynnag, rhan, trwy, am y llyfr, y cyfnod,
    athro, anifeiliaid, pob, o fewn, yn gwneud, cartref, elfennau,
    er enghraifft, bron, yn fwy, ar gael, sylw, edrych arno, arall,
    cyhoeddus, un pryd, clywed, ohonom, ei fod, aros, gwyrdd golau,
    yn ei gwen, mai, dod o Gymru, personol, allan, wrth y ffenestr,
    ystyr, dda, arbennig, mae'n bwysig, oeddwn, farw, nifer o wyau, maer,
    America, ar gyfer, iaith, bellach, genedlaethol, ateb, at y bont,
    ar y cefn, ac roedd, nesaf, i gyd, doedd dim, cynnwys, amlwg,
    amgylchiadau, gweithwyr, fy mam, ac yn llogi, pethau, unrhyw, drws,
    Evans, yn mynd, corff, neb, eglwys, cafwyd, sef, ar ei,
    datblygu, ac ati, traddodiad, yn byw, ond hefyd, y dydd, Williams,
    dosbarth, yr un, fod yn fawr, ni, yr ysgol, ail ganrif, am, nid,
    gofynnodd, gwybod, llawer, rhywbeth, o rywle, chwilio am, oddi ar,
    cynllun, cychwyn, diolch, llyfr, yn y blaen, dan, i ddim, cyn,
    i'r dde, ddyletswydd, hi, mae'n hwyr, dros, megis, milltir, adeg,
    ambell, yr ogof, yna, Lerpwl, ysgolion, parc, dal, plant,
    mam, oedd hwn, ifanc, gellir, oesoedd canol, capel, ysgol, mlynedd,
    o gwmpas, hon, weithiau, erbyn hyn, stori, i fod, ganddo, yn cael,
    Sir Benfro, gweld, gilydd, ond doedd, oes, un o'ch ffrindiau, ystod,
    ddim, ond pan, edrych, wrth gwrs, a phan, ystyried, wedi bod
'''.strip())]

# Data structures for stats collection
xword_nphone_counts = {} #  nphone: cross-word nphone count
word_counts = {} # word: count
phrase_counts = {} # phrase: count

word_phones = {} # word -> single phones
nphone_words = {} # nphone -> set of words
nphone_phrases = {} # nphone -> set of phrases

# Selected phrase info
sample_phrases_list = []
sample_phrases_set = set()
sample_nphone_count = {} # intra-phrase nphone count
sample_phrases_justification = {} # phrase -> nphone it provided

def add_phrase(phrase, required_nphone):
	sample_phrases_list.append(phrase)
	sample_phrases_set.add(phrase)
	sample_phrases_justification[phrase] = required_nphone
	nphones = list(get_nphones(get_phrase_phones(phrase)))
	for nphone in get_nphones(get_phrase_phones(phrase)):
		sample_nphone_count[nphone] = 1 + sample_nphone_count.get(nphone, 0)



def get_word_phones(word):
	if not word_phones.has_key(word):
		phones = get_stressed_phones(word)
		word_phones[word] = phones
		for nphone in get_nphones(phones):
			nphone_words.setdefault(nphone, set()).add(word)
	word_counts[word] = 1 + word_counts.get(word, 0)
	return word_phones[word]

def get_phrase_phones(phrase):
	phones = []
	for word in phrase:
		phones.extend(get_word_phones(word))
	return tuple(phones)

def get_phrases(words):
	"""return all 1-, 2-, 3-word phrases"""
	words = tuple(words)
	seen = set()
	for i in range(len(words)):
		for j in 1, 2, 3:
			phrase = words[i:i+j]
			if phrase in seen:
				continue
			if blacklist.intersection(set(phrase)):
				continue
			seen.add(phrase)
			yield phrase


def get_nphones(phones):
	nphones = set(zip(phones))
	nphones.update(zip(phones, phones[1:]))
	nphones.update(zip(phones, phones[1:], phones[2:]))
	return nphones

def build_stats():
	# Build statistics
	for sentence in ReadCorpus.getSentences():
		words = re.findall(ur'''[^0-9\W]+(?:'[^0-9\W]+)*''', sentence.lower(), re.UNICODE)
		phones = []
		for i, word in enumerate(words):
			if word in blacklist:
				# Break phones, to prevent false multiphones
				for nphone in get_nphones(phones):
					xword_nphone_counts[nphone] = xword_nphone_counts.get(nphone, 0) + 1
				phones = []
				continue
			if max(ord(ch) for ch in word) > 0x7F:
				continue # XXX exclude accents for now
			#if i > 0: phones.append(u'|')
			try:
				phones += get_word_phones(word)
			except Exception:
				pass # XXX print >> sys.stderr, "Cannot get unstressed phones: %r" % (word,)
				continue
		# Build cross-word nphone count
		for nphone in get_nphones(phones):
			xword_nphone_counts[nphone] = xword_nphone_counts.get(nphone, 0) + 1

		# Build phrase nphone info
		for phrase in get_phrases(words):
			phrase_counts[phrase] = 1 + phrase_counts.get(phrase, 0)
			try:
				for nphone in get_nphones(get_phrase_phones(phrase)):
					nphone_phrases.setdefault(nphone, set()).add(phrase)
			except Exception:
				#print >> sys.stderr, "Cannot get phrase phones: %r" % (phrase,)
				continue

def pick_phrases():
	# Pull out all monophones and the most common multiphones, keeping freq order
	xword_nphones = [x[1] for x in sorted((-count, nphone) for nphone, count in xword_nphone_counts.items())]
	phones_1 = tuple(x for x in xword_nphones if len(x) == 1)
	phones_2 = tuple(x for x in xword_nphones if len(x) == 2)[:500]
	phones_3 = tuple(x for x in xword_nphones if len(x) == 3)[:100]

	print >> sys.stderr, "phones_1: " + u' '.join(u'.'.join(x) for x in phones_1).encode('UTF-8')
	print >> sys.stderr, "phones_2: " + u' '.join(u'.'.join(x) for x in phones_2).encode('UTF-8')
	print >> sys.stderr, "phones_3: " + u' '.join(u'.'.join(x) for x in phones_3).encode('UTF-8')

	test_nphones = phones_1 + phones_2 + phones_3

	for word in whitelist:
		phrase = (word,)
		add_phrase(phrase, None)

	for nphone in test_nphones:
		if sample_nphone_count.get(nphone) > 0:
			#print >> sys.stderr, "Already have %r :-)" % (nphone,)
			continue
		remaining_phrases = nphone_phrases.get(nphone, set()) - sample_phrases_set - blacklist
		if not remaining_phrases:
			# There are no more phrases that have this nphone
			print >> sys.stderr, "No more phrases have %r" % (nphone,)
			continue
		most_frequent_phrase = sorted((-phrase_counts.get(phrase, 0), phrase) for phrase in remaining_phrases)[0][1]
		print >> sys.stderr, "Adding '" + u' '.join(most_frequent_phrase).encode('UTF-8') + "' for '" + u' '.join(nphone).encode('UTF-8') + "'"
		add_phrase(most_frequent_phrase, nphone)

def print_phrases():
	print 'rhif\tymadrodd\tffonau\tar gyfer'
	for i, phrase in enumerate(sample_phrases_list, start=1):
		justification = sample_phrases_justification.get(phrase)
		if justification is None:
			justification_text = u'None'
		else:
			justification_text = u' '.join(justification)
		print u'\t'.join((
			unicode(i),
			u' '.join(phrase).encode('UTF-8'),
			u' '.join(get_phrase_phones(phrase)),
			justification_text,
		)).encode('UTF-8')

def print_nphone_counts():
	freq_nphones = sorted((-count, nphone) for nphone, count in xword_nphone_counts.items())
	for mcount, nphone in freq_nphones:
		print "%dx %d-phone '%s'" % (-mcount, len(nphone), u' '.join(nphone).encode('UTF-8'))

def main():
	build_stats()
	pick_phrases()
	print_phrases()

main()
