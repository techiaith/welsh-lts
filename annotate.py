import sys, re, traceback
from llef import get_stressed_phones

MAX_PHONE = 6

nphoneCounts = {} #  (nphone): count

stopwords = set(u'''
ysst _ b c ch d dd f ff g ng h j l ll m n p ph r rh s t th u tc scya v l_n
abc access against ah ahmed algorithm allah amdanjnt amrbose ankst anltodus
ann's arms arts asthma attenborough badshah baeeh baghdad balls basn bass
bastards batch bathhurst bbc bclh bd bdcw bebb bedwareddd bellachd bensednne
beriah beulah beyah bhearna bholu biliards bitch bl blj bmqcdyn bmw bnr
boehm\xeb bohr bosch bp br brahmaputra brahms brenidn brezhnev brightness
brighton broughton brownists br\xfens bsc bt buckyballs burgess burghley
business busness bvgwth bywsd b\xf6hme b\xfe cam'r canrfi cartwright cbac cc
ccc cd cdm cds cdu cf cfe cgag cggc chanf chgronau chilterns chr churchlll
ch\xfen ciss cl clegg cletj clm closs cm cma cnd copyright coutts cpo cps cross
crossland crossley crrig cruft cruiserweight cryflhau
_l composts ct cuckold cv cyfanwsm cyfoedth cymc cymh cymsdc cyngr c\xfen
datguddioddd datlbygodd daughters dc ddchongli'r dddarparu dddibynnu
dddisgrifiad dddwi ddideitl ddilwgr ddisrgifio ddraft ddvlai dd\xfe dd\xfer
denbigh dench design designs developments dfod dgwydd dh dhi'n dhwnnw dinah
dipn disgrfir dispatch diwcdd dj dllm dn dna dnid dogdfen dr dryhurst ds dtws
dvma d\xfe d\xfer ecspyrts ecstracts edgbaston edinburgh edmunds edwards eehc
eidlr eight elijah engfhraifft england's enough ensslin enthusiasm eprdf eralll
escapism etc etendards events exists express f'asa'johnjones f'ochr fachgcn
facn falkands falklands fasaeh fd fdp fearless fentr ffermr fferrn fffl\xf4t
ffilr ffoddd ffrmawaith ffr\xfet ff\xfel fieldsmen fight fighting fireballs
first fl fm fmln fn fnna fresch friends frlfo frs ftorcld functionalism furness
fymrn gadalr garfth gbwysig gdaw'ch gepp gerelnt germs ghali ghandi ghose ghost
ghostbuster ghyfraith gibbs girls glenesslin gl\xf8s gmisiynwyd gmlo gn gnp
gochl gofdnodion goldsmith's gough governess gr grimm grst gr\xfep gs gssd
guiness guinness gvmryd gwiehtio gwyrln gyhdeddi gynghaendd gynmdeithas g\xfen
g\xfer hagr haigh hameln hannah', u"hannah'n", u'happiness hbj hcb hcn health
heavyweight hezekiah higgs high highland hillsborough hints hisht hitch hm hms
hnos hochr horns howard's howells hridesh hryweryn htj htv hugh hupmphries
hvnny h\xfe h\xfen ibn industrialism inst intends inverness itn iucn iwnifforms
jcbs jehovah jess jfelly jgymdeithaseg john john's johnes johnny johns johnson
jonh josiah jp jr k kesch kg kgb khder khmer kkk km knight knightley
kr\xe4tchmer l'r lahr laitumkhrah laleh lanbedrpontsteffan landschaft lb lc ld
leah leighton letch lfa lgeg lgwasg lhwyd light lincoln lll lllaw lloft llsg
llsgr llyft ll\xfen lms 
cuckold's ddisrgifio'r ehc hannah hannah'n happiness loughborough lpg lrgr
ltais ltd lunch lynch mabb mahjal mahler marcsdd masks mass massachusetts
mawreddd mbale mc mcbryde mccolvin mccowen mcdougal mckee mckellen mckinnon
mclean mcluhan mcnally mcpherson mcwhirter meisrri meistress melanchthon
mendelssohn meurlg mh mhwllehli micah micheah might mills miss mlc mlm mm
mnerlod moriah movements mr mrs ms mser mth mwmbls m\xf1decins nahd nbw'n nd
nddo ness nff ngh nghfnod nh nhgwrs nh\xfe nh\xfe'r night nightcap nightingale
nlw nm nne'n nneunant nni noah norah nozvezh nt nt\xea n\xfer ofm orumiyeh
ouromieh overalls overdraft paenl parchg parkfields parkhurst parts pass pc
pdag pdh peht pelntyn peterborough petersburgh philipps phnom phnompenh picls
piranshahr pitch plattdeutsch platts pll pmh pmj pontsh\xe2n portsmouth prblem
press prevents princess problcm progress prthyn prvdain psalmae psb psychology
pt pugh punp qmdeithasol r____ raleigh rd rhasp rhddheir rhredeg rhynghddynt
richards ricketts right righteousness rights rl rlhyl rmc rnae'n rnai rnerch
rnethu ross rothchilds rrach rrc rrez rsc rspb rts ruhamah r\xfem sandycroft
sarah sarj savants sc scafell scaletrix scaletta scalettapass scandal scandale
scarcely scargill scarum scene sceptred schedules scheme schick schipa
schleiermacher schleiner schmidt schneider schon school schools schrodinger
schubert schumacher schweitzer science sciences scienceworld scis scoop
scorpion scotch scothern scotland scott scoundrel scrabl scren script
scriptures scuds scurn sd sdi sergeyevitch setts sffagnwm sg sh shhhh shift
shouldn't shredded sicrhaoddd singh slimbridge sloane's slsters smalley
smithfield smooth smp snp spa space spam spaniel spanish spar spargo'r spd
speak speaks special speciality specie spectacle spectacles spectol spectols
spectrwm speech speed speing speiser spencer spengler spideal spido spielberg
spirea splash splendid split splitter sploet spocshef sponge sporting sports
sprach spreadsheet springer springfield spy sp\xeed srdaloedd srnaf ss ssb ssh
st stgreic subodh success sunlight sweetness swydddfa s\xfen t'r tan'r tb tccc
tchaikovsky td tdd tdim tehran tenderness tgau thewliss thought through th\xfe
th\xfer tl tn tolls towards tr transh transp trench troggs tsb tsianff tt tter
tymhereddd t\xfe t\xfe'r t\xfeb t\xfer un'r unf unhcr vd vetch vhf vhs vl vll
vlll vm vn walmsley walsh watch watts waugh wdodt webb wehrmacht weiss wells
welsh welshman welshmen werht whitgift whrrrrr whssss whtigift wireless witsh
words world worst wright wrrth wrtgtbt wwf www wwwwww wynff x xv xxv yahweh ybn
ydyeh yfg yggdrasil ymhlilth yngh yngln yngl\xfen ynm yrnhdacthu ysgnfennu
ysgrifcnny z \xf8 \xfe \xfed \xfem \xfer
it's let's nietzsche sleigh soft that's wat's what's
'''.strip().split())
seen = set()

n = 0

badwords = set()
f = sys.stdin
for word in f.read().decode('UTF-8').strip().split('\n'):
	if re.search(ur'\d', word): continue
	if word.lower() in stopwords or word.lower() in seen: continue
	seen.add(word.lower())
	try:
		stressed_phones = get_stressed_phones(word)
	except (ValueError, TypeError):
		print 'Bad word ==== "%s"' % word.encode('UTF-8')
		traceback.print_exc(file=sys.stdout)
		print '============='
		badwords.add(word)
		continue
	print (word + u': ' + u' '.join(stressed_phones)).encode('UTF-8')
