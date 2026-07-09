import re
import json
import random

random.seed(44)

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

chunk2_words = [w for w, p, d in words_data[252:378]]

# Synonym sets for chunk 2 words
synonym_sets = {
    # === VERBS ===
    "confound": {"perplex", "vex", "bewilder", "baffle", "discomfit", "stupefy", "flummox"},
    "congeal": {"coagulate", "coalesce", "solidify", "thicken"},
    "connive": {"conspire", "collude", "scheme", "plot"},
    "consecrate": {"sanctify", "dedicate", "bless", "hallow"},
    "consign": {"delegate", "bequeath", "commit", "entrust", "relegate"},
    "constrain": {"restrict", "fetter", "coerce", "inhibit", "restrain", "confine", "compel"},
    "construe": {"interpret", "ascertain", "deduce", "fathom"},
    "consummate": {"complete", "finalize", "conclude", "accomplish", "attain"},
    "contravene": {"violate", "transgress", "flout", "breach", "abrogate"},
    "convene": {"assemble", "gather", "congregate", "summon", "muster"},
    "corroborate": {"substantiate", "validate", "confirm", "buttress", "verify"},
    "counteract": {"neutralize", "negate", "offset", "mitigate", "nullify"},
    "covet": {"desire", "envy", "want", "crave", "aspire"},
    "cultivate": {"nurture", "foster", "develop", "tend", "ameliorate"},
    "curtail": {"reduce", "diminish", "lessen", "abridge", "truncate", "abate"},
    "debase": {"degrade", "demean", "abase", "humiliate", "lower", "defile"},
    "debauch": {"corrupt", "deprave", "degrade", "pervert"},
    "debunk": {"disprove", "discredit", "refute", "expose"},
    "decry": {"denounce", "condemn", "criticize", "deprecate", "disparage", "denigrate", "censure", "deplore"},
    "deface": {"vandalize", "mar", "disfigure", "damage", "desecrate"},
    "defer": {"postpone", "delay", "yield", "submit", "acquiesce", "capitulate", "accede", "concede", "relent"},
    "defile": {"pollute", "contaminate", "desecrate", "sully", "tarnish", "debase", "profane"},
    "delegate": {"assign", "entrust", "consign", "deputize", "allocate"},
    "delineate": {"outline", "describe", "depict", "portray", "sketch", "adumbrate"},
    "demean": {"degrade", "debase", "humiliate", "abase", "belittle", "denigrate"},
    "denigrate": {"disparage", "belittle", "deprecate", "decry", "vilify", "defame", "demean"},
    "denounce": {"condemn", "censure", "decry", "disparage", "rebuke", "reproach", "deplore"},
    "deplore": {"lament", "regret", "condemn", "decry", "denounce", "bemoan"},
    "deprecate": {"belittle", "disparage", "denigrate", "decry", "demean"},
    "deride": {"mock", "ridicule", "scoff", "scorn", "jeer"},
    "desecrate": {"profane", "defile", "violate", "deface"},
    "deter": {"discourage", "prevent", "dissuade", "inhibit"},
    "disavow": {"deny", "disclaim", "renounce", "repudiate", "disown", "abjure", "retract"},
    "discern": {"perceive", "detect", "distinguish", "ascertain", "apprehend"},
    "disclose": {"reveal", "divulge", "expose", "unveil", "evince"},
    "discomfit": {"thwart", "baffle", "confound", "perplex", "foil"},
    "disdain": {"scorn", "despise", "abhor", "spurn"},
    "disparage": {"belittle", "denigrate", "deprecate", "decry", "vilify", "malign", "defame"},
    "dispatch": {"send", "forward", "expedite", "convey"},
    "dispel": {"banish", "scatter", "dissipate", "drive away"},
    "disperse": {"scatter", "dissipate", "distribute", "diffuse", "dispel"},
    "dissemble": {"deceive", "conceal", "pretend", "fabricate", "beguile"},
    "disseminate": {"spread", "propagate", "distribute", "broadcast", "promulgate"},
    "dissent": {"disagree", "object", "protest", "oppose"},
    "dissipate": {"scatter", "disperse", "vanish", "waste", "squander", "dispel", "diffuse"},
    "dissuade": {"discourage", "deter", "prevent"},
    "distend": {"swell", "expand", "inflate", "bloat", "dilate"},
    "diffuse": {"scatter", "spread", "disperse", "disseminate", "dissipate"},

    # === NOUNS ===
    "conflagration": {"fire", "inferno", "blaze", "combustion"},
    "confluence": {"convergence", "meeting", "junction", "merging"},
    "conformist": {"traditionalist", "follower", "bourgeois"},
    "congregation": {"assembly", "gathering", "flock", "caucus", "convention"},
    "congruity": {"harmony", "agreement", "consistency", "accord", "concord"},
    "consensus": {"agreement", "accord", "concord", "unanimity"},
    "consolation": {"comfort", "solace", "condolence", "empathy", "pathos"},
    "constituent": {"component", "element", "part", "ingredient"},
    "consumption": {"use", "utilization", "intake"},
    "contusion": {"bruise", "injury", "wound", "laceration"},
    "conundrum": {"puzzle", "riddle", "enigma", "quandary", "dilemma", "paradox"},
    "convention": {"assembly", "meeting", "gathering", "caucus", "congregation", "forum"},
    "coronation": {"enthronement", "investiture", "inauguration"},
    "corpulence": {"obesity", "fatness", "gluttony"},
    "coup": {"overthrow", "putsch", "revolt"},
    "credulity": {"gullibility", "naivety"},
    "crescendo": {"climax", "peak", "culmination", "cadence"},
    "criteria": {"standards", "benchmarks"},
    "culmination": {"climax", "peak", "pinnacle", "zenith", "apex", "crescendo"},
    "cupidity": {"greed", "avarice", "covetousness", "parsimony"},
    "dearth": {"scarcity", "shortage", "paucity", "lack"},
    "debacle": {"disaster", "fiasco", "catastrophe", "calamity"},
    "demagogue": {"agitator", "rabble-rouser"},
    "demarcation": {"boundary", "border", "separation"},
    "depravity": {"wickedness", "corruption", "iniquity", "turpitude", "immorality"},
    "despot": {"tyrant", "dictator", "autocrat", "potentate"},
    "dialect": {"idiom", "vernacular", "patois"},
    "didacticism": {"moralizing", "preaching"},
    "dirge": {"elegy", "lament", "requiem", "ballad", "knell"},
    "discrepancy": {"inconsistency", "difference", "divergence", "disparity"},
    "discretion": {"prudence", "judgment", "caution", "circumspection"},
    "disrepute": {"infamy", "disgrace", "dishonor"},
    "dissonance": {"discord", "cacophony", "disharmony", "clamor"},

    # === ADJECTIVES ===
    "congenial": {"agreeable", "pleasant", "affable", "amiable", "genial", "cordial", "amicable", "convivial"},
    "consonant": {"harmonious", "concordant", "consistent", "compatible", "congruent", "commensurate"},
    "contemporaneous": {"simultaneous", "concurrent", "coeval", "synchronous", "chronological", "concomitant"},
    "contentious": {"quarrelsome", "combative", "pugnacious", "belligerent", "argumentative", "fractious", "truculent", "irascible"},
    "contrite": {"penitent", "remorseful", "repentant", "sorry", "apologetic"},
    "convivial": {"festive", "sociable", "jovial", "genial", "gregarious", "merry", "congenial", "ebullient"},
    "convoluted": {"complex", "intricate", "tortuous", "circuitous", "labyrinthine", "sinuous"},
    "copious": {"abundant", "plentiful", "profuse", "ample", "lavish", "replete", "capacious", "commodious"},
    "cordial": {"warm", "friendly", "affable", "genial", "amiable", "amicable", "congenial", "conciliatory"},
    "corrosive": {"caustic", "acidic", "erosive", "vitriolic", "acerbic"},
    "cosmopolitan": {"worldly", "sophisticated", "urbane", "cultured"},
    "covert": {"secret", "clandestine", "surreptitious", "furtive", "hidden"},
    "culpable": {"blameworthy", "guilty", "complicit", "reprehensible"},
    "cumulative": {"aggregate", "collective", "increasing", "accruing"},
    "cunning": {"sly", "wily", "crafty", "shrewd", "clever", "astute", "canny", "devious"},
    "cursory": {"superficial", "hasty", "brief", "perfunctory"},
    "curt": {"abrupt", "brusque", "terse", "laconic"},
    "daunting": {"intimidating", "formidable", "fearsome", "overwhelming", "redoubtable", "onerous"},
    "decorous": {"proper", "dignified", "seemly", "appropriate"},
    "defamatory": {"slanderous", "libelous", "scandalous", "scurrilous"},
    "deferential": {"respectful", "submissive", "obsequious", "compliant", "servile"},
    "deft": {"skillful", "adept", "adroit", "nimble", "dexterous", "agile"},
    "defunct": {"extinct", "obsolete", "dead", "inactive", "antiquated", "archaic"},
    "deleterious": {"harmful", "injurious", "detrimental", "noxious", "pernicious", "adverse"},
    "deliberate": {"intentional", "careful", "methodical", "calculated", "meticulous", "assiduous"},
    "demure": {"modest", "shy", "reserved", "bashful", "diffident", "reticent", "coy", "timorous"},
    "derelict": {"abandoned", "neglected", "dilapidated", "forsaken"},
    "derivative": {"unoriginal", "imitative", "secondary", "borrowed", "hackneyed", "trite", "banal"},
    "desiccated": {"dried", "dehydrated", "parched", "arid", "withered"},
    "desolate": {"barren", "bleak", "dreary", "forlorn", "austere", "forsaken", "bereft"},
    "despondent": {"depressed", "dejected", "disheartened", "hopeless", "dispirited", "morose", "forlorn"},
    "destitute": {"impoverished", "indigent", "penurious", "bereft", "impecunious"},
    "devious": {"deceitful", "cunning", "sly", "underhanded", "sneaky", "crafty", "wily", "furtive", "surreptitious", "covert"},
    "diaphanous": {"transparent", "sheer", "gauzy", "ethereal", "translucent"},
    "didactic": {"instructive", "educational", "pedagogic", "moralistic", "preachy", "cerebral"},
    "diffident": {"shy", "timid", "bashful", "demure", "reticent", "timorous"},
    "dilatory": {"slow", "tardy", "procrastinating", "sluggish", "lethargic", "languid", "indolent"},
    "diligent": {"industrious", "assiduous", "hardworking", "meticulous", "conscientious", "sedulous", "painstaking", "scrupulous"},
    "diminutive": {"small", "tiny", "miniature", "minute", "petite", "meager"},
    "disaffected": {"discontented", "rebellious", "disloyal", "estranged", "alienated", "disgruntled"},
    "discordant": {"dissonant", "clashing", "cacophonous", "inharmonious", "strident", "raucous"},
    "discursive": {"rambling", "digressive", "circuitous", "meandering", "verbose", "convoluted", "prolix"},
    "disgruntled": {"dissatisfied", "discontented", "disaffected", "aggrieved", "resentful"},
    "disheartened": {"discouraged", "dispirited", "despondent", "dejected", "demoralized"},
    "disparate": {"different", "dissimilar", "diverse", "heterogeneous", "distinct", "incongruous"},
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


# Curated distractor pools for every chunk 2 word
curated = {
    # ===================== NOUNS =====================

    # conflagration: "great fire"
    "conflagration": ["combustion", "eruption", "calamity", "debacle",
                      "maelstrom", "upheaval", "tumult", "pandemonium",
                      "infusion", "confection", "conundrum", "morass",
                      "quagmire", "travesty", "clamor", "crescendo"],

    # confluence: "a gathering together"
    "confluence": ["divergence", "discrepancy", "schism", "paradox",
                   "congruity", "consensus", "culmination", "aggregate",
                   "medley", "accretion", "increment", "precipice",
                   "paradigm", "criteria", "hierarchy", "morass"],

    # conformist: "one who behaves like others"
    "conformist": ["maverick", "iconoclast", "insurgent", "anarchist",
                   "partisan", "incumbent", "neophyte", "novice",
                   "demagogue", "sycophant", "potentate", "despot",
                   "litigant", "interlocutor", "surrogate", "toady"],

    # congregation: "a gathering, usually religious"
    "congregation": ["hierarchy", "faction", "coalition", "tribunal",
                     "caucus", "clergy", "constituency", "quorum",
                     "contingent", "partisan", "cohort", "convention",
                     "forum", "arbitration", "mandate", "edict"],

    # congruity: "quality of being in agreement"
    "congruity": ["discord", "discrepancy", "paradox", "anomaly",
                  "rapport", "propriety", "probity", "rectitude",
                  "nuance", "criteria", "paradigm", "antithesis",
                  "schism", "analogy", "juxtaposition", "preponderance"],

    # consensus: "an agreement of opinion"
    "consensus": ["discord", "schism", "dissent", "impasse",
                  "mandate", "edict", "decree", "injunction",
                  "paradigm", "criteria", "precedent", "arbitration",
                  "tribunal", "hierarchy", "coalition", "faction"],

    # consolation: "an act of comforting"
    "consolation": ["affliction", "tribulation", "anguish", "adversity",
                    "reprieve", "respite", "clemency", "absolution",
                    "restitution", "indulgence", "umbrage", "indignation",
                    "wrath", "rancor", "apathy", "ennui"],

    # constituent: "an essential part"
    "constituent": ["aggregate", "surplus", "deficit", "remnant",
                    "increment", "modicum", "pittance", "plenitude",
                    "liability", "impediment", "linchpin", "vestige",
                    "requisition", "commodity", "inventory", "cache"],

    # consumption: "the act of consuming"
    "consumption": ["accretion", "increment", "surfeit", "plenitude",
                    "depletion", "privation", "modicum", "pittance",
                    "erosion", "attrition", "combustion", "infusion",
                    "metamorphosis", "conflagration", "confluence", "expenditure"],

    # contusion: "bruise, injury"
    "contusion": ["laceration", "affliction", "malaise", "atrophy",
                  "salve", "panacea", "analgesic", "remedy",
                  "abrasion", "blemish", "stigma", "vestige",
                  "ailment", "infirmity", "trauma", "lesion"],

    # conundrum: "puzzle, problem"
    "conundrum": ["panacea", "axiom", "maxim", "platitude",
                  "impasse", "morass", "quagmire", "debacle",
                  "discrepancy", "anomaly", "antithesis", "nuance",
                  "criteria", "paradigm", "precedent", "conjecture"],

    # convention: "an assembly; a rule or custom"
    "convention": ["schism", "faction", "hierarchy", "tribunal",
                   "caucus", "forum", "coalition", "mandate",
                   "edict", "injunction", "precedent", "criteria",
                   "paradigm", "arbitration", "congregation", "quorum"],

    # coronation: "the act of crowning"
    "coronation": ["abdication", "inauguration", "arbitration", "hegemony",
                   "coup", "mandate", "edict", "decree",
                   "tribunal", "hierarchy", "convention", "culmination",
                   "pageantry", "spectacle", "oration", "salutation"],

    # corpulence: "extreme fatness"
    "corpulence": ["emaciation", "privation", "opulence", "decadence",
                   "temperance", "sobriety", "austerity", "frugality",
                   "gluttony", "surfeit", "plenitude", "modicum",
                   "pittance", "malaise", "lethargy", "torpor"],

    # coup: "a brilliant act; overthrow of government"
    "coup": ["debacle", "travesty", "fiasco", "impasse",
             "hegemony", "mandate", "edict", "decree",
             "arbitration", "coalition", "faction", "schism",
             "coronation", "abdication", "insurgent", "anarchy"],

    # credulity: "readiness to believe"
    "credulity": ["skepticism", "prudence", "sagacity", "acumen",
                  "duplicity", "guile", "hypocrisy", "pretense",
                  "veracity", "probity", "candor", "rectitude",
                  "naivete", "folly", "hubris", "temerity"],

    # crescendo: "steady increase in intensity"
    "crescendo": ["nadir", "lull", "respite", "reprieve",
                  "cadence", "cacophony", "clamor", "dissonance",
                  "zenith", "pinnacle", "epitome", "climax",
                  "oration", "dirge", "elegy", "ballad"],

    # criteria: "standards for judgment"
    "criteria": ["anomaly", "paradox", "paradigm", "precedent",
                 "maxim", "platitude", "mandate", "edict",
                 "nuance", "discrepancy", "propriety", "probity",
                 "convention", "hierarchy", "arbitration", "protocol"],

    # culmination: "the climax"
    "culmination": ["nadir", "inception", "genesis", "antecedent",
                    "zenith", "pinnacle", "epitome", "paragon",
                    "debacle", "travesty", "morass", "quagmire",
                    "paradigm", "precedent", "harbinger", "portent"],

    # cupidity: "greed, strong desire"
    "cupidity": ["largess", "munificence", "magnanimity", "temperance",
                 "opulence", "decadence", "gluttony", "surfeit",
                 "privation", "probity", "rectitude", "prudence",
                 "temerity", "effrontery", "hubris", "ardor"],

    # dearth: "a lack, scarcity"
    "dearth": ["surfeit", "plethora", "plenitude", "abundance",
               "modicum", "pittance", "increment", "morass",
               "privation", "adversity", "duress", "tribulation",
               "largess", "bounty", "windfall", "requisition"],

    # debacle: "a disastrous failure"
    "debacle": ["triumph", "coup", "zenith", "pinnacle",
                "morass", "quagmire", "maelstrom", "travesty",
                "adversity", "tribulation", "conundrum", "impasse",
                "upheaval", "turmoil", "pandemonium", "tumult"],

    # demagogue: "leader appealing to prejudices"
    "demagogue": ["arbiter", "diplomat", "maverick", "iconoclast",
                  "potentate", "despot", "insurgent", "partisan",
                  "incumbent", "neophyte", "litigant", "interlocutor",
                  "sycophant", "toady", "conformist", "surrogate"],

    # demarcation: "marking of boundaries"
    "demarcation": ["confluence", "convergence", "merger", "amalgamation",
                    "criteria", "paradigm", "precedent", "convention",
                    "jurisdiction", "hegemony", "hierarchy", "mandate",
                    "discrepancy", "nuance", "distinction", "antithesis"],

    # depravity: "wickedness"
    "depravity": ["probity", "rectitude", "virtue", "magnanimity",
                  "duplicity", "guile", "hypocrisy", "collusion",
                  "legerdemain", "ruse", "pretense", "iniquity",
                  "turpitude", "infamy", "disrepute", "effrontery"],

    # despot: "one with total brutal power"
    "despot": ["maverick", "arbiter", "conformist", "neophyte",
               "incumbent", "partisan", "insurgent", "demagogue",
               "litigant", "interlocutor", "sycophant", "novice",
               "iconoclast", "anarchist", "surrogate", "toady"],

    # dialect: "a variation of a language"
    "dialect": ["oration", "tirade", "harangue", "invective",
                "maxim", "platitude", "anecdote", "parable",
                "polemic", "treatise", "manifesto", "chronicle",
                "rhetoric", "vernacular", "jargon", "lexicon"],

    # didacticism: "the quality of being overly moralistic or instructional"
    "didacticism": ["grandiloquence", "verbosity", "circumlocution", "prolixity",
                    "propriety", "rectitude", "probity", "prudence",
                    "hypocrisy", "pretense", "duplicity", "pedantry",
                    "rhetoric", "iconoclasm", "sobriety", "temperance"],

    # dirge: "a mournful song"
    "dirge": ["oration", "tirade", "harangue", "invective",
              "ballad", "anthem", "maxim", "platitude",
              "anecdote", "parable", "polemic", "treatise",
              "chronicle", "manifesto", "medley", "cacophony"],

    # discrepancy: "difference, failure to correspond"
    "discrepancy": ["congruity", "consensus", "accord", "harmony",
                    "anomaly", "paradox", "nuance", "antithesis",
                    "criteria", "paradigm", "precedent", "aberration",
                    "deviation", "dichotomy", "juxtaposition", "analogy"],

    # discretion: "reserve in speech or action; good judgment"
    "discretion": ["temerity", "effrontery", "audacity", "hubris",
                   "prudence", "sagacity", "acumen", "temperance",
                   "propriety", "probity", "rectitude", "decorum",
                   "candor", "veracity", "sobriety", "fortitude"],

    # disrepute: "state of being held in low regard"
    "disrepute": ["renown", "acclaim", "eminence", "accolade",
                  "infamy", "notoriety", "stigma", "ignominy",
                  "calumny", "aspersion", "censure", "reproach",
                  "turpitude", "depravity", "iniquity", "travesty"],

    # dissonance: "lack of harmony or consistency"
    "dissonance": ["concord", "accord", "rapport", "harmony",
                   "cacophony", "clamor", "tumult", "pandemonium",
                   "discord", "acrimony", "rancor", "animosity",
                   "paradox", "anomaly", "discrepancy", "antithesis"],

    # ===================== VERBS =====================

    # confound: "to frustrate, confuse" -- synonyms: perplex, vex, discomfit, stupefy
    "confound": ["elucidate", "clarify", "illuminate", "validate",
                 "exasperate", "encumber", "impede", "thwart",
                 "obfuscate", "fabricate", "refute", "debunk",
                 "bewilder", "deter", "inhibit", "forestall"],

    # congeal: "to thicken into a solid" -- synonyms: coagulate, coalesce
    "congeal": ["dissolve", "diffuse", "disperse", "dissipate",
                "distend", "compress", "transmute", "refract",
                "precipitate", "compound", "permeate", "saturate",
                "modulate", "undulate", "erode", "corrode"],

    # connive: "to plot, scheme"
    "connive": ["divulge", "disclose", "denounce", "expose",
                "fabricate", "dissemble", "embezzle", "bilk",
                "collude", "implicate", "instigate", "abet",
                "exploit", "manipulate", "contravene", "transgress"],

    # consecrate: "to dedicate to a holy purpose"
    "consecrate": ["desecrate", "defile", "profane", "abrogate",
                   "venerate", "revere", "exalt", "extol",
                   "inaugurate", "ratify", "promulgate", "sanction",
                   "decree", "mandate", "implement", "espouse"],

    # consign: "to give over to another's care" -- synonyms: delegate, bequeath, relegate
    "consign": ["confiscate", "appropriate", "usurp", "arrogate",
                "procure", "allocate", "dispense", "requisition",
                "pilfer", "embezzle", "hoard", "amass",
                "relinquish", "forfeit", "annex", "withhold"],

    # constrain: "to forcibly restrict" -- synonyms: fetter, coerce, inhibit, compel
    "constrain": ["liberate", "emancipate", "enfranchise", "absolve",
                  "subjugate", "oppress", "encumber", "impede",
                  "curtail", "preclude", "forestall", "deter",
                  "compel", "relegate", "exile", "confine"],

    # construe: "to interpret" -- synonyms: ascertain, deduce, fathom
    "construe": ["obfuscate", "distort", "fabricate", "embellish",
                 "surmise", "allege", "contend", "postulate",
                 "insinuate", "stipulate", "delineate", "prescribe",
                 "speculate", "conjecture", "extrapolate", "interpolate"],

    # consummate: "to complete a deal or marriage"
    "consummate": ["abort", "forsake", "relinquish", "abandon",
                   "inaugurate", "implement", "ratify", "enact",
                   "expedite", "facilitate", "cultivate", "reconcile",
                   "instigate", "catalyze", "precipitate", "undertake"],

    # contravene: "to contradict, violate" -- synonyms: transgress, flout, abrogate
    "contravene": ["uphold", "ratify", "validate", "corroborate",
                   "undermine", "subvert", "rescind", "annul",
                   "circumvent", "evade", "elude", "preclude",
                   "repudiate", "revoke", "rebuke", "denounce"],

    # convene: "to call together"
    "convene": ["disperse", "disband", "segregate", "scatter",
                "delegate", "dispatch", "deploy", "allocate",
                "mobilize", "orchestrate", "inaugurate", "preside",
                "reconcile", "arbitrate", "mediate", "promulgate"],

    # corroborate: "to support with evidence" -- synonyms: substantiate, validate, buttress, verify
    "corroborate": ["refute", "debunk", "undermine", "repudiate",
                    "allege", "contend", "surmise", "postulate",
                    "fabricate", "embellish", "insinuate", "construe",
                    "stipulate", "prescribe", "extrapolate", "conjecture"],

    # counteract: "to neutralize" -- synonyms: mitigate, negate, offset
    "counteract": ["exacerbate", "compound", "augment", "amplify",
                   "curtail", "forestall", "preclude", "deter",
                   "mollify", "placate", "appease", "assuage",
                   "buttress", "bolster", "reconcile", "remediate"],

    # covet: "to desire enviously"
    "covet": ["spurn", "disdain", "forsake", "relinquish",
              "relish", "cherish", "revere", "emulate",
              "hoard", "amass", "pilfer", "embezzle",
              "squander", "forfeit", "procure", "usurp"],

    # cultivate: "to nurture, improve" -- synonyms: nurture, foster, ameliorate
    "cultivate": ["neglect", "forsake", "abandon", "squander",
                  "propagate", "disseminate", "augment", "embellish",
                  "refurbish", "renovate", "burnish", "innovate",
                  "implement", "expedite", "facilitate", "sustain"],

    # curtail: "to lessen, reduce" -- synonyms: abridge, truncate, abate, diminish
    "curtail": ["augment", "aggrandize", "amplify", "compound",
                "bolster", "buttress", "propagate", "proliferate",
                "forestall", "preclude", "impede", "deter",
                "deplete", "dissipate", "erode", "stagnate"],

    # debase: "to lower quality or esteem" -- synonyms: degrade, demean, abase, humiliate, defile
    "debase": ["exalt", "venerate", "extol", "revere",
               "burnish", "embellish", "adorn", "cultivate",
               "aggrandize", "augment", "refurbish", "renovate",
               "disparage", "vilify", "condemn", "corrode"],

    # debauch: "to corrupt via sensual pleasures"
    "debauch": ["edify", "enlighten", "nurture", "consecrate",
                "indulge", "satiate", "gorge", "wallow",
                "exploit", "subjugate", "coerce", "beguile",
                "blandish", "entice", "enthrall", "enamor"],

    # debunk: "to expose falseness" -- synonyms: refute, disprove, discredit
    "debunk": ["corroborate", "validate", "substantiate", "ratify",
               "fabricate", "concoct", "embellish", "dissemble",
               "scrutinize", "discern", "ascertain", "elucidate",
               "expose", "divulge", "disclose", "promulgate"],

    # decry: "to criticize openly" -- synonyms: denounce, condemn, deprecate, disparage, denigrate, censure, deplore
    "decry": ["commend", "extol", "exalt", "venerate",
              "acclaim", "laud", "champion", "espouse",
              "rebuke", "reproach", "chastise", "admonish",
              "repudiate", "impugn", "castigate", "assail"],

    # deface: "to ruin appearance" -- synonyms: desecrate, vandalize
    "deface": ["adorn", "burnish", "embellish", "refurbish",
               "renovate", "cultivate", "accentuate", "ornament",
               "corrode", "erode", "efface", "obliterate",
               "defile", "impair", "tarnish", "devastate"],

    # defer: "to postpone; to yield to wisdom" -- synonyms: acquiesce, capitulate, accede, concede, relent
    "defer": ["expedite", "hasten", "accelerate", "precipitate",
              "resist", "defy", "flout", "contravene",
              "dissent", "protest", "abstain", "balk",
              "delegate", "dispatch", "implement", "consummate"],

    # defile: "to make unclean or impure" -- synonyms: desecrate, profane, debase, pollute, contaminate
    "defile": ["consecrate", "venerate", "sanctify", "revere",
               "burnish", "refurbish", "renovate", "cultivate",
               "adorn", "embellish", "accentuate", "ornament",
               "corrode", "erode", "efface", "obliterate"],

    # delegate: "to hand over responsibility" -- synonyms: consign, allocate, entrust
    "delegate": ["arrogate", "usurp", "confiscate", "appropriate",
                 "retain", "hoard", "monopolize", "amass",
                 "prescribe", "mandate", "decree", "stipulate",
                 "implement", "expedite", "facilitate", "administer"],

    # delineate: "to describe, outline" -- synonyms: adumbrate, depict, portray
    "delineate": ["obfuscate", "obscure", "confound", "distort",
                  "articulate", "elucidate", "expound", "stipulate",
                  "construe", "surmise", "conjecture", "postulate",
                  "prescribe", "recapitulate", "annotate", "catalog"],

    # demean: "to lower status or stature" -- synonyms: degrade, debase, abase, humiliate, belittle, denigrate
    "demean": ["exalt", "venerate", "extol", "revere",
               "disparage", "chastise", "reproach", "rebuke",
               "subjugate", "coerce", "oppress", "exploit",
               "aggrandize", "embellish", "adorn", "burnish"],

    # denigrate: "to belittle" -- synonyms: disparage, deprecate, decry, vilify, defame, demean
    "denigrate": ["commend", "extol", "exalt", "laud",
                  "rebuke", "chastise", "reproach", "admonish",
                  "impugn", "assail", "castigate", "harangue",
                  "aggrandize", "embellish", "burnish", "cultivate"],

    # denounce: "to criticize publicly" -- synonyms: condemn, censure, decry, disparage, rebuke, reproach, deplore
    "denounce": ["commend", "extol", "exalt", "acclaim",
                 "espouse", "advocate", "champion", "endorse",
                 "vindicate", "exonerate", "absolve", "acquit",
                 "laud", "venerate", "revere", "cherish"],

    # deplore: "to feel sorrow or disapproval" -- synonyms: lament, denounce, decry, condemn
    "deplore": ["commend", "extol", "exalt", "acclaim",
                "relish", "cherish", "revere", "venerate",
                "espouse", "champion", "advocate", "endorse",
                "condone", "sanction", "absolve", "vindicate"],

    # deprecate: "to belittle, depreciate" -- synonyms: disparage, denigrate, decry, belittle, demean
    "deprecate": ["commend", "extol", "exalt", "laud",
                  "aggrandize", "embellish", "burnish", "cultivate",
                  "rebuke", "chastise", "reproach", "admonish",
                  "espouse", "champion", "advocate", "endorse"],

    # deride: "to laugh at mockingly"
    "deride": ["commend", "extol", "exalt", "acclaim",
               "reproach", "chastise", "rebuke", "admonish",
               "deplore", "lament", "condemn", "censure",
               "venerate", "revere", "cherish", "relish"],

    # desecrate: "to violate sacredness" -- synonyms: profane, defile, deface
    "desecrate": ["consecrate", "venerate", "revere", "sanctify",
                  "adorn", "embellish", "burnish", "cultivate",
                  "efface", "obliterate", "corrode", "erode",
                  "exploit", "pillage", "plunder", "ravage"],

    # deter: "to discourage, prevent" -- synonyms: dissuade, discourage, inhibit
    "deter": ["incite", "instigate", "goad", "provoke",
              "catalyze", "foster", "cultivate", "promote",
              "impede", "forestall", "preclude", "thwart",
              "compel", "coerce", "constrain", "subjugate"],

    # disavow: "to deny knowledge or responsibility" -- synonyms: repudiate, disclaim, abjure, retract
    "disavow": ["espouse", "advocate", "champion", "endorse",
                "allege", "contend", "assert", "proclaim",
                "corroborate", "validate", "substantiate", "ratify",
                "condone", "sanction", "absolve", "vindicate"],

    # discern: "to perceive, detect" -- synonyms: ascertain, apprehend, perceive
    "discern": ["overlook", "disregard", "neglect", "ignore",
                "surmise", "conjecture", "speculate", "postulate",
                "scrutinize", "appraise", "calibrate", "assess",
                "obfuscate", "distort", "fabricate", "embellish"],

    # disclose: "to reveal" -- synonyms: divulge, expose, evince
    "disclose": ["conceal", "obfuscate", "suppress", "withhold",
                 "dissemble", "fabricate", "embellish", "concoct",
                 "insinuate", "allege", "contend", "surmise",
                 "promulgate", "disseminate", "propagate", "proclaim"],

    # discomfit: "to thwart, baffle" -- synonyms: confound, perplex, foil, thwart
    "discomfit": ["placate", "mollify", "appease", "console",
                  "exasperate", "vex", "encumber", "impede",
                  "elude", "circumvent", "deter", "forestall",
                  "stupefy", "bewilder", "obfuscate", "flummox"],

    # disdain: "to scorn" -- synonyms: abhor, spurn, despise
    "disdain": ["cherish", "revere", "venerate", "extol",
                "covet", "relish", "emulate", "adore",
                "deplore", "condemn", "denounce", "censure",
                "rebuke", "reproach", "chastise", "disparage"],

    # disparage: "to criticize or speak ill of" -- synonyms: denigrate, deprecate, decry, vilify, defame, belittle
    "disparage": ["commend", "extol", "exalt", "acclaim",
                  "rebuke", "chastise", "reproach", "admonish",
                  "venerate", "revere", "cherish", "relish",
                  "espouse", "champion", "advocate", "endorse"],

    # dispatch: "to send off"
    "dispatch": ["detain", "withhold", "intercept", "impede",
                 "convene", "summon", "deploy", "mobilize",
                 "expedite", "delegate", "relegate", "consign",
                 "allocate", "procure", "requisition", "distribute"],

    # dispel: "to drive away, scatter" -- synonyms: dissipate, banish
    "dispel": ["compound", "exacerbate", "augment", "propagate",
               "cultivate", "foster", "nurture", "engender",
               "permeate", "inundate", "saturate", "proliferate",
               "accumulate", "amass", "consolidate", "aggregate"],

    # disperse: "to scatter" -- synonyms: dissipate, diffuse, dispel
    "disperse": ["convene", "congregate", "amass", "consolidate",
                 "propagate", "disseminate", "promulgate", "deploy",
                 "accumulate", "aggregate", "compile", "hoard",
                 "delegate", "allocate", "distribute", "dispatch"],

    # dissemble: "to conceal, fake" -- synonyms: fabricate, beguile, deceive
    "dissemble": ["disclose", "divulge", "expose", "reveal",
                  "embellish", "exaggerate", "distort", "obfuscate",
                  "connive", "collude", "conspire", "exploit",
                  "insinuate", "allege", "contend", "surmise"],

    # disseminate: "to spread widely" -- synonyms: propagate, distribute, promulgate
    "disseminate": ["suppress", "withhold", "conceal", "censor",
                    "compile", "catalog", "archive", "consolidate",
                    "permeate", "inundate", "saturate", "proliferate",
                    "dispatch", "deploy", "delegate", "allocate"],

    # dissent: "to disagree" -- synonyms: object, protest, oppose
    "dissent": ["accede", "acquiesce", "concede", "comply",
                "concur", "endorse", "ratify", "sanction",
                "capitulate", "relent", "defer", "abstain",
                "balk", "vacillate", "waver", "equivocate"],

    # dissipate: "to disappear; to waste" -- synonyms: scatter, disperse, vanish, squander
    "dissipate": ["accumulate", "amass", "consolidate", "aggregate",
                  "compound", "augment", "propagate", "proliferate",
                  "cultivate", "foster", "nurture", "sustain",
                  "hoard", "stockpile", "conserve", "bolster"],

    # dissuade: "to persuade someone not to do something" -- synonyms: deter, discourage
    "dissuade": ["cajole", "blandish", "exhort", "goad",
                 "instigate", "incite", "provoke", "compel",
                 "coerce", "entice", "beguile", "induce",
                 "advocate", "espouse", "champion", "endorse"],

    # distend: "to swell out"
    "distend": ["compress", "constrict", "curtail", "diminish",
                "augment", "amplify", "proliferate", "propagate",
                "inflate", "dilate", "expand", "engorge",
                "erode", "corrode", "dissipate", "deplete"],

    # diffuse: "to scatter; not concentrated" -- synonyms: scatter, spread, disperse, disseminate, dissipate
    "diffuse": ["concentrate", "consolidate", "compress", "condense",
                "permeate", "inundate", "saturate", "proliferate",
                "propagate", "augment", "compound", "amplify",
                "accumulate", "amass", "aggregate", "hoard"],

    # ===================== ADJECTIVES =====================

    # congenial: "pleasantly agreeable" -- synonyms: affable, amiable, genial, cordial, amicable, convivial
    "congenial": ["surly", "cantankerous", "irascible", "petulant",
                  "gregarious", "ebullient", "effervescent", "vivacious",
                  "decorous", "gracious", "solicitous", "diplomatic",
                  "nonchalant", "phlegmatic", "aloof", "taciturn"],

    # consonant: "in harmony" -- synonyms: harmonious, concordant, commensurate
    "consonant": ["discordant", "incongruous", "disparate", "contentious",
                  "congruent", "analogous", "tantamount", "equivalent",
                  "integral", "paramount", "salient", "nominal",
                  "tangential", "extraneous", "superfluous", "ancillary"],

    # contemporaneous: "existing during the same time" -- synonyms: chronological, concomitant
    "contemporaneous": ["antiquated", "archaic", "antediluvian", "primeval",
                        "nascent", "inchoate", "ephemeral", "transient",
                        "extant", "perennial", "perpetual", "immutable",
                        "anachronistic", "obsolete", "defunct", "nominal"],

    # contentious: "tending to quarrel" -- synonyms: quarrelsome, pugnacious, belligerent, fractious, truculent, irascible
    "contentious": ["conciliatory", "amicable", "affable", "pacific",
                    "obstinate", "intransigent", "recalcitrant", "defiant",
                    "officious", "imperious", "haughty", "presumptuous",
                    "petulant", "querulous", "peevish", "acerbic"],

    # contrite: "penitent, eager to be forgiven" -- synonyms: penitent, remorseful, repentant
    "contrite": ["impenitent", "defiant", "obstinate", "brazen",
                 "despondent", "morose", "wistful", "forlorn",
                 "solicitous", "deferential", "submissive", "meek",
                 "indifferent", "nonchalant", "complacent", "stoic"],

    # convivial: "characterized by feasting or merriment" -- synonyms: genial, gregarious, ebullient, congenial
    "convivial": ["somber", "austere", "morose", "taciturn",
                  "animated", "vivacious", "effervescent", "exuberant",
                  "boisterous", "raucous", "vociferous", "jubilant",
                  "nonchalant", "phlegmatic", "aloof", "stoic"],

    # convoluted: "intricate, complicated" -- synonyms: tortuous, circuitous, labyrinthine, sinuous
    "convoluted": ["lucid", "pellucid", "succinct", "concise",
                   "elaborate", "ornate", "byzantine", "intricate",
                   "abstruse", "esoteric", "arcane", "nebulous",
                   "tedious", "interminable", "protracted", "discursive"],

    # copious: "profuse, abundant" -- synonyms: abundant, profuse, replete, capacious, commodious, lavish
    "copious": ["meager", "scant", "sparse", "paltry",
                "voluminous", "comprehensive", "exhaustive", "myriad",
                "superfluous", "exorbitant", "gratuitous", "nominal",
                "diminutive", "modicum", "pittance", "trivial"],

    # cordial: "warm, affectionate" -- synonyms: affable, genial, amiable, amicable, congenial, conciliatory
    "cordial": ["brusque", "curt", "aloof", "surly",
                "solicitous", "gracious", "convivial", "gregarious",
                "deferential", "obsequious", "effusive", "unctuous",
                "nonchalant", "phlegmatic", "taciturn", "stoic"],

    # corrosive: "having tendency to erode" -- synonyms: caustic, vitriolic, acerbic
    "corrosive": ["benign", "innocuous", "emollient", "palatable",
                  "pernicious", "deleterious", "noxious", "insidious",
                  "pungent", "scathing", "mordant", "trenchant",
                  "abrasive", "incendiary", "volatile", "noisome"],

    # cosmopolitan: "sophisticated, worldly"
    "cosmopolitan": ["provincial", "parochial", "insular", "rustic",
                     "erudite", "urbane", "eclectic", "cultivated",
                     "affluent", "opulent", "ostentatious", "pretentious",
                     "pragmatic", "empirical", "utilitarian", "secular"],

    # covert: "secretly engaged in" -- synonyms: clandestine, surreptitious, furtive
    "covert": ["overt", "manifest", "conspicuous", "patent",
               "insidious", "devious", "perfidious", "nefarious",
               "oblique", "obscure", "enigmatic", "esoteric",
               "latent", "dormant", "implicit", "tacit"],

    # culpable: "deserving blame" -- synonyms: complicit, reprehensible
    "culpable": ["blameless", "innocent", "exonerated", "acquitted",
                 "negligent", "remiss", "derelict", "perfidious",
                 "heinous", "nefarious", "egregious", "odious",
                 "penitent", "contrite", "repentant", "vindicated"],

    # cumulative: "increasing, building upon itself"
    "cumulative": ["diminishing", "nominal", "negligible", "marginal",
                   "comprehensive", "exhaustive", "copious", "voluminous",
                   "incremental", "successive", "consecutive", "progressive",
                   "aggregate", "superfluous", "exorbitant", "manifest"],

    # cunning: "sly, clever at deceit" -- synonyms: wily, crafty, astute, canny, devious
    "cunning": ["obtuse", "naive", "gullible", "fatuous",
                "ingenious", "shrewd", "sagacious", "perspicacious",
                "perfidious", "mendacious", "duplicitous", "insidious",
                "pragmatic", "judicious", "circumspect", "meticulous"],

    # cursory: "brief, superficial" -- synonyms: perfunctory, superficial, hasty
    "cursory": ["meticulous", "exhaustive", "comprehensive", "scrupulous",
                "negligent", "indolent", "complacent", "apathetic",
                "succinct", "concise", "laconic", "pithy",
                "tedious", "protracted", "interminable", "dilatory"],

    # curt: "abruptly or rudely short" -- synonyms: brusque, terse, laconic
    "curt": ["verbose", "garrulous", "loquacious", "effusive",
             "cordial", "gracious", "affable", "genial",
             "taciturn", "reticent", "stoic", "impassive",
             "peremptory", "imperious", "officious", "surly"],

    # daunting: "intimidating" -- synonyms: formidable, redoubtable, onerous
    "daunting": ["trivial", "facile", "pedestrian", "mundane",
                 "harrowing", "grievous", "dire", "perilous",
                 "strenuous", "arduous", "laborious", "rigorous",
                 "imposing", "colossal", "prodigious", "monumental"],

    # decorous: "socially proper"
    "decorous": ["boorish", "uncouth", "crass", "gauche",
                 "dignified", "punctilious", "fastidious", "scrupulous",
                 "ostentatious", "pretentious", "grandiose", "bombastic",
                 "demure", "deferential", "reserved", "genteel"],

    # defamatory: "harmful to reputation" -- synonyms: scurrilous, slanderous
    "defamatory": ["laudatory", "commendatory", "complimentary", "meritorious",
                   "pejorative", "derisive", "contemptuous", "vitriolic",
                   "fallacious", "spurious", "mendacious", "apocryphal",
                   "incendiary", "inflammatory", "provocative", "insidious"],

    # deferential: "showing respect for authority" -- synonyms: submissive, obsequious, compliant, servile
    "deferential": ["impertinent", "insolent", "impudent", "presumptuous",
                    "solicitous", "gracious", "punctilious", "fastidious",
                    "docile", "tractable", "amenable", "malleable",
                    "stoic", "impassive", "nonchalant", "phlegmatic"],

    # deft: "skillful, capable" -- synonyms: adept, adroit, agile, nimble
    "deft": ["inept", "clumsy", "maladroit", "awkward",
             "ingenious", "resourceful", "versatile", "proficient",
             "meticulous", "fastidious", "scrupulous", "punctilious",
             "pragmatic", "empirical", "judicious", "prudent"],

    # defunct: "no longer used or existing" -- synonyms: obsolete, antiquated, archaic
    "defunct": ["extant", "nascent", "vibrant", "dynamic",
                "dormant", "latent", "vestigial", "residual",
                "anachronistic", "antediluvian", "primeval", "decrepit",
                "ephemeral", "transient", "evanescent", "fleeting"],

    # deleterious: "harmful" -- synonyms: noxious, pernicious, adverse, detrimental
    "deleterious": ["salubrious", "benign", "innocuous", "beneficial",
                    "insidious", "corrosive", "incendiary", "virulent",
                    "onerous", "grievous", "punitive", "draconian",
                    "gratuitous", "superfluous", "extraneous", "nominal"],

    # deliberate: "intentional, careful" -- synonyms: methodical, meticulous, calculated, assiduous
    "deliberate": ["impetuous", "rash", "haphazard", "arbitrary",
                   "circumspect", "prudent", "judicious", "scrupulous",
                   "perfunctory", "cursory", "negligent", "indolent",
                   "fastidious", "punctilious", "systematic", "empirical"],

    # demure: "quiet, modest, reserved" -- synonyms: bashful, diffident, reticent, timorous
    "demure": ["brazen", "audacious", "impudent", "gregarious",
               "aloof", "stoic", "phlegmatic", "impassive",
               "taciturn", "laconic", "nonchalant", "indifferent",
               "effervescent", "vivacious", "ebullient", "winsome"],

    # derelict: "abandoned, run-down"
    "derelict": ["pristine", "resplendent", "immaculate", "opulent",
                 "dilapidated", "decrepit", "squalid", "ramshackle",
                 "dormant", "defunct", "obsolete", "antiquated",
                 "austere", "spartan", "barren", "bleak"],

    # derivative: "taken from a source, unoriginal" -- synonyms: hackneyed, trite, banal
    "derivative": ["innovative", "seminal", "novel", "original",
                   "prosaic", "mundane", "pedestrian", "quotidian",
                   "eclectic", "heterogeneous", "multifarious", "myriad",
                   "conventional", "orthodox", "archetypal", "paradigmatic"],

    # desiccated: "dried up, dehydrated" -- synonyms: arid, parched
    "desiccated": ["verdant", "lush", "fecund", "fertile",
                   "emaciated", "pallid", "wizened", "gaunt",
                   "barren", "desolate", "austere", "spartan",
                   "putrid", "rancid", "fetid", "noisome"],

    # desolate: "deserted, dreary" -- synonyms: bleak, barren, forlorn, austere, bereft
    "desolate": ["verdant", "lush", "opulent", "resplendent",
                 "stark", "spartan", "arid", "desiccated",
                 "morose", "somber", "lugubrious", "melancholy",
                 "tranquil", "serene", "placid", "pastoral"],

    # despondent: "depressed, hopeless" -- synonyms: disheartened, morose, forlorn, dejected
    "despondent": ["jubilant", "elated", "euphoric", "ecstatic",
                   "melancholy", "wistful", "lugubrious", "maudlin",
                   "stoic", "impassive", "phlegmatic", "nonchalant",
                   "resilient", "indomitable", "resolute", "sanguine"],

    # destitute: "impoverished" -- synonyms: indigent, penurious, bereft, impecunious
    "destitute": ["affluent", "opulent", "lavish", "prosperous",
                  "hapless", "forlorn", "wretched", "abject",
                  "frugal", "austere", "spartan", "ascetic",
                  "meager", "paltry", "nominal", "paucity"],

    # devious: "not straightforward, deceitful" -- synonyms: cunning, sly, wily, crafty, furtive, surreptitious, covert
    "devious": ["forthright", "candid", "transparent", "ingenuous",
                "insidious", "perfidious", "mendacious", "duplicitous",
                "oblique", "circuitous", "tortuous", "convoluted",
                "nefarious", "illicit", "reprehensible", "heinous"],

    # diaphanous: "light, airy, transparent" -- synonyms: ethereal, transparent
    "diaphanous": ["opaque", "dense", "impervious", "viscous",
                   "gossamer", "delicate", "flimsy", "fragile",
                   "luminous", "iridescent", "effulgent", "resplendent",
                   "ephemeral", "evanescent", "fleeting", "transient"],

    # didactic: "intended to instruct; overly moralistic" -- synonyms: cerebral
    "didactic": ["entertaining", "frivolous", "whimsical", "facile",
                 "erudite", "pedantic", "scholarly", "abstruse",
                 "sanctimonious", "dogmatic", "doctrinaire", "authoritarian",
                 "pragmatic", "empirical", "utilitarian", "esoteric"],

    # diffident: "shy, quiet, modest" -- synonyms: bashful, demure, reticent, timorous
    "diffident": ["brazen", "audacious", "gregarious", "vociferous",
                  "taciturn", "stoic", "aloof", "phlegmatic",
                  "nonchalant", "impassive", "apathetic", "indifferent",
                  "winsome", "vivacious", "effervescent", "ebullient"],

    # dilatory: "tending to delay" -- synonyms: sluggish, languid, lethargic, indolent
    "dilatory": ["expedient", "prompt", "diligent", "assiduous",
                 "perfunctory", "cursory", "negligent", "remiss",
                 "interminable", "protracted", "tedious", "plodding",
                 "complacent", "apathetic", "phlegmatic", "torpid"],

    # diligent: "showing care in work" -- synonyms: assiduous, meticulous, scrupulous, painstaking, sedulous
    "diligent": ["negligent", "indolent", "remiss", "lackadaisical",
                 "fastidious", "punctilious", "conscientious", "zealous",
                 "tenacious", "indefatigable", "resolute", "pertinacious",
                 "perfunctory", "cursory", "complacent", "apathetic"],

    # diminutive: "small, miniature" -- synonyms: meager
    "diminutive": ["colossal", "prodigious", "grandiose", "monumental",
                   "nominal", "trivial", "paltry", "negligible",
                   "capacious", "commodious", "copious", "voluminous",
                   "quaint", "petite", "compact", "sparse"],

    # disaffected: "rebellious, resentful" -- synonyms: disgruntled, discontented
    "disaffected": ["loyal", "compliant", "deferential", "docile",
                    "restive", "fractious", "recalcitrant", "defiant",
                    "indifferent", "apathetic", "nonchalant", "complacent",
                    "petulant", "querulous", "irascible", "contentious"],

    # discordant: "not in harmony" -- synonyms: cacophonous, strident, raucous, dissonant
    "discordant": ["harmonious", "melodious", "mellifluous", "consonant",
                   "contentious", "fractious", "acrimonious", "pugnacious",
                   "incongruous", "disparate", "anomalous", "aberrant",
                   "obstreperous", "vociferous", "boisterous", "shrill"],

    # discursive: "rambling, lacking order" -- synonyms: circuitous, verbose, prolix, convoluted, digressive
    "discursive": ["concise", "succinct", "pithy", "laconic",
                   "tedious", "protracted", "interminable", "pedantic",
                   "tangential", "extraneous", "superfluous", "gratuitous",
                   "elaborate", "ornate", "florid", "bombastic"],

    # disgruntled: "upset, not content" -- synonyms: disaffected, aggrieved
    "disgruntled": ["content", "gratified", "jubilant", "complacent",
                    "petulant", "querulous", "irascible", "fractious",
                    "despondent", "morose", "melancholy", "sullen",
                    "restive", "indignant", "resentful", "embittered"],

    # disheartened: "loss of spirit or morale" -- synonyms: despondent, dispirited, dejected
    "disheartened": ["elated", "jubilant", "euphoric", "sanguine",
                     "resilient", "resolute", "indomitable", "steadfast",
                     "complacent", "indifferent", "apathetic", "nonchalant",
                     "morose", "wistful", "melancholy", "forlorn"],

    # disparate: "sharply differing" -- synonyms: diverse, heterogeneous, incongruous
    "disparate": ["analogous", "homogeneous", "tantamount", "commensurate",
                  "eclectic", "multifarious", "variegated", "manifold",
                  "anomalous", "aberrant", "idiosyncratic", "atypical",
                  "tangential", "extraneous", "peripheral", "collateral"],
}

# Generate output
output = {}

for word in chunk2_words:
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

# Check pool quality
print("\n=== Pool Quality Check (first 10) ===")
for word in chunk2_words[:10]:
    if word in curated:
        pool = build_pool(word, curated[word])
        curated_count = len([c for c in curated[word] if c in set(all_words_by_pos[pos_map[word]]) and c != word and c not in get_synonyms(word)])
        print(f"  {word}: {curated_count} curated survived, pool size = {len(pool)}")
    else:
        syns = get_synonyms(word)
        pool_size = len([w for w in all_words_by_pos[pos_map[word]] if w != word and w not in syns])
        print(f"  {word}: NO CURATED, fallback pool size = {pool_size}")

# Write output
import os
os.makedirs('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp', exist_ok=True)
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_2_output.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nWritten to tmp/chunk_2_output.json")
fsize = os.path.getsize('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_2_output.json')
print(f"File size: {fsize} bytes ({fsize/1024:.1f} KB)")
