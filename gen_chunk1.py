import re
import json
import random

random.seed(43)

# Parse words.js
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/words.js') as f:
    content = f.read()

words_data = re.findall(r'\{w:"([^"]+)",p:"([^"]+)",d:"([^"]+)"\}', content)

pos_map = {}
word_info = {}
all_words_by_pos = {"v": [], "n": [], "adj": []}

for w, p, d in words_data:
    pk = p.replace(".", "")
    pos_map[w] = pk
    word_info[w] = {"w": w, "p": pk, "d": d}
    if pk in all_words_by_pos:
        all_words_by_pos[pk].append(w)

# Parse sentences.js
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/sentences.js') as f:
    sent_content = f.read()

sentences = {}
current_word = None
current_sentences = []
for line in sent_content.split('\n'):
    line = line.strip()
    m = re.match(r'"([^"]+)":\[', line)
    if m:
        if current_word and current_sentences:
            sentences[current_word] = current_sentences
        current_word = m.group(1)
        current_sentences = []
        continue
    m = re.match(r'"(.+)"[,]?$', line)
    if m:
        current_sentences.append(m.group(1))
        continue
    if line == '],':
        if current_word and current_sentences:
            sentences[current_word] = current_sentences
        current_word = None
        current_sentences = []
if current_word and current_sentences:
    sentences[current_word] = current_sentences

chunk1_words = [w for w, p, d in words_data[126:252]]

# Synonym sets
synonym_sets = {
    # VERBS
    "assuage": {"allay", "alleviate", "soothe", "ease", "mitigate", "mollify", "palliate", "appease", "placate", "quell"},
    "atone": {"expiate", "compensate", "reconcile"},
    "atrophy": {"wane", "stagnate", "enervate", "deteriorate"},
    "attain": {"procure", "consummate"},
    "attribute": {"ascribe", "impute"},
    "augment": {"aggrandize", "accentuate", "embellish"},
    "avenge": {"vindicate", "retaliate"},
    "balk": {"abstain", "dissent", "eschew"},
    "beguile": {"bilk", "dissemble", "enamor", "enthrall"},
    "bequeath": {"bestow", "consign", "delegate"},
    "berate": {"admonish", "chide", "upbraid", "reproach", "chastise", "rebuke", "reprove", "vituperate", "rail"},
    "beseech": {"cajole", "exhort", "entreat"},
    "bilk": {"beguile", "embezzle", "swindle", "defraud"},
    "blandish": {"cajole", "flatter"},
    "buffet": {"assail"},
    "burnish": {"adorn", "embellish", "refurbish"},
    "buttress": {"corroborate", "validate"},
    "cajole": {"blandish", "beseech", "exhort"},
    "calibrate": {"appraise", "assess"},
    "capitulate": {"acquiesce", "accede", "concede", "defer", "relent"},
    "captivate": {"enthrall", "enamor", "beguile", "stupefy"},
    "carouse": {"revel", "cavort"},
    "carp": {"reproach", "rebuke", "chide", "reprove", "rail"},
    "catalog": {"delineate", "recapitulate"},
    "catalyze": {"instigate", "goad", "foster", "engender", "induce"},
    "cavort": {"revel", "carouse", "exult"},
    "chastise": {"admonish", "berate", "rebuke", "reproach", "chide", "upbraid", "reprove", "vituperate", "rail"},
    "cherish": {"revere", "venerate", "extol", "relish", "adore"},
    "chide": {"admonish", "berate", "rebuke", "reproach", "chastise", "upbraid", "reprove", "vituperate", "rail"},
    "circumvent": {"elude", "evade", "forestall", "preclude", "eschew"},
    "cleave": {"amalgamate", "coalesce", "yoke"},
    "coagulate": {"congeal", "coalesce"},
    "coalesce": {"amalgamate", "congeal", "coagulate", "yoke"},
    "coerce": {"constrain", "subjugate", "fetter", "compel"},
    "compensate": {"atone", "expiate", "reciprocate"},
    "complement": {"augment", "embellish", "accentuate"},
    "compound": {"exacerbate", "augment", "aggrandize"},
    "compress": {"abridge", "truncate", "curtail", "constrain"},
    "concede": {"capitulate", "acquiesce", "accede", "defer"},
    "concoct": {"fabricate", "dissemble"},
    "condone": {"exonerate", "exculpate", "absolve", "vindicate", "sanction"},

    # NOUNS
    "asylum": {"sanctuary", "haven", "refuge"},
    "avarice": {"cupidity", "gluttony", "parsimony"},
    "aversion": {"antipathy", "enmity", "animosity", "rancor", "acrimony", "disdain"},
    "ballad": {"dirge", "elegy"},
    "bane": {"anathema", "blight", "scourge"},
    "bard": {"artisan", "virtuoso"},
    "battery": {"barrage"},
    "behemoth": {"colossus"},
    "bias": {"predilection", "proclivity", "propensity", "penchant", "inclination", "affinity"},
    "blemish": {"blight", "aberration"},
    "blight": {"bane", "anathema", "blemish"},
    "boon": {"windfall", "largess", "munificence"},
    "bourgeois": {"conformist", "partisan"},
    "cacophony": {"clamor", "dissonance", "discord"},
    "cadence": {"crescendo"},
    "calamity": {"debacle", "maelstrom", "travesty"},
    "calumny": {"aspersion", "innuendo", "invective", "malediction"},
    "camaraderie": {"rapport", "affinity"},
    "candor": {"veracity", "probity", "rectitude"},
    "canvas": {"palette", "facade", "veneer"},
    "caucus": {"forum", "convention", "congregation"},
    "censure": {"reproach", "reprimand", "rebuke", "invective"},
    "chaos": {"pandemonium", "tumult", "anarchy", "bedlam", "maelstrom"},
    "choreography": {"orchestration", "pageantry"},
    "chronicle": {"anthology", "tome", "compendium", "memoir"},
    "circumlocution": {"verbosity", "grandiloquence", "prolixity"},
    "clamor": {"cacophony", "dissonance"},
    "clemency": {"absolution", "reprieve", "magnanimity", "forbearance"},
    "clergy": {"congregation", "hierarchy"},
    "cobbler": {"artisan"},
    "collusion": {"duplicity", "guile", "legerdemain"},
    "colossus": {"behemoth"},
    "combustion": {"conflagration"},
    "commendation": {"acclaim", "accolade", "approbation", "kudos", "plaudits", "adulation"},
    "complacency": {"apathy", "ennui", "lethargy"},
    "compliment": {"commendation", "accolade", "approbation", "adulation", "plaudits", "kudos"},
    "compunction": {"anguish", "trepidation"},
    "concord": {"accord", "consensus", "rapport"},
    "condolence": {"consolation", "empathy", "pathos"},
    "conduit": {"aisle", "reservoir"},
    "confection": {"amenity", "indulgence"},
    "confidant": {"surrogate", "partisan", "sycophant", "toady"},

    # ADJECTIVES
    "astute": {"canny", "adroit", "adept", "cunning", "wily", "acute", "judicious"},
    "atypical": {"anomalous", "idiosyncratic", "aberrant"},
    "audacious": {"brazen", "intrepid", "impudent", "insolent", "presumptuous", "impetuous"},
    "audible": {"manifest", "patent", "salient", "conspicuous"},
    "auspicious": {"propitious", "felicitous", "fortuitous", "sanguine"},
    "austere": {"ascetic", "spartan", "frugal", "penurious", "desolate"},
    "banal": {"hackneyed", "mundane", "prosaic", "vapid", "insipid", "trite"},
    "bashful": {"diffident", "demure", "timorous", "reticent", "taciturn"},
    "benevolent": {"altruistic", "magnanimous", "philanthropic", "munificent"},
    "benign": {"innocuous", "emollient", "pacific", "placid"},
    "bereft": {"destitute", "indigent", "impecunious", "forlorn"},
    "boisterous": {"raucous", "obstreperous", "vociferous", "animated"},
    "bombastic": {"grandiose", "ostentatious", "turgid", "florid", "verbose"},
    "brazen": {"audacious", "impudent", "insolent", "presumptuous"},
    "brusque": {"curt", "laconic", "acerbic", "caustic"},
    "cacophonous": {"strident", "discordant", "raucous"},
    "callous": {"implacable", "obdurate"},
    "canny": {"astute", "adroit", "adept", "cunning", "wily", "judicious"},
    "capacious": {"commodious", "copious"},
    "capricious": {"mercurial", "fickle", "whimsical", "impetuous"},
    "caustic": {"acerbic", "vitriolic", "trenchant", "scathing", "corrosive", "pungent"},
    "cerebral": {"erudite", "didactic", "esoteric"},
    "chronological": {"contemporaneous"},
    "circuitous": {"tortuous", "convoluted", "sinuous", "oblique", "discursive"},
    "circumscribed": {"insular"},
    "circumspect": {"judicious", "prudent", "vigilant", "meticulous", "scrupulous"},
    "clairvoyant": {"prescient"},
    "clandestine": {"covert", "surreptitious", "furtive", "illicit", "devious"},
    "cloying": {"saccharine", "mawkish"},
    "cogent": {"compelling", "eloquent", "incisive", "trenchant", "pithy"},
    "cognizant": {"vigilant", "prescient"},
    "coherent": {"lucid", "pellucid", "eloquent", "cogent"},
    "collateral": {"tangential", "extraneous", "superfluous"},
    "colloquial": {"prosaic", "mundane"},
    "commensurate": {"tantamount", "analogous", "consonant"},
    "commodious": {"capacious", "copious", "opulent", "lavish"},
    "compelling": {"cogent", "eloquent", "incisive"},
    "compliant": {"docile", "amenable", "tractable", "acquiescent", "obsequious", "servile", "submissive", "deferential", "malleable", "pliable"},
    "complicit": {"culpable"},
    "comprehensive": {"copious", "manifold", "multifarious", "myriad"},
    "conciliatory": {"pacific", "affable", "cordial", "genial", "amicable", "amiable"},
    "concise": {"succinct", "pithy", "laconic", "terse"},
    "concomitant": {"collateral", "contemporaneous"},
}


def get_synonyms(word):
    syns = set()
    if word in synonym_sets:
        syns.update(synonym_sets[word])
    for k, v in synonym_sets.items():
        if word in v:
            syns.add(k)
            syns.update(v)
    syns.discard(word)
    return syns


def build_pool(word, curated_candidates):
    pos = pos_map[word]
    syns = get_synonyms(word)
    available = set(all_words_by_pos[pos])
    
    pool = []
    for c in curated_candidates:
        if c in available and c != word and c not in syns:
            pool.append(c)
    
    if len(pool) < 12:
        extras = [w for w in all_words_by_pos[pos] 
                  if w != word and w not in syns and w not in pool]
        random.shuffle(extras)
        pool.extend(extras[:20 - len(pool)])
    
    return pool


# ALL curated distractor pools using ONLY words in the master list
# Each pool has 14+ entries to ensure variety across 8 sentences
curated = {
    # === VERBS (using only words from the 253-word verb list) ===
    # assuage: "to ease, pacify" - distractors should be verbs that DON'T mean ease/soothe
    "assuage": ["exacerbate", "compound", "instigate", "curtail", "stagnate", "deplete",
                "dispel", "deter", "impede", "elicit", "divulge", "fabricate",
                "inundate", "vex", "confound", "perplex", "encumber", "exasperate"],
    
    # atone: "to repent, make amends" 
    "atone": ["transgress", "condone", "deplore", "absolve", "avenge", "repudiate",
              "exonerate", "exculpate", "forsake", "denounce", "repulse", "disavow",
              "relegate", "abscond", "vindicate", "lament", "concede", "repose"],
    
    # atrophy: "to wither away, decay"
    "atrophy": ["cultivate", "augment", "flourish", "propagate", "proliferate",
                "dissipate", "deplete", "languish", "erode", "abase", "efface",
                "wallow", "accrue", "abate", "fester", "congeal", "corrode", "refract"],
    
    # attain: "to achieve, arrive at"
    "attain": ["forfeit", "relinquish", "squander", "aspire", "covet",
               "cultivate", "abdicate", "usurp", "arrogate", "amass",
               "embezzle", "pilfer", "annex", "appropriate", "allocate", "bequeath"],
    
    # attribute: "to credit or assign"
    "attribute": ["disavow", "refute", "allege", "surmise", "construe",
                  "relegate", "designate", "stipulate", "contend", "deduce",
                  "corroborate", "fabricate", "insinuate", "delineate", "prescribe", "divulge"],
    
    # augment: "to add to, expand"
    "augment": ["curtail", "deplete", "abridge", "truncate", "dissipate",
                "cultivate", "compound", "buttress", "corroborate",
                "consolidate", "amass", "propagate", "permeate", "inundate", "encumber"],
    
    # avenge: "to seek revenge"
    "avenge": ["condone", "exonerate", "deplore", "chastise", "reproach",
               "denounce", "admonish", "rebuke", "exculpate", "absolve",
               "prosecute", "implicate", "subjugate", "apprehend", "assail", "repudiate"],
    
    # balk: "to stop, block abruptly"
    "balk": ["accede", "capitulate", "acquiesce", "comply", "relent",
             "vacillate", "concede", "defer", "persist",
             "waver", "dither", "flinch", "recoil", "abide", "aspire", "atone"],
    
    # beguile: "to trick, deceive"
    "beguile": ["repulse", "dissuade", "deter", "captivate", "coerce",
                "blandish", "discomfit", "elude", "confound", "perplex",
                "stupefy", "embellish", "fabricate", "insinuate", "flout", "connive"],
    
    # bequeath: "to pass on, give"
    "bequeath": ["confiscate", "appropriate", "usurp", "arrogate", "allocate",
                 "procure", "annex", "forfeit", "relinquish",
                 "pilfer", "embezzle", "disperse", "relegate", "consign", "amass", "hoard"],
    
    # berate: "to scold vehemently"
    "berate": ["commend", "extol", "exalt", "venerate", "acclaim",
               "appease", "mollify", "placate", "console", "allay",
               "assuage", "cherish", "revere", "laud", "espouse", "nurture"],
    
    # beseech: "to beg, plead"
    "beseech": ["command", "compel", "coerce", "blandish",
                "admonish", "goad", "instigate", "dissuade",
                "rebuke", "reproach", "denounce", "disparage", "exhort", "implore"],
    
    # bilk: "to cheat, defraud"
    "bilk": ["compensate", "bequeath", "allocate", "dispense",
             "connive", "appropriate", "confiscate", "procure",
             "exploit", "pilfer", "embezzle", "arrogate", "usurp", "annex", "extort"],
    
    # blandish: "to coax using flattery"
    "blandish": ["rebuke", "admonish", "chastise", "coerce",
                 "dissuade", "deter", "goad", "exhort",
                 "reproach", "reprove", "disparage", "vilify", "denounce", "decry"],
    
    # buffet: "to strike with force"
    "buffet": ["shield", "nurture", "cultivate", "mollify",
               "inundate", "repulse", "dispel", "deter",
               "encumber", "fetter", "constrain", "impinge", "accost", "assail"],
    
    # burnish: "to polish, shine"
    "burnish": ["deface", "defile", "desecrate", "efface",
                "cultivate", "accentuate", "aggrandize",
                "renovate", "emend", "innovate", "augment", "enhance", "distend", "modulate"],
    
    # buttress: "to support"
    "buttress": ["undermine", "curtail", "subvert", "deplete",
                 "augment", "cultivate", "embellish", "accentuate",
                 "compound", "propagate", "disseminate", "promulgate", "espouse", "advocate"],
    
    # cajole: "to urge, coax"
    "cajole": ["coerce", "compel", "constrain", "rebuke",
               "dissuade", "deter", "admonish", "goad",
               "reproach", "disparage", "reprove", "chastise", "subjugate", "fetter"],
    
    # calibrate: "to set, standardize"
    "calibrate": ["distort", "skew", "refract", "obfuscate",
                  "scrutinize", "modulate", "implement", "prescribe",
                  "delineate", "ascertain", "discern", "surmise", "construe", "recapitulate"],
    
    # capitulate: "to surrender"
    "capitulate": ["resist", "persist", "prevail", "defy",
                   "abdicate", "relinquish", "forsake",
                   "abstain", "dissent", "vacillate", "waver", "dither", "flout", "balk"],
    
    # captivate: "to hold attention"
    "captivate": ["repulse", "deter", "dissuade", "vex",
                  "perplex", "confound", "discomfit", "stupefy",
                  "enamor", "emulate", "immerse", "exasperate", "enervate", "enthrall"],
    
    # carouse: "to party, celebrate"
    "carouse": ["abstain", "languish", "lament", "wallow",
                "deplore", "ruminate", "repose", "eschew",
                "exult", "relish", "indulge", "satiate", "gorge", "immerse"],
    
    # carp: "to annoy, pester"
    "carp": ["commend", "extol", "exalt", "acclaim",
             "harangue", "disparage", "vilify", "denounce",
             "denigrate", "deprecate", "decry", "deride", "rebuke", "vex"],
    
    # catalog: "to list"
    "catalog": ["discard", "neglect", "dismiss", "obfuscate",
                "compile", "tabulate", "chronicle", "annotate",
                "appraise", "survey", "audit", "enumerate", "disseminate", "ascertain"],
    
    # catalyze: "to charge, inspire"
    "catalyze": ["impede", "inhibit", "suppress", "deter",
                 "precipitate", "invigorate", "provoke",
                 "incite", "forestall", "preclude", "quell", "stagnate", "enervate", "foil"],
    
    # cavort: "to leap about, behave boisterously"
    "cavort": ["languish", "stagnate", "wallow", "repose",
               "relish", "exult", "indulge",
               "ruminate", "dither", "vacillate", "oscillate", "undulate", "wane", "abate"],
    
    # chastise: "to criticize severely" -- synonyms: admonish berate rebuke reproach chide upbraid reprove vituperate rail
    "chastise": ["commend", "extol", "exalt", "venerate",
                 "acclaim", "espouse", "nurture", "foster",
                 "mollify", "appease", "placate", "assuage", "allay", "cherish"],
    
    # cherish: "to feel or show affection"
    "cherish": ["despise", "spurn", "disdain", "forsake",
                "covet", "emulate", "nurture", "cultivate",
                "abhor", "deplore", "lament", "condemn", "denounce", "decry"],
    
    # chide: "to voice disapproval" -- synonyms: admonish berate rebuke reproach chastise upbraid reprove vituperate rail
    "chide": ["commend", "extol", "exalt", "acclaim",
              "espouse", "nurture", "foster", "mollify",
              "appease", "placate", "allay", "assuage", "cherish", "venerate"],
    
    # circumvent: "to get around" -- synonyms: elude, evade, forestall, preclude, eschew
    "circumvent": ["confront", "contravene", "transgress", "flout",
                   "obfuscate", "impede", "inhibit", "thwart",
                   "foil", "deter", "dissuade", "subvert", "undermine", "rescind"],
    
    # cleave: "to divide; to stick together"
    "cleave": ["compress", "distend", "disperse", "diffuse",
               "fuse", "merge", "consolidate", "dissolve",
               "dissipate", "transmute", "refract", "modulate", "truncate", "congeal"],
    
    # coagulate: "to thicken, clot"
    "coagulate": ["dissolve", "diffuse", "disperse", "dissipate",
                  "distend", "compress", "transmute", "refract",
                  "precipitate", "compound", "permeate", "saturate", "modulate", "undulate"],
    
    # coalesce: "to fuse into a whole"
    "coalesce": ["fragment", "fracture", "splinter", "disperse",
                 "dissolve", "diffuse", "dissipate", "segregate",
                 "compound", "accumulate", "assimilate", "amass", "aggregate", "converge"],
    
    # coerce: "to force by threat"
    "coerce": ["cajole", "blandish", "beguile", "dissuade",
               "entice", "placate", "mollify", "deter",
               "subjugate", "oppress", "exploit", "manipulate", "intimidate", "suppress"],
    
    # compensate: "to make appropriate payment"
    "compensate": ["forfeit", "deplete", "confiscate", "withhold",
                   "allocate", "bequeath", "dispense", "reimburse",
                   "bestow", "disburse", "appropriate", "procure", "consign", "relegate"],
    
    # complement: "to complete, make perfect"
    "complement": ["undermine", "curtail", "counteract", "impede",
                   "buttress", "corroborate", "validate", "cultivate",
                   "compound", "exacerbate", "mitigate", "mollify", "reconcile", "supplant"],
    
    # compound: "to combine; a combination"
    "compound": ["alleviate", "mitigate", "palliate", "resolve",
                 "curtail", "dispel", "quell", "mollify",
                 "augment", "propagate", "disseminate", "permeate", "diffuse", "consolidate"],
    
    # compress: "to apply pressure, squeeze"
    "compress": ["expand", "distend", "diffuse", "disperse",
                 "consolidate", "encumber", "fetter", "constrain",
                 "condense", "constrict", "compact", "concentrate", "relegate", "immerse"],
    
    # concede: "to accept as valid"
    "concede": ["dispute", "contest", "refute", "assert",
                "repudiate", "dissent", "protest", "contravene",
                "relinquish", "abdicate", "forsake", "abstain", "disavow", "retract"],
    
    # concoct: "to fabricate, make up"
    "concoct": ["disclose", "divulge", "reveal", "uncover",
                "debunk", "corroborate", "substantiate", "validate",
                "embellish", "distort", "exaggerate", "manipulate", "contrive", "improvise"],
    
    # condone: "to pardon, overlook"
    "condone": ["condemn", "denounce", "deplore", "decry",
                "censure", "proscribe", "rebuke", "reproach",
                "reprove", "chastise", "castigate", "vilify", "disparage", "denigrate"],

    # === NOUNS ===
    # asylum: "a place of refuge"
    "asylum": ["bastion", "enclave", "domain", "jurisdiction",
               "outpost", "pinnacle", "nadir", "precipice",
               "morass", "quagmire", "facade", "veneer", "vestige", "artifact"],
    
    # avarice: "excessive greed"
    "avarice": ["largess", "munificence", "magnanimity", "parsimony",
                "opulence", "corpulence", "decadence", "prudence",
                "temperance", "privation", "surfeit", "plenitude", "probity", "rectitude"],
    
    # aversion: "a particular dislike"
    "aversion": ["affinity", "predilection", "proclivity", "inclination",
                 "penchant", "propensity", "rapport", "empathy",
                 "indifference", "apathy", "contempt", "disdain", "umbrage", "indignation"],
    
    # ballad: "a love song"
    "ballad": ["oration", "tirade", "harangue", "polemic",
               "anecdote", "parable", "maxim", "platitude",
               "chronicle", "treatise", "manifesto", "tome", "anthology", "medley"],
    
    # bane: "a burden"
    "bane": ["boon", "windfall", "largess", "amenity",
             "liability", "impediment", "nuisance", "detriment",
             "scourge", "nemesis", "menace", "affliction", "pestilence", "privation"],
    
    # bard: "a poet or singer"
    "bard": ["orator", "demagogue", "potentate", "despot",
             "maverick", "conformist", "incumbent", "neophyte",
             "novice", "patron", "connoisseur", "savant", "interlocutor", "litigant"],
    
    # battery: "a power device; assault"
    "battery": ["arsenal", "cache", "repertoire", "aggregate",
                "medley", "plenitude", "plethora", "surfeit",
                "modicum", "pittance", "increment", "constituent", "inventory", "requisition"],
    
    # behemoth: "something of tremendous power or size"
    "behemoth": ["vestige", "modicum", "pittance", "fragment",
                 "pinnacle", "bastion", "edifice", "zenith",
                 "nadir", "precipice", "epitome", "paragon", "paradigm", "anomaly"],
    
    # bias: "a tendency, prejudice"
    "bias": ["equity", "probity", "rectitude", "veracity",
             "discretion", "prudence", "nuance", "paradigm",
             "anomaly", "paradox", "pretense", "veneer", "facade", "duplicity"],
    
    # blemish: "an imperfection, flaw"
    "blemish": ["accolade", "merit", "asset", "virtue",
                "stigma", "liability", "discrepancy", "anomaly",
                "vestige", "modicum", "pittance", "nuance", "contusion", "laceration"],
    
    # blight: "a plague or disease"
    "blight": ["boon", "windfall", "largess", "amenity",
               "scourge", "pestilence", "calamity", "affliction",
               "detriment", "liability", "morass", "quagmire", "debacle", "maelstrom"],
    
    # boon: "a gift or blessing"
    "boon": ["bane", "liability", "detriment", "impediment",
             "windfall", "amenity", "luxury", "commodity",
             "largess", "surfeit", "plenitude", "bounty", "reprieve", "respite"],
    
    # bourgeois: "a middle-class person"
    "bourgeois": ["aristocrat", "potentate", "despot", "pariah",
                  "maverick", "iconoclast", "partisan",
                  "neophyte", "novice", "incumbent", "demagogue", "insurgent", "anarchist"],
    
    # cacophony: "tremendous noise, disharmonious sound"
    "cacophony": ["cadence", "crescendo", "harmony", "consonance",
                  "tumult", "commotion", "maelstrom", "pandemonium",
                  "oration", "harangue", "tirade", "invective", "dirge", "elegy"],
    
    # cadence: "a rhythm, progression of sound"
    "cadence": ["dissonance", "cacophony", "clamor", "discord",
                "crescendo", "inflection", "modulation", "nuance",
                "platitude", "maxim", "parable", "dirge", "elegy", "ballad"],
    
    # calamity: "an event with disastrous consequences"
    "calamity": ["boon", "windfall", "zenith", "pinnacle",
                 "debacle", "upheaval", "adversity", "tribulation",
                 "maelstrom", "morass", "quagmire", "privation", "duress", "anguish"],
    
    # calumny: "spreading lies to spoil reputation"
    "calumny": ["accolade", "commendation", "acclaim", "plaudits",
                "aspersion", "innuendo", "invective", "tirade",
                "polemic", "harangue", "infamy", "disrepute", "duplicity", "guile"],
    
    # camaraderie: "brotherhood, jovial unity"
    "camaraderie": ["animosity", "enmity", "acrimony", "rancor",
                    "antipathy", "discord", "indifference", "apathy",
                    "solidarity", "cohesion", "affinity", "kinship", "fidelity", "probity"],
    
    # candor: "honesty, frankness"
    "candor": ["duplicity", "guile", "pretense", "veneer",
               "veracity", "probity", "rectitude", "discretion",
               "prudence", "propriety", "decorum", "legerdemain", "ruse", "hypocrisy"],
    
    # canvas: "cloth for painting"
    "canvas": ["palette", "facade", "veneer", "tapestry",
               "artifact", "relic", "vestige", "archive",
               "reservoir", "conduit", "scaffold", "linchpin", "tableau", "panorama"],
    
    # caucus: "a meeting for a common goal"
    "caucus": ["forum", "convention", "tribunal", "hierarchy",
               "congregation", "consensus", "coalition", "faction",
               "mandate", "edict", "injunction", "paradigm", "protocol", "quorum"],
    
    # censure: "harsh criticism"
    "censure": ["accolade", "commendation", "approbation", "acclaim",
                "indictment", "invective", "tirade", "harangue",
                "rebuke", "reproof", "aspersion", "polemic", "injunction", "mandate"],
    
    # chaos: "absolute disorder"
    "chaos": ["harmony", "tranquility", "serenity", "concord",
              "turmoil", "upheaval", "commotion", "discord",
              "debacle", "morass", "quagmire", "conundrum", "travesty", "anomaly"],
    
    # choreography: "arrangement of dances"
    "choreography": ["improvisation", "composition", "medley",
                     "spectacle", "repertoire", "oration",
                     "convention", "hierarchy", "paradigm", "criteria", "nuance", "crescendo"],
    
    # chronicle: "a written history"
    "chronicle": ["anecdote", "parable", "maxim", "platitude",
                  "treatise", "manifesto", "tome", "oration",
                  "tirade", "harangue", "polemic", "invective", "elegy", "dirge"],
    
    # circumlocution: "indirect, wordy language"
    "circumlocution": ["brevity", "conciseness", "oration", "invective",
                       "tirade", "harangue", "diatribe", "polemic",
                       "platitude", "maxim", "nuance", "rhetoric", "grandiloquence", "verbosity"],
    
    # clamor: "loud noise"
    "clamor": ["tranquility", "serenity", "respite", "reprieve",
               "tumult", "commotion", "upheaval", "furor",
               "crescendo", "oration", "harangue", "tirade", "invective", "polemic"],
    
    # clemency: "mercy"
    "clemency": ["retribution", "wrath", "indignation", "acrimony",
                 "reprieve", "respite", "amnesty", "magnanimity",
                 "forbearance", "largess", "benevolence", "dispensation", "absolution", "pardon"],
    
    # clergy: "members of holy orders"
    "clergy": ["laity", "hierarchy", "congregation",
               "convention", "caucus", "faction", "coalition",
               "partisan", "constituent", "incumbent", "demagogue", "potentate", "despot"],
    
    # cobbler: "a shoe repairer"
    "cobbler": ["artisan", "virtuoso", "neophyte", "novice",
                "maven", "gourmand", "conformist", "maverick",
                "incumbent", "litigant", "interlocutor", "surrogate", "partisan", "demagogue"],
    
    # collusion: "secret agreement, conspiracy"
    "collusion": ["candor", "probity", "veracity", "rectitude",
                  "duplicity", "guile", "legerdemain", "ruse",
                  "pretense", "veneer", "hypocrisy", "iniquity", "turpitude", "depravity"],
    
    # colossus: "a gigantic statue or thing"
    "colossus": ["vestige", "modicum", "pittance", "fragment",
                 "pinnacle", "zenith", "nadir", "paradigm",
                 "paragon", "epitome", "precipice", "bastion", "edifice", "monument"],
    
    # combustion: "the act of burning"
    "combustion": ["conflagration", "infusion", "erosion", "attrition",
                   "consumption", "metamorphosis", "corrosion", "accretion",
                   "increment", "modicum", "surfeit", "plenitude", "confluence", "convergence"],
    
    # commendation: "notice of approval" -- synonyms: acclaim accolade approbation kudos plaudits adulation
    "commendation": ["censure", "reproach", "aspersion", "calumny",
                     "rebuke", "indictment", "invective", "tirade",
                     "infamy", "disrepute", "umbrage", "indignation", "wrath", "rancor"],
    
    # complacency: "self-satisfied ignorance of danger"
    "complacency": ["vigilance", "diligence", "prudence", "fortitude",
                    "apathy", "lethargy", "torpor", "inertia",
                    "ennui", "malaise", "indolence", "negligence", "trepidation", "anxiety"],
    
    # compliment: "expression of esteem" -- synonyms: commendation accolade approbation adulation plaudits kudos
    "compliment": ["insult", "reproach", "censure", "aspersion",
                   "calumny", "innuendo", "invective", "tirade",
                   "rebuke", "affront", "indignity", "slight", "slur", "epithet"],
    
    # compunction: "distress from guilt"
    "compunction": ["indifference", "apathy", "nonchalance", "complacency",
                    "remorse", "penitence", "contrition", "regret",
                    "trepidation", "apprehension", "misgiving", "scruple", "equanimity", "forbearance"],
    
    # concord: "harmonious agreement" -- synonyms: accord consensus rapport
    "concord": ["discord", "strife", "dissent", "schism",
                "acrimony", "rancor", "enmity", "antipathy",
                "animosity", "antagonism", "contention", "friction", "impasse", "deadlock"],
    
    # condolence: "expression of sympathy" -- synonyms: consolation empathy pathos
    "condolence": ["jubilation", "elation", "euphoria", "exultation",
                   "umbrage", "indignation", "wrath", "rancor",
                   "acrimony", "antipathy", "apathy", "indifference", "ennui", "malaise"],
    
    # conduit: "a pipe or channel"
    "conduit": ["barrier", "impediment", "obstruction", "blockade",
                "reservoir", "confluence", "precipice", "morass",
                "linchpin", "bastion", "facade", "veneer", "vestige", "artifact"],
    
    # confection: "a sweet, fancy food"
    "confection": ["commodity", "staple", "provision", "requisition",
                   "delicacy", "luxury", "surfeit", "plenitude",
                   "modicum", "pittance", "bounty", "largess", "windfall", "amenity"],
    
    # confidant: "a person entrusted with secrets"
    "confidant": ["adversary", "rival", "antagonist", "litigant",
                  "accomplice", "cohort", "compatriot", "surrogate",
                  "partisan", "maverick", "mentor", "interlocutor", "sycophant", "toady"],

    # === ADJECTIVES ===
    # astute: "very clever, crafty" -- synonyms: canny adroit adept cunning wily acute judicious
    "astute": ["obtuse", "naive", "fatuous", "inept",
               "ingenious", "prudent", "sagacious", "perspicacious",
               "shrewd", "discerning", "circumspect", "meticulous", "pragmatic", "empirical"],
    
    # atypical: "not typical, unusual" -- synonyms: anomalous idiosyncratic aberrant
    "atypical": ["conventional", "orthodox", "mundane", "prosaic",
                 "eccentric", "enigmatic", "esoteric", "arcane",
                 "incongruous", "disparate", "heterogeneous", "multifarious", "protean", "mercurial"],
    
    # audacious: "excessively bold" -- synonyms: brazen intrepid impudent insolent presumptuous impetuous
    "audacious": ["timid", "timorous", "diffident", "demure",
                  "reckless", "rash", "defiant", "truculent",
                  "pugnacious", "brash", "ostentatious", "flagrant", "egregious", "haughty"],
    
    # audible: "able to be heard"
    "audible": ["imperceptible", "obscure", "latent", "dormant",
                "palpable", "tangible", "conspicuous", "ubiquitous",
                "pervasive", "discernible", "pronounced", "vociferous", "strident", "ephemeral"],
    
    # auspicious: "favorable, indicative of good things" -- synonyms: propitious felicitous fortuitous sanguine
    "auspicious": ["ominous", "dire", "adverse", "pernicious",
                   "opportune", "promising", "serendipitous",
                   "portentous", "prescient", "nascent", "inchoate", "seminal", "pivotal", "paramount"],
    
    # austere: "very bare, bleak" -- synonyms: ascetic spartan frugal penurious desolate
    "austere": ["lavish", "opulent", "extravagant", "ornate",
                "barren", "stark", "bleak", "desiccated",
                "rigorous", "strenuous", "stringent", "stoic", "impassive", "dour"],
    
    # banal: "dull, commonplace" -- synonyms: hackneyed mundane prosaic vapid insipid trite
    "banal": ["novel", "innovative", "seminal", "scintillating",
              "pedestrian", "mediocre", "derivative", "perfunctory",
              "staid", "inane", "fatuous", "lackluster", "nondescript", "quotidian"],
    
    # bashful: "shy, excessively timid" -- synonyms: diffident demure timorous reticent taciturn
    "bashful": ["gregarious", "garrulous", "vociferous", "ebullient",
                "aloof", "stoic", "impassive", "phlegmatic",
                "nonchalant", "effervescent", "vivacious", "winsome", "convivial", "genial"],
    
    # benevolent: "marked by goodness" -- synonyms: altruistic magnanimous philanthropic munificent
    "benevolent": ["malevolent", "vindictive", "callous", "nefarious",
                   "compassionate", "gracious", "solicitous", "merciful",
                   "devout", "pious", "sanctimonious", "scrupulous", "reputable", "meritorious"],
    
    # benign: "favorable, not threatening, mild" -- synonyms: innocuous emollient pacific placid
    "benign": ["malignant", "pernicious", "noxious", "deleterious",
               "salubrious", "amiable", "genial", "affable",
               "clement", "temperate", "docile", "inoffensive", "palatable", "moderate"],
    
    # bereft: "devoid of, without" -- synonyms: destitute indigent impecunious forlorn
    "bereft": ["replete", "copious", "profuse", "affluent",
               "hapless", "despondent", "disheartened", "morose",
               "barren", "desiccated", "emaciated", "pallid", "derelict", "defunct"],
    
    # boisterous: "loud, full of energy" -- synonyms: raucous obstreperous vociferous animated
    "boisterous": ["subdued", "sedate", "somber", "tranquil",
                   "exuberant", "ebullient", "vivacious", "effervescent",
                   "gregarious", "convivial", "turbulent", "frenetic", "restive", "fractious"],
    
    # bombastic: "excessively confident, pompous" -- synonyms: grandiose ostentatious turgid florid verbose
    "bombastic": ["understated", "laconic", "succinct", "demure",
                  "pretentious", "garish", "ornate", "elaborate",
                  "overwrought", "flamboyant", "theatrical", "sanctimonious", "imperious", "haughty"],
    
    # brazen: "excessively bold, brash" -- synonyms: audacious impudent insolent presumptuous
    "brazen": ["timid", "bashful", "demure", "reticent",
               "defiant", "flagrant", "egregious", "garish",
               "ostentatious", "reckless", "rash", "truculent", "pugnacious", "haughty"],
    
    # brusque: "short, abrupt, dismissive" -- synonyms: curt laconic acerbic caustic
    "brusque": ["courteous", "gracious", "affable", "genial",
                "terse", "taciturn", "gruff", "dour",
                "peremptory", "imperious", "officious", "surly", "irascible", "contentious"],
    
    # cacophonous: "having a harsh, discordant mixture of sounds" -- synonyms: strident discordant raucous
    "cacophonous": ["melodious", "harmonious", "mellifluous", "euphonic",
                    "vociferous", "obstreperous", "shrill", "noisome",
                    "grating", "jarring", "abrasive", "lugubrious", "boisterous", "garrulous"],
    
    # callous: "harsh, cold, unfeeling" -- synonyms: implacable obdurate
    "callous": ["compassionate", "empathetic", "benevolent", "merciful",
                "ruthless", "pitiless", "indifferent", "apathetic",
                "nonchalant", "stoic", "impassive", "imperious", "obstinate", "truculent"],
    
    # canny: "shrewd, careful" -- synonyms: astute adroit adept cunning wily judicious
    "canny": ["naive", "obtuse", "gullible", "fatuous",
              "prudent", "sagacious", "circumspect", "perspicacious",
              "discerning", "perceptive", "meticulous", "pragmatic", "deliberate", "scrupulous"],
    
    # capacious: "very spacious" -- synonyms: commodious copious
    "capacious": ["cramped", "constricted", "diminutive", "meager",
                  "expansive", "voluminous", "cavernous", "ample",
                  "grandiose", "opulent", "lavish", "palatial", "sprawling", "profuse"],
    
    # capricious: "subject to whim, fickle" -- synonyms: mercurial fickle whimsical impetuous
    "capricious": ["steadfast", "resolute", "adamant", "immutable",
                   "erratic", "volatile", "arbitrary", "spontaneous",
                   "temperamental", "mutable", "protean", "quixotic", "restive", "fractious"],
    
    # caustic: "bitter, biting, acidic" -- synonyms: acerbic vitriolic trenchant scathing corrosive pungent
    "caustic": ["affable", "genial", "cordial", "gracious",
                "mordant", "sardonic", "incisive", "derisive",
                "contemptuous", "pejorative", "ribald", "wry", "sardonic", "sarcastic"],
    
    # cerebral: "related to the intellect" -- synonyms: erudite didactic esoteric
    "cerebral": ["visceral", "emotional", "impulsive", "instinctive",
                 "pedantic", "scholarly", "abstruse", "arcane",
                 "contemplative", "speculative", "empirical", "pragmatic", "utilitarian", "abstract"],
    
    # chronological: "arranged in time order" -- synonyms: contemporaneous
    "chronological": ["arbitrary", "haphazard", "random", "erratic",
                      "sequential", "systematic", "methodical", "cumulative",
                      "concurrent", "consecutive", "cyclical", "periodic", "nominal", "tangential"],
    
    # circuitous: "roundabout" -- synonyms: tortuous convoluted sinuous oblique discursive
    "circuitous": ["direct", "forthright", "explicit", "succinct",
                   "labyrinthine", "serpentine", "meandering", "tangential",
                   "digressive", "protracted", "interminable", "tedious", "elaborate", "intricate"],
    
    # circumscribed: "marked off, bounded" -- synonyms: insular
    "circumscribed": ["boundless", "expansive", "ubiquitous", "pervasive",
                      "constrained", "finite", "delineated", "prescribed",
                      "codified", "regulated", "delimited", "nominal", "marginal", "peripheral"],
    
    # circumspect: "cautious" -- synonyms: judicious prudent vigilant meticulous scrupulous
    "circumspect": ["reckless", "impetuous", "rash", "heedless",
                    "deliberate", "measured", "calculated", "guarded",
                    "fastidious", "punctilious", "wary", "discerning", "sagacious", "canny"],
    
    # clairvoyant: "able to perceive things others cannot" -- synonyms: prescient
    "clairvoyant": ["oblivious", "obtuse", "myopic", "ignorant",
                    "prophetic", "visionary", "intuitive", "perceptive",
                    "astute", "discerning", "sagacious", "uncanny", "enigmatic", "ethereal"],
    
    # clandestine: "secret" -- synonyms: covert surreptitious furtive illicit devious
    "clandestine": ["overt", "transparent", "conspicuous", "manifest",
                    "insidious", "subversive", "nefarious", "perfidious",
                    "duplicitous", "mendacious", "oblique", "obscure", "enigmatic", "esoteric"],
    
    # cloying: "sickeningly sweet" -- synonyms: saccharine mawkish
    "cloying": ["refreshing", "austere", "tart", "pungent",
                "gratuitous", "overwrought", "indulgent", "ostentatious",
                "garish", "florid", "ornate", "lavish", "opulent", "sumptuous"],
    
    # cogent: "intellectually convincing" -- synonyms: compelling eloquent incisive trenchant pithy
    "cogent": ["fallacious", "specious", "dubious", "tenuous",
               "persuasive", "authoritative", "definitive", "empirical",
               "pragmatic", "substantive", "lucid", "articulate", "systematic", "methodical"],
    
    # cognizant: "aware, mindful" -- synonyms: vigilant prescient
    "cognizant": ["oblivious", "ignorant", "heedless", "nonchalant",
                  "conscious", "mindful", "attuned", "perceptive",
                  "discerning", "astute", "conversant", "informed", "sentient", "alert"],
    
    # coherent: "logically consistent" -- synonyms: lucid pellucid eloquent cogent
    "coherent": ["incoherent", "muddled", "garbled", "nebulous",
                 "articulate", "systematic", "methodical", "rational",
                 "intelligible", "orderly", "concise", "succinct", "pithy", "limpid"],
    
    # collateral: "secondary" -- synonyms: tangential extraneous superfluous
    "collateral": ["primary", "paramount", "integral", "salient",
                   "ancillary", "subsidiary", "peripheral", "incidental",
                   "nominal", "supplementary", "auxiliary", "contingent", "concomitant", "implicit"],
    
    # colloquial: "characteristic of informal conversation" -- synonyms: prosaic mundane
    "colloquial": ["formal", "erudite", "elaborate", "florid",
                   "vernacular", "idiomatic", "pedestrian", "provincial",
                   "parochial", "vulgar", "rustic", "quaint", "archaic", "anachronistic"],
    
    # commensurate: "corresponding in size or amount" -- synonyms: tantamount analogous consonant
    "commensurate": ["disproportionate", "exorbitant", "excessive", "inordinate",
                     "proportional", "equivalent", "congruent", "equitable",
                     "nominal", "adequate", "moderate", "meager", "copious", "profuse"],
    
    # commodious: "roomy" -- synonyms: capacious copious opulent lavish
    "commodious": ["cramped", "austere", "spartan", "diminutive",
                   "expansive", "voluminous", "ample", "palatial",
                   "cavernous", "grandiose", "elaborate", "ornate", "resplendent", "sumptuous"],
    
    # compelling: "forceful, demanding attention" -- synonyms: cogent eloquent incisive
    "compelling": ["tepid", "lackluster", "insipid", "vapid",
                   "riveting", "gripping", "engrossing", "formidable",
                   "authoritative", "poignant", "stirring", "sublime", "redoubtable", "salient"],
    
    # compliant: "ready to adapt to wishes" -- synonyms: docile amenable tractable acquiescent obsequious servile submissive deferential malleable pliable
    "compliant": ["defiant", "obstinate", "recalcitrant", "intransigent",
                  "meek", "complacent", "perfunctory", "nonchalant",
                  "indolent", "phlegmatic", "stoic", "impassive", "indifferent", "reluctant"],
    
    # complicit: "being an accomplice" -- synonyms: culpable
    "complicit": ["innocent", "blameless", "exonerated", "absolved",
                  "conniving", "duplicitous", "nefarious", "illicit",
                  "insidious", "devious", "perfidious", "mendacious", "reprehensible", "heinous"],
    
    # comprehensive: "including everything" -- synonyms: copious manifold multifarious myriad
    "comprehensive": ["superficial", "cursory", "perfunctory", "selective",
                      "exhaustive", "extensive", "sweeping", "panoramic",
                      "eclectic", "meticulous", "methodical", "elaborate", "voluminous", "profuse"],
    
    # conciliatory: "friendly, agreeable" -- synonyms: pacific affable cordial genial amicable amiable
    "conciliatory": ["belligerent", "hostile", "combative", "contentious",
                     "diplomatic", "accommodating", "amenable", "deferential",
                     "magnanimous", "gracious", "lenient", "clement", "decorous", "congenial"],
    
    # concise: "brief, direct" -- synonyms: succinct pithy laconic terse
    "concise": ["verbose", "prolix", "discursive", "garrulous",
                "economical", "spare", "truncated", "abridged",
                "incisive", "trenchant", "elliptical", "perfunctory", "cursory", "nominal"],
    
    # concomitant: "accompanying in a subordinate fashion" -- synonyms: collateral contemporaneous
    "concomitant": ["independent", "autonomous", "disparate", "unrelated",
                    "ancillary", "subsidiary", "peripheral", "tangential",
                    "incidental", "contingent", "auxiliary", "supplementary", "implicit", "latent"],
}

# Generate output
output = {}

for word in chunk1_words:
    pos = pos_map[word]
    word_sentences_list = sentences.get(word, [])
    
    if word in curated:
        pool = build_pool(word, curated[word])
    else:
        syns = get_synonyms(word)
        pool = [w for w in all_words_by_pos[pos] if w != word and w not in syns]
        random.shuffle(pool)
        pool = pool[:20]
    
    used_distractor_sets = set()
    entries = []
    
    for i, sent in enumerate(word_sentences_list[:8]):
        attempts = 0
        best = None
        while attempts < 300:
            random.shuffle(pool)
            picked = pool[:3]
            if len(picked) < 3:
                break
            picked_set = frozenset(picked)
            if picked_set not in used_distractor_sets:
                used_distractor_sets.add(picked_set)
                best = list(picked)
                break
            if best is None:
                best = list(picked)
            attempts += 1
        
        if best and len(best) >= 3:
            entries.append([sent] + best[:3])
        else:
            entries.append([sent] + pool[:3])
    
    while len(entries) < 8:
        entries.append(["", "", "", ""])
    
    output[word] = entries

# Validate
print(f"Generated output for {len(output)} words")

errors = 0
for word, entries in output.items():
    if len(entries) != 8:
        print(f"ERROR: {word} has {len(entries)} entries")
        errors += 1
    for i, entry in enumerate(entries):
        if len(entry) != 4:
            print(f"ERROR: {word}[{i}] has {len(entry)} elements")
            errors += 1
        if entry[0] == "":
            print(f"WARNING: {word}[{i}] has empty sentence")
            errors += 1
        for d in entry[1:4]:
            if d and d not in pos_map:
                print(f"ERROR: {word}[{i}]: distractor '{d}' not in word list")
                errors += 1
            elif d and pos_map.get(d) != pos_map[word]:
                print(f"ERROR: {word}[{i}]: distractor '{d}' POS mismatch ({pos_map.get(d)} vs {pos_map[word]})")
                errors += 1

# Check synonyms
syn_errors = 0
for word, entries in output.items():
    syns = get_synonyms(word)
    for i, entry in enumerate(entries):
        for d in entry[1:4]:
            if d and d in syns:
                print(f"SYNONYM ERROR: {word}[{i}]: '{d}' is synonym")
                syn_errors += 1

# Check variety
low_variety = 0
for word, entries in output.items():
    all_d = set()
    for entry in entries:
        for d in entry[1:4]:
            if d:
                all_d.add(d)
    if len(all_d) < 6:
        print(f"LOW VARIETY: {word} uses only {len(all_d)} unique distractors")
        low_variety += 1

print(f"\nValidation errors: {errors}")
print(f"Synonym errors: {syn_errors}")
print(f"Low variety words: {low_variety}")

# Check pool quality - how many curated words survived filtering?
print("\n=== Pool Quality Check ===")
for word in chunk1_words[:10]:
    if word in curated:
        pool = build_pool(word, curated[word])
        curated_count = len([c for c in curated[word] if c in set(all_words_by_pos[pos_map[word]]) and c != word and c not in get_synonyms(word)])
        print(f"  {word}: {curated_count} curated survived, pool size = {len(pool)}")

# Write output
import os
os.makedirs('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp', exist_ok=True)
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_1_output.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nWritten to tmp/chunk_1_output.json")
fsize = os.path.getsize('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_1_output.json')
print(f"File size: {fsize} bytes ({fsize/1024:.1f} KB)")
