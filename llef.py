#!/usr/bin/env python
#encoding: UTF-8
import re, sys, traceback

def u8(ob):
	if isinstance(ob, unicode):
		return ob.encode('UTF-8')
	elif isinstance(ob, tuple):
		return tuple(u8(x) for x in ob)
	elif isinstance(ob, list):
		return [u8(x) for x in ob]
	elif isinstance(ob, dict):
		return dict((u8(k), u8(v)) for k, v in ob)
	else:
		return ob

class Syllable(object):
	def __init__(self, onset, vowels, coda, is_final):
		self.onset = onset
		self.vowels = vowels
		self.coda = coda
		self.is_final = is_final

	def __repr__(self):
		return 'Syllable(onset=%r, vowels=%r, coda=%r)' % (
			u8(self.onset),
			''.join(u8(self.vowels)) if self.vowels else self.vowels,
			''.join(u8(self.coda)) if self.coda else '',
		)

	def reprShort(self):
		return '(%s %s %s%s)' % (
			(''.join(u8(self.onset)) if self.onset else '.'),
			(''.join(u8(self.vowels)) if self.vowels else '.'),
			(''.join(u8(self.coda)) if self.coda else '.'),
			'' # Kill the dollars temporarily because it's messing up diff. ('$' if self.is_final else ''),
		)

# CONSONANTS
# p b t d c g m n ng r ff f th dd
# s sh(orth si/sh/???) ch ll w(orth w cyts)
# l ts(orth ts/tsh/???) dz(orth j) h mh nh ngh rh z(orth wtf???)
# wl wn wr chw 
# j(orth i liquid) (at start of suffix???)

# PERMISSABLE TWO-MEMBER ONSET CLUSTERS
# p-l l-r ff-l ff-r b-l b-r mh-l mh-r f-l f-r m-l m-r
# t-l t-r th-l th-r d-l d-r nh-l nh-r dd-r n-r
# c-l c-r c-n ch-l ch-r ch-n g-l g-n ngh-l ngh-r ngh-n ng-l ng-r
# g-w c-w ch-w
# s-b s-t s-g
# g-wl g-wn g-wr
# XXX hw (hwyneb) hi (hiawndal) ???? hrrrmmm

# PERMISSABLE THREE-MEMBER ONSET CLUSTERS
# s-b-r s-b-l s-t-r s-g-l s-g-r

ONSETS = tuple(tuple(x.split(u'-')) for x in u"""
	ch-d ll-n
	s-b-r s-b-l s-t-r s-g-l s-g-r
	p-l p-n p-r ff-l ff-r b-l b-n b-r mh-l mh-r f-l f-r m-l m-r
	t-l t-r th-l th-r d-l d-r nh-l nh-r dd-r n-r s-d s-ff
	c-l c-r c-n ch-l ch-r ch-n g-l g-n g-r ngh-l ngh-r ngh-n ng-l ng-r
	g-w c-w ch-w
	s-b s-t s-g s-l s-m s-n
	ng-wl ng-wn ng-wr
	g-wl g-wn g-wr
	wl wn wr
	p b t d c g m n ng r ff f th dd
	s sh ch ll w
	l ts chw dz h mh nh ngh rh z
	j
""".split())

# PERMISSIBLE ONE-MEMBER CODA CLUSTERS
# not: h mh nh ngh rh wl wn wr chw

# PERMISSIBLE TWO-MEMBER CODA CLUSTERS
#son-son
#son-ob
#vob-vob
#nvob-nvob
#'sg', 'sb'
#pethau weird ac ymwthiol gyda '[lr]$'

# In a coda, <cons-not-r> [lr] is really <cons-not-r> @ [lr] (but instead the [lr] will split to
# the next syll if poss). Therefore <ob> l s is really <ob> @ l s etc

# PERMISSIBLE THREE-MEMBER CODA CLUSTERS
# Either syllabic [lr] + s (or both: picls)

CODAS = tuple(tuple(x.split(u'-')) for x in u"""
	n-c-r n-c-l n-c-s n-d-r n-t-r n-d-l m-b-l m-b-r l-ts l-d-s r-ts g-l-s
	s-t-r m-p-l s-t-l s-ts r-p-s ff-ts c-ts n-ts m-p-s
	r-ts n-d-s s-g-l r-f-s d-l-s r-d-s c-ts r-c-s n-c-t
	f-r c-r g-l th-r c-l n-s d-r p-r t-r d-n th-m
	s-l ff-r ff-l f-l b-r p-l g-r g-n t-l ch-r s-m
	n-t r-dd r-n r-ch r-th s-t s-g ll-t n-s l-ch c-s r-s n-c r-t r-f r-d
	l-s ts n-d m-p r-m r-c r-ff ng-l c-t ff-t l-d l-t p-s d-s l-c m-s l-m
	l-ff r-p l-f dd-f s-b r-ts l-p m-l r-l n-ts t-t n-th ng-s m-b ff-s
	f-s p-t r-ll g-s r-g l-ts ch-t th-s l-b r-b b-s n-j s-c ff-ts
	m-ff m-n l-g th-t s-ts
	w-n
	n-n r-r f-n b-l d-l d-r
	tsh
	p b t d c g m n ng r ff f th dd
	s sh ch ll w
	l ts dz rh z
	j
""".split())


STRESSED_EXCEPTIONS = {
	u'a': (u'A'),
	u'ag': (u'A', u'g'),
	u'â': (u'A'),
	u'ei': (u'EI'),
	u'i': (u'i'),
	u'o': (u'o'),
	u'dy': (u'd', u'@',),
	u'fy': (u'f', u'@',),
	u'mi': (u'm', u'I',),
	u'y': (u'@',),
	u'ych': (u'@', u'ch',),
	u'yng': (u'@', u'ng',),
	u'yn': (u'@', u'n',),
	u'ym': (u'@', u'm',),
	u'yr': (u'@', u'r',),
	u'cilometr': (u'c', u'I', u'l', u'O1', u'm', u'E', u't', u'@', u'r'),
	u'chilometr': (u'ch', u'I', u'l', u'O1', u'm', u'E', u't', u'@', u'r'),
	u'gilometr': (u'g', u'I', u'l', u'O1', u'm', u'E', u't', u'@', u'r'),
	u'hwyr': (u'h', u'WY1', u'r'),
	u'llwyr': (u'll', u'WY1', u'r'),
	u'lwyr': (u'l', u'WY1', u'r'),
	u'metr': (u'm', u'E1', u't', u'@', u'r'),
	u'fetr': (u'm', u'E1', u't', u'@', u'r'),
	u'litr': (u'l', u'I1', u't', u'@', u'r'),
	u'ochr': (u'O1', u'ch', u'@', u'r'),
	u'theatr': (u'th', u'E1', u'A', u't', u'@', u'r'),
	u'trwy': (u't', u'r', u'WY1'),
	u'thrwy': (u'th', u'r', u'WY1'),
	u'drwy': (u'd', u'r', u'WY1'),
	u'trwy’r': (u't', u'r', u'WY1', u'r'),
	u'thrwy’r': (u'th', u'r', u'WY1', u'r'),
	u'drwy’r': (u'd', u'r', u'WY1', u'r'),
	u'dirprwy': (u'd', u'I1', u'r', u'p', u'r', u'WY'),
	u'ddirprwy': (u'dd', u'I1', u'r', u'p', u'r', u'WY'),
	u'dirprwy’r': (u'd', u'I1', u'r', u'p', u'r', u'WY', u'r'),
	u'ddirprwy’r': (u'dd', u'I1', u'r', u'p', u'r', u'WY', u'r'),
	u'dsilis': (u'j', u'I1', u'l', u'I', u's'),
	u'ïodin': (u'I1', u'O', u'd', u'I', u'n'),
}
def get_stressed_phones(word):
	if word in STRESSED_EXCEPTIONS:
		return tuple(STRESSED_EXCEPTIONS[word]) # XXX why tuple?
	phones = []
	syllables = get_syllables(word)
	if syllables is None: return []
	for s in syllables:
		phones.extend(s.onset or ())
		phones.extend(s.vowels)
		phones.extend(s.coda or ())
	return phones

def get_syllables(word):
	unstressed_phones, apostrophe_phone_indexes = get_unstressed_phones(word)
	syllables = split_syllables(unstressed_phones, apostrophe_phone_indexes)
	if syllables is not None:
		add_schwa(syllables)
		add_stress(syllables)
		remove_accents(syllables)
	return syllables

def add_stress(syllables):
	"""modifies in place"""
	# Stress at the (last) circumflex/acute accent, if there is one
	for syll in reversed(syllables):
		for i in reversed(range(len(syll.vowels))):
			v = syll.vowels[i]
			if re.match(ur'[ÂÊÎÔÛŴŶÁÉÍÓÚẂÝ]', v):
				syll.vowels[i] = v + u'1'
				return

	# Else stress the penult (or the last syllable for monosyllabic words)
	if len(syllables) >= 2:
		stressed = syllables[-2]
	else:
		stressed = syllables[0]
	stressed.vowels[-1] = stressed.vowels[-1] + u'1'

ACCENT_REPLACEMENTS = dict(zip(u'ÂÊÎÔÛŴŶÁÉÍÓÚẂÝÀÈÌÒÙẀỲÄËÏÖÜẄŸ', u'AEIOUWYAEIOUWYAEIOUWYAEIOUWY'))
def remove_accents(syllables):
	"""modifies in place"""
	for syll in syllables:
		newVowels = []
		for v in syll.vowels:
			newVowels.append(u''.join(ACCENT_REPLACEMENTS.get(ch, ch) for ch in v))
		syll.vowels = newVowels

SCHWA_REPLACEMENTS = {
	(u'Y',): (u'@',), # usual case, including w-cons + Y, e.g. chwythu. (But there are complexities: gwynion etc)
	(u'I', u'Y'): (u'I', u'@'), # miliynau, cwestiynau
	(u'YW',): (u'@W',), # amryw < cywion < cywrain. Oh dear. @ better than Y if in doubt
	# Don't do WY: gwyddel ayb.
}
def add_schwa(syllables):
	"""modifies in place"""
	for s in syllables:
		if not s.is_final:
			old = tuple(s.vowels)
			s.vowels = list(SCHWA_REPLACEMENTS.get(old, old))

def split_syllables(orig_phones, apostrophe_phone_indexes):
	"""Split into (C* V+ C*) groups.

	This algorithm is left-greedy, leaving consonants with the preceding vowel.
	That's what we want so that position in the stressed syllable can reflect
	vowel length.
	"""
	phones = orig_phones[:]
	syllables = []


	offset = 0

	while True:
		if not phones:
			break
		found_onset = None
		for onset in ONSETS:
			if tuple(phones[:len(onset)]) == onset:
				found_onset = onset
				phones = phones[len(onset):]
				break
		
		found_vowels = []
		while phones and is_vowel_phone(phones[0]):
			vowel = phones[0]
			found_vowels.append(vowel)
			phones = phones[1:]
			if vowel != u'I':
				# Allow 'iad' etc to be one syllable
				break
		if not found_vowels:
			raise ValueError('No vowels in syllable: orig_phones=%r, phones=%r' % (orig_phones, phones))

		found_coda = None
		for coda in CODAS:
			if tuple(phones[:len(coda)]) == coda:
				found_coda = coda
				phones = phones[len(coda):]
				break
		syllable_length = len(found_onset or ()) + len(found_vowels) + len(found_coda or ())
		precoda_length = len(found_onset or ()) + len(found_vowels)

		# is_final if end of word, or if there is an apostrophe after the nucleus
		is_final = (not phones)
		for i in range(offset + precoda_length + 1, offset + syllable_length + 1): # + 1 to look before the next syllable
			if i in apostrophe_phone_indexes:
				is_final = True
	
		syllables.append(Syllable(found_onset, found_vowels, found_coda, is_final))
	return tuple(syllables)

def extract_apostrophes(seq):
	inputSeq = list(seq)
	outputSeq = []
	apostropheIndexes = set()
	offset = 0
	for i in range(len(inputSeq)):
		elt = inputSeq[i]
		if elt == u"'":
			apostropheIndexes.add(i - offset)
			offset += 1
		else:
			outputSeq.append(elt)
	return outputSeq, apostropheIndexes

# VOWELS: SINGLE SHORT
# I E A O W(orth w llaf) @(orth y dywyll) Y(orth y olau) U(orth u)
# VOWELS: SINGLE LONG
# II EE AA OO WW(orth w llaf) - YY(orth y olau) UU(orth u)
# VOWELS: DIPHTHONGS
# IW EW AW YW OW OI AI EI AU AE OE WY EU UW

# Sillafiadau eithriadol:
# oy: moyn.
# ey: feydd/meysydd/-eych/teyrn/ceyrydd
#
# (XXX beth am 'ei hiaith hi'? A beth am 'ioga' vs 'cicio'? eh? eh???)


UNSTRESSED_EXCEPTIONS = {}
for line in """
moyn: m OE n
dy: d @
fy: f @
y: @
ych: @ ch
ym: @ m
yn: @ n
yr: @ r
Celsius: c E l s I W s
Gelsius: g E l s I W s
Chelsius: ch E l s I W s
Nghelsius: ngh E l s I W s
trapesiymau: t r A p E s I @ m AU
drapesiymau: d r A p E s I @ m AU
thrapesiymau: th r A p E s I @ m AU
nhrapesiymau: nh r A p E s I @ m AU
acasiâu: A c A s I Â U
hacasiâu: h A c A s I Â U
ffantasiâu: ff A n t A s I Â U
siwmper: sh W m p E r
siwmperi: sh W m p E r I
siwed: s IW E d
siw: s IW
siwio: s IW I o
siwper: s IW p E r
gwysiwr: g w Y s I W r
wysiwr: w Y s I W r
bwa: b W A
fwa: f W A
mwa: m W A
dwi: d W I
wnion: W n I O n
hwnion: h W n I O n
wnionyn: W n I O n Y n
hwnionyn: h W n I O n Y n
wnionod: W n I O n O d
hwnionod: h W n I O n O d
chwlomb: ch W l O m b
chwlombau: ch W l O m b AU
cwlomb: c W l O m b
cwlombau: c W l O m b AU
gwlomb: g W l O m b
gwlombau: g W l O m b AU
nghwlomb: ngh W l O m b
nghwlombau: ngh W l O m b AU
gwlwm: g W l W m
wlna: W l n A
hwlna: h W l n A
diwlychol: d I wl @ ch O l
ewlychol: E wl @ ch O l
hewlychol: h E wl @ ch O l
ewlychu: E wl @ ch U
hewlychu: h E wl @ ch U
diwnïad: d I wn Ï A d
ddiwnïad: dd I wn Ï A d
diwraidd: d I wr AI dd
ddiwraidd: dd I wr AI dd
diwreiddio: d I wr EI dd I O
ddiwreiddio: dd I wr EI dd I O
diwres: d I wr E s
ddiwres: dd I wr E s
dwywreiciaeth: d WY wr EI c I AE th
ddwywreiciaeth: dd WY wr EI c I AE th
dwywreigiaeth: d WY wr EI g I AE th
ddwywreigiaeth: dd WY wr EI g I AE th
dwywreigiol: d WY wr EI g I O l
ddwywreigiol: dd WY wr EI g I O l
Llandegwning: ll A n d E g W n I ng
Landegwning: l A n d E g W n I ng
emwladu: E m W l A d U
hemwladu: h E m W l A d U
dramaeiddio: d r A m A EI dd I O
Eirawen: EI r A w E n
ffawydd: ff A WY dd
ffawydden: ff A WY dd E n
bioymoleuedd: b I O @ m O l EU E dd
fioymoleuedd: f I O @ m O l EU E dd
mioymoleuedd: m I O @ m O l EU E dd
Gelliwastad: g E ll I w A s t A d
Ngelliwastad: ng E ll I w A s t A d
microeiliad: m I c r O EI l I A d
ficroeiliad: f I c r O EI l I A d
microeiliadau: m I c r O EI l I A d AU
ficroeiliadau: f I c r O EI l I A d AU
seroeiddio: s E r O EI dd I O
gloeuni: g l o EU n i
cilowat: c I l O w A t
gilowat: g I l O w A t
chilowat: ch I l O w A t
nghilowat: ngh I l O w A t
Niwrowyddorau: n IW r O w Y dd o r AU
ffocsls: ff O c s @ l s
hyrdls: h @ r d @ l s
fangls: f A n g @ l s
jyngls: j @ n g @ l s
mangls: m A n g @ l s
metr: m E t @ r
fetr: f E t @ r
cilometr: c I l O m E t @ r
chilometr: ch I l O m E t @ r
nghilometr: ngh I l O m E t @ r
gilometr: g I l O m E t @ r
litr: l I t @ r
theatr: th E A t @ r
ochr: O ch @ r
""".strip().split('\n'):
	word, phonestring = line.split(': ')
	UNSTRESSED_EXCEPTIONS[word] = phonestring.split()

# IW EW AW YW OW OI AI EI AU AE OE WY EU UW


#mwynhau Lasa    m WY nh AU1     m WY n h AU1
#yn haul Asia	    @ nh AU1 l      @ n h AU1 l

# Bantsaeson   b A n ts AE1 s O n      b A n t s AE s O n
# mats aeddfed  m A1 ts AE1 dd f E d    m A1 t s AE1 dd f E d

# yn Tsar	 @ n ts A1 r	   

class LogicError(RuntimeError):
	pass

def split_chars(word):
	return re.findall(ur"ch|dd|ff|ngh|mh|nh|ng|ll|ph|rh|th|tsh|ts|sh|[bcdfghjlmnprst']|[aeouâêîôûäëïöüáéíóúàèìòùŵŷẅÿẃýẁỳ]|[iwy]", word, re.I|re.U)

def is_simple_cons(ch):
	return re.match(ur'ch|dd|ff|ng|ll|ph|rh|th|mh|nh|ngh|tsh|ts|sh|[bcdfghjlmnprst]', ch, re.I|re.U)

def is_simple_vowel_cluster(ch):
	# all vowels except i/w/y as these may be consonantal
	return re.match(ur'[aeouâêîôûŵŷäëïöüẅÿáéíóúẃýàèìòùẁỳ]+', ch, re.I)

def is_possible_vowel_cluster(ch):
	# all possible vowels, including i/w/y which may be consonantal
	return re.match(ur'[aeiouwyâêîôûŵŷäëïöüẅÿáéíóúẃýàèìòùẁỳ]+', ch, re.I)

def is_vowel_phone(ff):
	return ff.isupper() or ff == u'@'

# 1. Get phones, disambiguating /si/ from /s I/ and /W [lnr]/ from /w[lnr]/. Simple vowels (not iwy) are clustered.
# TODO: ts: rules or exceptions
# TODO: soft chw: exceptions (chwa vs chwe vs ymchwilio)
# 2. Find diphthongs
#  XXX [aeiou]wyd$ bob tro yn 'WY d'
#  XXX ^diw yn issue (ddim yn issue yng nghanol geiriau)
#  xxx wyw (obviously) yn issue. wy[aeiouy] yn biafio
#  xxx ywy (obviously) yn issue. yw[aeiouw] yn biafio
# 3. Break syllables, making syllable codas as big as is legal (because consonant length depends on previous vowel stress)
# 4. Add stress
# 5. Add final-syllableness.
# 5.1. Disambiguate Y from @.
# 6. Add vowel length.
# 7. Label vowels with stress


def get_unstressed_phones(word):
	phones = []
	apostrophePhoneIndexes = set()
	if word in UNSTRESSED_EXCEPTIONS:
		return UNSTRESSED_EXCEPTIONS[word]
	partsAndApostrophes = split_chars(word.lower())
	parts, apostrophePartIndexes = extract_apostrophes(partsAndApostrophes)

	dictparts = dict((i, parts[i]) for i in range(len(parts)))
	for i in range(len(parts)):
		if i in apostrophePartIndexes:
			apostrophePhoneIndexes.add(len(phones))
		append_phone(phones, parts, i, apostrophePartIndexes)
	phones = join_diphthongs(phones)
	return tuple(phones), apostrophePhoneIndexes

def append_phone(phones, parts, i, apostrophePartIndexes):
	pre = parts[i - 1] if i - 1 >= 0 else u'^'
	now = parts[i]
	post = parts[i + 1] if i + 1 < len(parts) else u'$'
	# tail and tailstr are unprocessed ouput from split_chars
	tail = tuple(parts[i + 1:])
	tailstr = u''.join(tail)

	# 0. Skip letters that were already included as part of a cluster
	if phones and phones[-1] == u'wl' and now == u'l':
		return
	elif phones and phones[-1] == u'wn' and now == u'n':
		return
	elif phones and phones[-1] == u'wr' and now == u'r':
		return
	# 1. Disambiguate vowels and consonants.
	# 1.1 Simple cases: unambiguous vowels / consonants
	elif now == u'ph':
		phones.append(u'ff')
	elif is_simple_cons(now):
		phones.append(now)
	elif is_simple_vowel_cluster(now) or now == u'y':
		phones.append(now.upper())
	# 1.2 The letter 'i' can be /I/ or part of /sh/
	elif now == u'i':
		append_i(phones, parts, i, pre, now, post, tail, tailstr)
	# 1.3 The letter 'w' can be /W/ or part of /wl/, /wn/, or /wr/
	elif now == u'w':
		append_w(phones, parts, i, pre, now, post, tail, tailstr, apostrophePartIndexes)
	else:
		#raise LogicError("This code should never be reached: " + repr((phones, parts, i, pre, now, post, tail)))
		print >> sys.stderr, "append_phone: This code should never be reached: " + repr((phones, parts, i, pre, now, post, tail))

def append_i(phones, parts, i, pre, now, post, tail, tailstr):
	"""Handles 'i': determines whether part of 'si'=/sh/"""
	if pre != u's':
		phones.append(u'I')
	elif is_simple_cons(post):
		phones.append(u'I')
	elif post == u'i':
		# sI + ir|id|iff|it|ith
		phones.append(u'I')
	elif post == u'u':
		# Latin 'sius' etc
		phones.append(u'I')
	elif u''.join(phones).endswith('rAWs') and now == u'i':
		# trawsieithu, trawsiwerydd etc
		phones.append(u'I')
	elif post == u'y':
		phones.pop() # remove 's'
		phones.append(u'sh')
	elif is_simple_vowel_cluster(post) and post[0] != 'w':
		phones.pop() # remove 's'
		phones.append(u'sh')
	elif tailstr.startswith('wy'):
		# si + wyd|wyf
		# Pronunciation varies, so use 's I wy' and let triphones disambiguate
		phones.append(u'I')
	elif tailstr.startswith(u'wm'):
		# calsiwm etc
		phones.append(u'I')
	elif tailstr.startswith(u'wl'):
		# capsiwl, insiwleiddio etc
		# Pronunciation varies, so use 's IW l' and let triphones disambiguate
		phones.append(u'I')
	elif post == u'w':
		phones.pop() # remove 's'
		phones.append(u'sh')
	elif not tail:
		phones.append(u'I')
	else:
		#raise LogicError("This code should never be reached: " + repr((phones, parts, i, pre, now, post, tail)))
		print >> sys.stderr, "append_i: This code should never be reached: " + repr((phones, parts, i, pre, now, post, tail))

def append_w(phones, parts, i, pre, now, post, tail, tailstr, apostrophePartIndexes):
	# 1.3.1 Handle simple cases (not w[lnr]<vowel>)
	if len(tail) < 2 or tail[0] not in u'lnr' or not is_possible_vowel_cluster(tail[1]):
		#phones.append(u'W')
		phones.append(get_type_of_w(phones, parts, i, pre, now, post, tail, tailstr, apostrophePartIndexes))
		return

	# 1.3.2 Handle w[lnr]<vowel>: may append /wl/, /wn/, or /wr/ .
	# If so, the l|n|r will be omitted in the next loop iteration.
	if is_possible_vowel_cluster(pre):
		phones.append(u'W')
	elif re.match(ur'^(ryw|ria|ro)', tailstr):
		# gwryw, wriaeth|wriad|wrian, wrol|wron|wrogaeth
		phones.append(u'W')
	elif u''.join(phones[-2:]) == u'sg' and post == u'l':
		# *sgwl*
		phones.append(u'W')
	elif (pre == u'g' and u''.join(phones[-2:]) != u'sg') or pre == u'^':
		if post == u'l':
			# XXX # except: gwlio, gwlyddyn, gwlaw
			# gwlydd g wl Y dd
			phones.append(u'wl')
		elif post == u'n':
			phones.append(u'wn')
		elif post == u'r':
			# XXX # except: gwrymiog gwrw
			# gwra gwrwst gwryd gwrhydau gwryf(-oedd)
			# gwrwst
			# gwrym x2 gwrymio gwrymiog gwrysg gwrysgen
			phones.append(u'wr')
	# Compounded mutated gw[lnr]- is /w[lnr]/ . Approximate this by looking
	# for likely compounds (mined from the hunspell word list: the tests are
	# 100% accurate for that list)
	elif post == u'l' and re.match(ur'^(lad|ledydd|ledd|leidydd|latgar|orwlych)', tailstr):
		phones.append(u'wl')
	elif post == u'n' and (re.match(ur'^(neud|neuthur)', tailstr) or (tuple(phones[-2:]) == (u'y', u'm') and post == u'n')):
		phones.append(u'wn')
	elif post == u'r' and re.match(ur'^(rand|rend|ragedd|raig|reidd)', tailstr):
		phones.append(u'wr')
	else: 
		phones.append(u'W')

def remove_inner_space(m):
	return re.sub(ur'(?<=\S)\s+(?=\S)', u'', m.group(1))

def join_diphthongs(phones):
	phonestring = u' '.join(phones)
	phonestring = re.sub(ur'(I W|E W|A W|O W|Y W|O I|A I|E I|A U|A E|O E|W Y|E U|U W)', remove_inner_space, phonestring)
	return phonestring.split(u' ')

def get_type_of_w(phones, parts, i, pre, now, post, tail, tailstr, apostrophePartIndexes):
	# lead and leadstr are unprocessed ouput from split_chars
	lead = tuple(parts[:i])
	leadstr = u''.join(lead)

	partstr = u''.join(parts)

	if re.match(ur'^([bfm]wa|dwi)$', partstr, re.UNICODE):
		return u'W'
	elif tailstr.startswith(u'ryw'):
		return u'W'
	elif tailstr.startswith(u'y') and i + 2 in apostrophePartIndexes:
		return u'W' # wy'
	elif tailstr == u'yr':
		return u'w' # -wyr
	elif is_simple_cons(pre) and not tailstr.startswith(u'y'):
		return u'W'
	elif tailstr.startswith(u'y'):
		if tailstr == u'yd':
			return u'W'
		elif re.match(ur'^(g?ogwydd|(t|d|th|nh)ramgwydd.*)$', partstr):
			return u'w'
		elif re.match(ur'^(wy|gwy|frogwy|llugwy)$', partstr):
			return u'W'
		elif re.match(ur'^(c|ch|g|ngh)$', leadstr) and re.match(ur'^ymp.*$', tailstr):
			return u'w' # Cwympo: just a freaky exception
		elif re.match(ur'^(c|ch|g|ngh)$', leadstr):
			return u'w' # Cwympo: just a freaky exception
		elif pre == u'g': # XXX and not soft mutated  OR  pre == '' or 'ng' and mutated:
			return u'W' # XXX fix with counterexamples below!
		elif pre == u'ch':
			return u'W'
		else:
			return u'W'
	elif is_simple_vowel_cluster(post):
		return u'w'
	elif is_simple_cons(post):
		return u'W'
	elif post == u'$':
		return u'W'
	elif pre == u'^' and post == u'i':
		return u'w'
	elif pre == u'y':
		if len(tailstr) >= 2 and tail[0] == u'i' and is_possible_vowel_cluster(tail[1]):
			return u'W'
		elif is_possible_vowel_cluster(post):
			return u'w'
		else:
			# XXX angen mwy o ymchwil: bywgraffiad, cywrain ... ?
			return u'W'
	elif (is_simple_vowel_cluster(pre) or pre == u'i') and (is_simple_vowel_cluster(post) or post == u'i'):
		return u'w'
	else:
		print >> sys.stderr, "get_type_of_w: This code should never be reached: ", locals()

#def get_type_of_w():
#        elif followed by 'y':
#                # XXX Oes yna rywbeth am eiriau unsill â choda syml????
#                if part of suffix '-wyr$':
#                        return Consonant # XXX but people like Bruce and JMJ call it a Vowel!
#                if part of suffix '-wyd$':
#                        # Brains yn meddwl ei fod yn hanner ffordd
#                        return Vowel
#
#                if word in ('gogwydd', 'tramgwydd', 'tramgwyddo'):
#                        # gwyddai ayb yn Consonant
#                        return Vowel
#                elif word is 'wy' or 'gwy' or 'gwydir' or 'frogwy' or 'llugwy':
#                        # 'wy' as in river. But XXX check 'gwydir'
#			# Dawi: gwydir=Cytsain (o 'gwe-dir' gwe~=cors)
#                        return Vowel
#                elif preceded by inherent 'c' mutated to 'g' or 'ng' or 'ch':
#                        if word is 'cwympo' and friends:
#                                # Just a freaky exception
#                                return Consonant
#                        else:
#				# R: cwyn=Llafariad, ond cwyn+x=Cytsain
#                                # just 'cwyno' a ffrindiau
#                                return Vowel
#                elif preceded by inherent 'g' (radical or mutated to '' or 'ng'):
#                        # XXX is 'wydd' always Vowelly?
#                        # gwylio is Consonant, ond beth am 'gwyl', 'fe wyl y teledu' (DBJ: llaf)
#                        # D:Dewi=Llafariad
#			# T:Tegau=Llafariad
#			# !d:Dawi=Cytsain
#                        # XXX tsieicio: disgwyl, digwydd, clogwyn/clogwyni, tramgwydd/tramgwyddo, dygwyl, dysgwyl, egwyl
#                        #                                  ^dR     ^DdR      ^DT!d     ^DT!d                       ^DT 
#                        # frogwy, gogwydd, gwybed, gwybod/gwybodus/gwybodaeth, gwybyddol, gwylan, gwymon, gwyr (he knows)/fe wyr
#                        # ^DTdR   ^DTd!R                                                 ^DT!d!R  ^D!d!R   ^R
#                        # egwyddor, gwylnos, gwyrdroi, gwyriad, gwyro, gwyrth, gwyryf, gwystl/gwystlon
#                        #           ^DT!d!R                    ^DT!d!R
#                        # gwythïen, gwyw/gwywo (shrivel), 
#                        # llugwy
#                        # ^DTdR
#                        if word is 'egwyl' or 'gwylnos' or another friend of 'gŵyl':
#                                return Vowel
#                        elif word is 'gwylan':
#                                return Vowel # XXX or not!
#                        elif word is 'colgwyni' or 'gwymon' or 'gwyro':
#                                Ask Pawb
#                        else:
#                                return Consonant
#                elif word is 'chwydd': # ond ddim ei ffrindiau
#                        return Vowel
#                elif preceded by inherent 'ch':
#                        return Consonant
#
#                # XXX rhagor o bosibiliadau yma
#                # XXX ble mae'r macwy[aid]?????
#        elif followed by vowel:
#                return Consonant
#        elif followed by consonant:
#                return Vowel
#        elif follow
#

# 1. sillafau
# 2. hir a byr
# 3. ffonau
#

if __name__ == '__main__':
	badwords = set()
	while True:
	    line = sys.stdin.readline().decode('UTF-8')
	    if not line: break
	    readings = []
	    for word in re.findall(ur'\w+', line, flags=re.UNICODE):
		try:
		    stressed_phones = get_stressed_phones(word)
		except (ValueError, TypeError):
		    readings.append(u'??')
		    badwords.add(word)
		    traceback.print_exc(file=sys.stdout)
		    continue
		readings.append(u' '.join(stressed_phones))
	    print u' | '.join(readings)

	if not badwords:
	    sys.exit(0)
	print >> sys.stderr, 'Bad words: ' + u' '.join(badwords).encode('UTF-8')
	sys.exit(1)
