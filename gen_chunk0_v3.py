import re
import json
import random

random.seed(42)

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

chunk0_words = [w for w, p, d in words_data[:126]]

# Synonyms to exclude - words too close in meaning
synonym_sets = {
    "abase": {"debase", "demean", "degrade", "humiliate"},
    "abate": {"diminish", "lessen", "wane", "subside", "dwindle", "alleviate", "mitigate"},
    "abdicate": {"renounce", "relinquish", "resign"},
    "abduct": {"kidnap", "seize"},
    "abet": {"assist", "aid", "foment", "facilitate"},
    "abhor": {"detest", "loathe", "despise", "execrate"},
    "abide": {"endure", "tolerate", "withstand"},
    "abjure": {"renounce", "forswear", "recant", "repudiate"},
    "abort": {"abandon", "terminate", "cease"},
    "abridge": {"condense", "truncate", "curtail", "shorten"},
    "abrogate": {"annul", "revoke", "rescind", "repeal", "nullify"},
    "abscond": {"flee", "escape"},
    "abstain": {"refrain", "forgo", "eschew"},
    "accede": {"acquiesce", "assent", "concur", "consent", "agree"},
    "accentuate": {"emphasize", "highlight", "underscore", "stress"},
    "accost": {"confront"},
    "acquiesce": {"accede", "consent", "comply", "submit", "yield"},
    "adhere": {"cling", "stick"},
    "admonish": {"rebuke", "reprimand", "reproach", "chide", "scold"},
    "adorn": {"decorate", "embellish", "ornament", "beautify"},
    "adumbrate": {"foreshadow", "outline", "sketch"},
    "advocate": {"champion", "promote", "endorse", "support"},
    "aggrandize": {"magnify", "amplify", "inflate", "enlarge", "augment"},
    "allay": {"assuage", "alleviate", "soothe", "ease", "mitigate", "palliate"},
    "allege": {"claim", "assert", "contend"},
    "alleviate": {"assuage", "ease", "relieve", "mitigate", "palliate", "ameliorate"},
    "allocate": {"distribute", "apportion", "assign", "designate"},
    "amalgamate": {"merge", "combine", "unite", "fuse", "consolidate", "integrate"},
    "ameliorate": {"improve", "alleviate", "enhance", "better"},
    "annex": {"seize", "appropriate", "commandeer"},
    "annul": {"abrogate", "revoke", "rescind", "invalidate", "nullify", "void"},
    "appease": {"placate", "mollify", "pacify", "conciliate", "soothe", "allay", "assuage"},
    "appraise": {"assess", "evaluate", "gauge"},
    "apprehend": {"arrest", "seize", "capture", "detain", "grasp", "comprehend"},
    "appropriate": {"seize", "commandeer", "confiscate", "expropriate", "usurp"},
    "arrogate": {"usurp", "appropriate", "seize", "commandeer"},
    "ascertain": {"determine", "discover", "establish", "verify", "confirm"},
    "ascribe": {"attribute", "credit", "assign", "impute"},
    "aspire": {"yearn", "strive", "aim"},
    "assail": {"attack", "assault", "bombard"},
    "assess": {"evaluate", "appraise", "gauge", "judge"},
    # Nouns
    "aberration": {"anomaly", "deviation", "irregularity"},
    "abnegation": {"self-denial", "abstinence", "renunciation"},
    "absolution": {"forgiveness", "pardon", "exoneration", "amnesty", "clemency"},
    "acclaim": {"praise", "accolade", "commendation", "approbation", "adulation", "kudos"},
    "accolade": {"acclaim", "praise", "commendation", "approbation", "tribute", "honor"},
    "accord": {"agreement", "pact", "treaty", "consensus"},
    "accretion": {"accumulation", "buildup", "growth"},
    "acrimony": {"bitterness", "rancor", "animosity", "hostility", "enmity", "antagonism", "antipathy"},
    "acumen": {"insight", "sagacity", "discernment", "shrewdness", "astuteness"},
    "adulation": {"acclaim", "praise", "flattery", "veneration", "worship"},
    "affinity": {"kinship", "rapport", "closeness", "bond"},
    "affront": {"insult", "slight", "indignity", "offense"},
    "aggregate": {"total", "sum", "whole", "composite"},
    "alacrity": {"eagerness", "enthusiasm", "zeal", "fervor", "ardor"},
    "alias": {"pseudonym"},
    "altercation": {"quarrel", "dispute", "confrontation", "clash", "skirmish"},
    "amenity": {"comfort", "convenience", "luxury"},
    "analgesic": {"painkiller"},
    "anarchist": {"rebel", "insurgent", "revolutionary"},
    "anathema": {"bane", "curse"},
    "anecdote": {"story", "tale", "account", "narrative"},
    "anesthesia": {"numbness", "sedation"},
    "anguish": {"agony", "torment", "suffering", "distress", "grief"},
    "anomaly": {"aberration", "irregularity", "deviation"},
    "antagonism": {"hostility", "enmity", "antipathy", "animosity", "acrimony"},
    "antecedent": {"precursor", "predecessor", "forerunner"},
    "anthology": {"collection", "compilation", "compendium"},
    "antipathy": {"aversion", "hostility", "antagonism", "animosity", "enmity", "repugnance"},
    "antithesis": {"opposite", "contrary", "inverse"},
    "anxiety": {"worry", "unease", "apprehension", "trepidation", "dread"},
    "approbation": {"acclaim", "approval", "praise", "commendation", "endorsement"},
    "arbiter": {"mediator", "judge", "adjudicator", "arbitrator"},
    "arbitration": {"mediation", "negotiation", "settlement"},
    "ardor": {"passion", "fervor", "zeal", "enthusiasm", "intensity", "alacrity"},
    "artifact": {"relic", "remnant", "vestige"},
    "artisan": {"craftsman", "craftsperson"},
    "aspersion": {"slander", "defamation", "slur", "calumny"},
    # Adjectives
    "abject": {"wretched", "miserable", "pitiful", "deplorable"},
    "abstruse": {"esoteric", "arcane", "recondite", "obscure", "cryptic"},
    "accessible": {"available", "reachable", "obtainable"},
    "accommodating": {"obliging", "helpful", "compliant"},
    "acerbic": {"caustic", "mordant", "sardonic", "biting", "acrimonious", "trenchant"},
    "acute": {"sharp", "keen", "incisive", "piercing", "astute", "shrewd", "perceptive"},
    "adamant": {"unyielding", "resolute", "steadfast", "inflexible", "intransigent", "obstinate", "immovable"},
    "adept": {"skilled", "proficient", "dexterous", "masterful", "accomplished", "adroit"},
    "adroit": {"skilled", "deft", "nimble", "dexterous", "proficient", "adept"},
    "adverse": {"unfavorable", "detrimental", "hostile", "harmful"},
    "aerial": {"airborne"},
    "aesthetic": {"artistic", "beautiful"},
    "affable": {"friendly", "amiable", "genial", "cordial", "amicable", "sociable"},
    "affluent": {"wealthy", "rich", "prosperous", "opulent"},
    "aggrieved": {"wronged", "distressed", "hurt"},
    "agile": {"nimble", "quick", "lithe", "spry", "adroit"},
    "agnostic": {"skeptical"},
    "aloof": {"distant", "detached", "remote", "standoffish", "reserved"},
    "altruistic": {"selfless", "charitable", "philanthropic", "magnanimous", "benevolent"},
    "ambiguous": {"vague", "unclear", "equivocal", "nebulous"},
    "ambivalent": {"conflicted", "undecided", "torn"},
    "amenable": {"willing", "compliant", "cooperative", "receptive", "agreeable", "acquiescent", "accommodating"},
    "amiable": {"friendly", "affable", "genial", "cordial", "amicable", "likable"},
    "amicable": {"friendly", "cordial", "harmonious", "affable", "amiable"},
    "amorous": {"romantic", "passionate", "loving"},
    "amorphous": {"shapeless", "formless", "nebulous"},
    "anachronistic": {"outdated", "outmoded", "antiquated", "archaic", "antediluvian"},
    "analogous": {"similar", "comparable", "akin", "parallel", "corresponding"},
    "animated": {"lively", "spirited", "vivacious", "vibrant", "exuberant", "energetic", "boisterous"},
    "anonymous": {"unnamed", "unknown", "unidentified"},
    "antediluvian": {"ancient", "archaic", "antiquated", "prehistoric", "primordial", "anachronistic"},
    "antiquated": {"outdated", "archaic", "obsolete", "old-fashioned", "antediluvian", "anachronistic"},
    "antiseptic": {"sterile", "clean", "sanitary"},
    "apathetic": {"indifferent", "unconcerned", "unmoved", "dispassionate", "impassive", "aloof"},
    "apocryphal": {"fictitious", "false", "fabricated", "spurious", "dubious", "unsubstantiated"},
    "appalling": {"horrifying", "shocking", "dreadful", "atrocious", "ghastly", "deplorable", "abject"},
    "aquatic": {"marine", "maritime", "nautical"},
    "arable": {"fertile", "cultivable"},
    "arbitrary": {"random", "capricious", "whimsical", "haphazard"},
    "arboreal": {"sylvan"},
    "arcane": {"esoteric", "obscure", "cryptic", "mysterious", "abstruse", "recondite"},
    "archaic": {"ancient", "antiquated", "obsolete", "antediluvian", "anachronistic"},
    "archetypal": {"quintessential", "prototypical", "exemplary", "definitive"},
    "arid": {"dry", "parched", "barren"},
    "ascetic": {"austere", "spartan", "abstemious", "frugal"},
    "assiduous": {"diligent", "industrious", "tireless", "meticulous", "conscientious", "sedulous", "painstaking"},
}

def get_synonyms(word):
    syns = set()
    if word in synonym_sets:
        syns.update(synonym_sets[word])
    # Bidirectional check
    for k, v in synonym_sets.items():
        if word in v:
            syns.add(k)
            syns.update(v)
    syns.discard(word)
    return syns

# Curated distractor pools - 12+ per word, all must be in the master word list
# These are words that fit grammatically but mean something DIFFERENT
# I'll verify each one against the word list

# First, let's see what words are actually available
available_v = set(all_words_by_pos["v"])
available_n = set(all_words_by_pos["n"])
available_adj = set(all_words_by_pos["adj"])

print(f"Available verbs: {len(available_v)}")
print(f"Available nouns: {len(available_n)}")
print(f"Available adjectives: {len(available_adj)}")

# For each chunk0 word, build a curated pool of 12+ valid distractors
# The pool is: words same POS, in the master list, not synonyms, plausible in similar contexts

def build_pool(word, curated_candidates):
    """Build pool from curated list, filtering to only valid words"""
    pos = pos_map[word]
    syns = get_synonyms(word)
    available = set(all_words_by_pos[pos])
    
    pool = []
    for c in curated_candidates:
        if c in available and c != word and c not in syns:
            pool.append(c)
    
    # If pool is too small, supplement with random same-POS words
    if len(pool) < 12:
        extras = [w for w in all_words_by_pos[pos] 
                  if w != word and w not in syns and w not in pool]
        random.shuffle(extras)
        pool.extend(extras[:20 - len(pool)])
    
    return pool

# Define curated candidates for every chunk0 word
# Format: word -> list of candidate distractors (will be filtered against master list)
curated = {
    # === VERBS ===
    "abase": ["accost", "appease", "chastise", "subjugate", "berate", "admonish", "censure", "exalt", "venerate", "commend", "laud", "reprimand", "reproach", "rebuke"],
    "abate": ["augment", "curtail", "abrogate", "accentuate", "aggrandize", "fluctuate", "proliferate", "intensify", "persist", "abscond", "accumulate", "oscillate", "stagnate", "compound"],
    "abdicate": ["appropriate", "arrogate", "capitulate", "accede", "abstain", "attain", "advocate", "delegate", "usurp", "inaugurate", "aspire", "preside", "annex", "inherit"],
    "abduct": ["accost", "apprehend", "assail", "escort", "dispatch", "intercept", "liberate", "harbor", "detain", "arraign", "sequester", "imprison", "acquit", "extradite"],
    "abet": ["impede", "thwart", "deter", "obstruct", "incite", "conspire", "advocate", "compel", "condemn", "admonish", "sanction", "instigate", "provoke", "inhibit"],
    "abhor": ["cherish", "revere", "esteem", "relish", "endure", "covet", "spurn", "adore", "savor", "deplore", "lament", "rue", "resent", "venerate"],
    "abide": ["abstain", "acquiesce", "protest", "defy", "capitulate", "persist", "resist", "linger", "comply", "vacillate", "waver", "relent", "concede", "dissent"],
    "abjure": ["espouse", "uphold", "advocate", "abdicate", "abstain", "rescind", "repeal", "endorse", "profess", "affirm", "proclaim", "retract", "invoke", "revoke"],
    "abort": ["commence", "initiate", "consummate", "expedite", "resume", "sustain", "undertake", "defer", "postpone", "curtail", "launch", "catalyze", "implement", "improvise"],
    "abridge": ["augment", "elaborate", "amplify", "annotate", "supplement", "distill", "redact", "extend", "embellish", "compile", "consolidate", "catalog", "expound", "append"],
    "abrogate": ["enact", "ratify", "enforce", "uphold", "sanction", "amend", "decree", "invoke", "implement", "rescind", "repeal", "impose", "mandate", "promulgate"],
    "abscond": ["loiter", "linger", "congregate", "emerge", "infiltrate", "trespass", "roam", "retreat", "migrate", "traverse", "wander", "prowl", "encroach", "converge"],
    "abstain": ["indulge", "partake", "carouse", "revel", "succumb", "persevere", "gorge", "consume", "savor", "relish", "imbibe", "wallow", "splurge", "capitulate"],
    "accede": ["dissent", "protest", "resist", "abstain", "capitulate", "concede", "dispute", "contend", "comply", "defer", "rebuff", "relent", "balk", "demur"],
    "accentuate": ["obscure", "diminish", "undermine", "embellish", "distort", "amplify", "exaggerate", "qualify", "supplement", "bolster", "magnify", "inflate", "adorn", "burnish"],
    "accost": ["evade", "shun", "beckon", "summon", "hail", "implore", "beseech", "interrogate", "rebuff", "confront", "berate", "entreat", "importune", "harangue"],
    "acquiesce": ["protest", "dissent", "resist", "defy", "relent", "capitulate", "concede", "contend", "dispute", "comply", "balk", "demur", "object", "abstain"],
    "adhere": ["deviate", "digress", "stray", "waver", "conform", "defer", "abstain", "persist", "aspire", "vacillate", "diverge", "comply", "oscillate", "abide"],
    "admonish": ["commend", "extol", "laud", "exalt", "berate", "censure", "exonerate", "console", "appease", "rebuke", "reprimand", "castigate", "reproach", "chastise"],
    "adorn": ["burnish", "garnish", "furnish", "mar", "illuminate", "enhance", "cultivate", "deface", "tarnish", "lacquer", "polish", "augment", "accentuate", "embellish"],
    "adumbrate": ["elaborate", "elucidate", "expound", "articulate", "delineate", "intimate", "insinuate", "allude", "portend", "imply", "stipulate", "conjecture", "surmise", "postulate"],
    "advocate": ["denounce", "oppose", "condemn", "disparage", "champion", "endorse", "censure", "critique", "refute", "propose", "promote", "sanction", "decree", "mandate"],
    "aggrandize": ["diminish", "undermine", "curtail", "bolster", "fortify", "embellish", "cultivate", "abate", "depreciate", "erode", "enhance", "buttress", "inflate", "consolidate"],
    "allay": ["exacerbate", "aggravate", "provoke", "incite", "inflame", "compound", "amplify", "kindle", "escalate", "stoke", "intensify", "instigate", "foment", "agitate"],
    "allege": ["verify", "substantiate", "corroborate", "attest", "contend", "surmise", "postulate", "speculate", "insinuate", "refute", "proclaim", "stipulate", "decree", "affirm"],
    "alleviate": ["exacerbate", "aggravate", "intensify", "compound", "amplify", "curtail", "prolong", "bolster", "rectify", "restore", "sustain", "perpetuate", "augment", "escalate"],
    "allocate": ["confiscate", "appropriate", "hoard", "squander", "deplete", "consolidate", "disperse", "withhold", "amass", "disburse", "ration", "accumulate", "stockpile", "requisition"],
    "amalgamate": ["segregate", "fracture", "fragment", "dissolve", "partition", "converge", "disperse", "diverge", "splinter", "differentiate", "aggregate", "assimilate", "compile", "dissipate"],
    "ameliorate": ["exacerbate", "aggravate", "compound", "impair", "undermine", "sustain", "bolster", "rectify", "restore", "revitalize", "intensify", "perpetuate", "fortify", "augment"],
    "annex": ["relinquish", "cede", "confiscate", "commandeer", "liberate", "occupy", "allocate", "reclaim", "vacate", "abdicate", "procure", "requisition", "appropriate", "bequeath"],
    "annul": ["ratify", "enact", "enforce", "validate", "sanction", "decree", "affirm", "uphold", "institute", "authorize", "amend", "implement", "promulgate", "mandate"],
    "appease": ["provoke", "antagonize", "incite", "inflame", "aggravate", "exacerbate", "console", "rebuke", "admonish", "cajole", "agitate", "berate", "censure", "chastise"],
    "appraise": ["disregard", "overlook", "neglect", "scrutinize", "discern", "calibrate", "survey", "quantify", "audit", "inventory", "tabulate", "conjecture", "surmise", "catalog"],
    "apprehend": ["liberate", "release", "exonerate", "detain", "evade", "elude", "ascertain", "discern", "overlook", "disregard", "surmise", "arraign", "indict", "acquit"],
    "appropriate": ["relinquish", "forfeit", "bequeath", "bestow", "allocate", "dispense", "requisition", "donate", "distribute", "confiscate", "commandeer", "procure", "arrogate", "amass"],
    "arrogate": ["relinquish", "abdicate", "bestow", "delegate", "appropriate", "commandeer", "forfeit", "cede", "allocate", "confer", "bequeath", "procure", "requisition", "usurp"],
    "ascertain": ["surmise", "speculate", "conjecture", "presume", "postulate", "corroborate", "scrutinize", "discern", "deduce", "hypothesize", "appraise", "calibrate", "extrapolate", "fathom"],
    "ascribe": ["disclaim", "disavow", "allege", "infer", "deduce", "designate", "stipulate", "contend", "presume", "postulate", "proclaim", "surmise", "impute", "mandate"],
    "aspire": ["resign", "succumb", "abstain", "languish", "stagnate", "covet", "endeavor", "crave", "pursue", "persist", "contend", "toil", "persevere", "wallow"],
    "assail": ["defend", "accost", "berate", "confront", "rebuke", "chastise", "denounce", "censure", "impugn", "bombard", "admonish", "harangue", "disparage", "reproach"],
    "assess": ["disregard", "overlook", "neglect", "conjecture", "surmise", "calibrate", "scrutinize", "audit", "quantify", "tabulate", "survey", "catalog", "appraise", "discern"],

    # === NOUNS ===
    "aberration": ["precedent", "paradigm", "phenomenon", "archetype", "antithesis", "anecdote", "artifact", "epitome", "manifestation", "discrepancy", "paradox", "relic", "harbinger"],
    "abnegation": ["avarice", "opulence", "fortitude", "temperance", "decadence", "austerity", "extravagance", "indulgence", "moderation", "frugality", "prudence", "tenacity", "candor"],
    "absolution": ["condemnation", "censure", "indictment", "retribution", "penance", "reprieve", "verdict", "clemency", "sanction", "acquittal", "atonement", "recourse", "redress"],
    "acclaim": ["censure", "ridicule", "contempt", "derision", "scorn", "notoriety", "indifference", "scrutiny", "rebuke", "infamy", "disdain", "enmity", "animosity", "antipathy"],
    "accolade": ["censure", "rebuke", "reprimand", "stigma", "criticism", "commendation", "tribute", "indictment", "sanction", "citation", "distinction", "blemish", "aspersion"],
    "accord": ["discord", "impasse", "schism", "rift", "consensus", "compromise", "concession", "mandate", "decree", "covenant", "edict", "grievance", "stalemate", "deadlock"],
    "accretion": ["erosion", "depletion", "attrition", "diminution", "expansion", "aggregation", "surplus", "deficit", "increment", "remnant", "abundance", "scarcity", "residue"],
    "acrimony": ["camaraderie", "cordiality", "rapport", "civility", "discord", "rancor", "friction", "animosity", "malice", "resentment", "contention", "tension", "strife"],
    "acumen": ["naivete", "ignorance", "incompetence", "aptitude", "finesse", "prudence", "foresight", "instinct", "prowess", "sagacity", "cunning", "tenacity", "intuition"],
    "adulation": ["censure", "contempt", "derision", "scorn", "ridicule", "reverence", "admiration", "criticism", "indifference", "rebuke", "disdain", "enmity", "antipathy"],
    "affinity": ["aversion", "antipathy", "discord", "apathy", "rapport", "kinship", "inclination", "bias", "predilection", "proclivity", "enmity", "ambivalence", "repulsion"],
    "affront": ["compliment", "accolade", "tribute", "slight", "indignity", "transgression", "provocation", "grievance", "courtesy", "commendation", "aspersion", "rebuke", "epithet"],
    "aggregate": ["fragment", "fraction", "remnant", "component", "surplus", "deficit", "composite", "inventory", "assortment", "quota", "bounty", "compilation", "cache", "arsenal"],
    "agriculture": ["commerce", "industry", "infrastructure", "horticulture", "forestry", "enterprise", "manufacture", "conservation", "cultivation", "husbandry", "irrigation", "tariff"],
    "aisle": ["corridor", "vestibule", "alcove", "terrace", "facade", "partition", "promenade", "threshold", "foyer", "balcony", "arcade", "rampart", "parapet", "turret"],
    "alacrity": ["reluctance", "lethargy", "indifference", "apathy", "hesitation", "trepidation", "diligence", "haste", "vigor", "tenacity", "resolve", "inertia", "complacency"],
    "alias": ["moniker", "epithet", "title", "designation", "surname", "emblem", "insignia", "trademark", "namesake", "acronym", "credential", "memoir", "pedigree", "lineage"],
    "altercation": ["consensus", "accord", "reconciliation", "discourse", "debacle", "confrontation", "feud", "quarrel", "commotion", "standoff", "impasse", "skirmish", "fracas"],
    "amenity": ["liability", "burden", "nuisance", "hindrance", "deficiency", "commodity", "provision", "fixture", "supplement", "apparatus", "accessory", "bounty", "windfall"],
    "analgesic": ["stimulant", "antidote", "toxin", "remedy", "tonic", "elixir", "compound", "supplement", "placebo", "palliative", "serum", "vaccine", "sedative", "salve"],
    "anarchist": ["autocrat", "tyrant", "despot", "monarch", "patriarch", "partisan", "zealot", "dissident", "idealist", "agitator", "insurgent", "demagogue", "aristocrat"],
    "anathema": ["blessing", "boon", "privilege", "pariah", "scourge", "nemesis", "taboo", "stigma", "nuisance", "menace", "windfall", "heresy", "blight", "bane"],
    "anecdote": ["treatise", "manifesto", "chronicle", "testimony", "allegory", "parable", "proverb", "memoir", "excerpt", "vignette", "fable", "diatribe", "monologue", "tirade"],
    "anesthesia": ["stimulus", "lethargy", "stupor", "torpor", "delirium", "vertigo", "malaise", "fatigue", "consciousness", "paralysis", "coma", "euphoria", "trauma", "atrophy"],
    "anguish": ["bliss", "euphoria", "serenity", "composure", "melancholy", "resentment", "dismay", "indignation", "despair", "remorse", "adversity", "tribulation", "consternation"],
    "anomaly": ["norm", "standard", "precedent", "paradigm", "archetype", "discrepancy", "phenomenon", "rarity", "paradox", "inconsistency", "irregularity", "curiosity", "outlier"],
    "antagonism": ["camaraderie", "rapport", "solidarity", "affinity", "acrimony", "friction", "animosity", "resentment", "contempt", "malice", "discord", "tension", "strife"],
    "antecedent": ["consequence", "aftermath", "culmination", "outcome", "catalyst", "harbinger", "origin", "genesis", "impetus", "prologue", "stimulus", "foundation", "inception"],
    "anthology": ["manuscript", "chronicle", "treatise", "compendium", "archive", "memoir", "journal", "gazette", "almanac", "digest", "volume", "tome", "encyclopedia", "lexicon"],
    "antipathy": ["affinity", "rapport", "solidarity", "empathy", "acrimony", "friction", "contempt", "malice", "discord", "disdain", "scorn", "resentment", "indifference"],
    "antithesis": ["complement", "corollary", "parallel", "counterpart", "analogy", "paradox", "contradiction", "deviation", "juxtaposition", "dichotomy", "anomaly", "inverse"],
    "anxiety": ["serenity", "composure", "confidence", "indifference", "trepidation", "melancholy", "apprehension", "foreboding", "dread", "paranoia", "consternation", "unease"],
    "approbation": ["censure", "condemnation", "reproach", "rebuke", "contempt", "derision", "scorn", "ridicule", "commendation", "endorsement", "sanction", "aspersion", "calumny"],
    "arbiter": ["partisan", "advocate", "litigant", "adversary", "delegate", "envoy", "proxy", "intermediary", "magistrate", "counselor", "diplomat", "steward", "custodian"],
    "arbitration": ["litigation", "confrontation", "impasse", "deliberation", "tribunal", "proceeding", "verdict", "reconciliation", "adjudication", "stalemate", "deadlock", "truce"],
    "ardor": ["apathy", "indifference", "lethargy", "complacency", "fervor", "tenacity", "devotion", "conviction", "intensity", "vigor", "resolve", "inertia", "fortitude"],
    "artifact": ["replica", "counterfeit", "facsimile", "specimen", "heirloom", "antiquity", "fossil", "monument", "memento", "souvenir", "trophy", "curio", "keepsake"],
    "artisan": ["novice", "amateur", "entrepreneur", "connoisseur", "virtuoso", "laborer", "merchant", "vendor", "curator", "patron", "maestro", "apprentice", "prodigy"],
    "aspersion": ["accolade", "commendation", "tribute", "compliment", "endorsement", "allegation", "innuendo", "insinuation", "reproach", "rebuke", "diatribe", "tirade", "calumny"],
    "agriculture": ["commerce", "industry", "infrastructure", "forestry", "enterprise", "manufacture", "conservation", "husbandry", "irrigation", "tariff", "commodity", "bounty"],

    # === ADJECTIVES ===
    "abject": ["exalted", "dignified", "resilient", "stoic", "destitute", "forlorn", "squalid", "austere", "harrowing", "grievous", "dismal", "bleak", "desolate", "somber"],
    "abstruse": ["lucid", "rudimentary", "convoluted", "ambiguous", "enigmatic", "inscrutable", "perplexing", "pedantic", "cerebral", "erudite", "verbose", "opaque", "banal", "trite"],
    "accessible": ["prohibitive", "elusive", "exclusive", "obscure", "remote", "ubiquitous", "conspicuous", "prevalent", "abundant", "sparse", "scarce", "viable", "feasible", "tangible"],
    "accommodating": ["obstinate", "inflexible", "intransigent", "petulant", "cantankerous", "amenable", "gracious", "congenial", "indulgent", "perfunctory", "officious", "deferential"],
    "acerbic": ["affable", "genial", "cordial", "amiable", "sardonic", "scathing", "venomous", "incisive", "wry", "pungent", "vitriolic", "derisive", "contemptuous", "flippant"],
    "acute": ["obtuse", "superficial", "negligible", "chronic", "profound", "discerning", "perceptive", "shrewd", "incisive", "piercing", "severe", "critical", "salient", "poignant"],
    "adamant": ["amenable", "pliant", "acquiescent", "malleable", "obstinate", "tenacious", "unwavering", "intransigent", "staunch", "defiant", "dogmatic", "imperious", "belligerent"],
    "adept": ["inept", "clumsy", "incompetent", "mediocre", "versatile", "resourceful", "astute", "ingenious", "masterful", "accomplished", "proficient", "prolific", "pragmatic"],
    "adroit": ["inept", "clumsy", "awkward", "maladroit", "versatile", "astute", "resourceful", "shrewd", "ingenious", "deft", "agile", "pragmatic", "prudent", "savvy"],
    "adverse": ["favorable", "beneficial", "auspicious", "propitious", "detrimental", "precarious", "perilous", "ominous", "formidable", "dire", "onerous", "catastrophic", "chronic"],
    "aerial": ["terrestrial", "subterranean", "aquatic", "nautical", "celestial", "elevated", "lofty", "ethereal", "atmospheric", "vertical", "lateral", "peripheral", "tangential"],
    "aesthetic": ["utilitarian", "functional", "pragmatic", "mundane", "ornamental", "exquisite", "picturesque", "opulent", "lavish", "gaudy", "ostentatious", "grandiose", "quaint"],
    "affable": ["aloof", "austere", "taciturn", "brusque", "curt", "genial", "cordial", "gregarious", "congenial", "jovial", "personable", "cantankerous", "surly", "petulant"],
    "affluent": ["destitute", "impoverished", "indigent", "austere", "frugal", "lavish", "extravagant", "ostentatious", "bourgeois", "privileged", "avaricious", "penurious", "parsimonious"],
    "aggrieved": ["complacent", "gratified", "indifferent", "resentful", "embittered", "disgruntled", "indignant", "vindictive", "despondent", "incensed", "irate", "morose", "petulant"],
    "agile": ["sluggish", "cumbersome", "lethargic", "unwieldy", "deft", "lithe", "supple", "versatile", "robust", "vigorous", "nimble", "limber", "spry", "fleet"],
    "agnostic": ["devout", "pious", "fervent", "dogmatic", "secular", "impartial", "ambivalent", "indifferent", "apathetic", "pragmatic", "empirical", "skeptical", "dubious"],
    "aloof": ["gregarious", "sociable", "affable", "genial", "cordial", "reticent", "taciturn", "stoic", "indifferent", "nonchalant", "apathetic", "detached", "dispassionate"],
    "altruistic": ["selfish", "avaricious", "mercenary", "magnanimous", "benevolent", "compassionate", "noble", "virtuous", "pious", "devout", "zealous", "ostentatious", "pretentious"],
    "ambiguous": ["explicit", "definitive", "unequivocal", "cryptic", "enigmatic", "convoluted", "elusive", "tentative", "paradoxical", "misleading", "speculative", "dubious", "opaque"],
    "ambivalent": ["resolute", "decisive", "adamant", "steadfast", "indecisive", "hesitant", "tentative", "apathetic", "indifferent", "vacillating", "uncertain", "complacent", "reticent"],
    "amenable": ["obstinate", "defiant", "intransigent", "recalcitrant", "docile", "malleable", "receptive", "tractable", "acquiescent", "reluctant", "averse", "petulant", "cantankerous"],
    "amiable": ["surly", "cantankerous", "brusque", "aloof", "cordial", "congenial", "gregarious", "jovial", "genial", "gracious", "sociable", "petulant", "morose", "taciturn"],
    "amicable": ["hostile", "contentious", "belligerent", "antagonistic", "cordial", "congenial", "harmonious", "diplomatic", "cooperative", "collegial", "civil", "equitable", "pragmatic"],
    "amorous": ["indifferent", "platonic", "aloof", "detached", "ardent", "fervent", "passionate", "sentimental", "wistful", "enamored", "flirtatious", "coquettish", "bashful"],
    "amorphous": ["rigid", "defined", "structured", "diffuse", "fluid", "malleable", "ephemeral", "transient", "elusive", "intangible", "volatile", "disparate", "erratic", "abstract"],
    "anachronistic": ["contemporary", "progressive", "antiquated", "archaic", "obsolete", "outmoded", "nostalgic", "conventional", "traditional", "retrogressive", "quaint", "vintage"],
    "analogous": ["disparate", "dissimilar", "incongruent", "commensurate", "corresponding", "congruent", "homogeneous", "tantamount", "redundant", "ancillary", "peripheral", "tangential"],
    "animated": ["listless", "lethargic", "somber", "subdued", "ebullient", "buoyant", "effervescent", "fervent", "exuberant", "vivacious", "zealous", "raucous", "boisterous", "jovial"],
    "anonymous": ["renowned", "illustrious", "prominent", "conspicuous", "obscure", "enigmatic", "elusive", "nondescript", "inconspicuous", "clandestine", "discreet", "covert", "surreptitious"],
    "antediluvian": ["contemporary", "innovative", "progressive", "antiquated", "archaic", "obsolete", "medieval", "primordial", "decrepit", "dilapidated", "rudimentary", "primitive"],
    "antiquated": ["contemporary", "innovative", "modern", "archaic", "obsolete", "dilapidated", "decrepit", "outmoded", "rudimentary", "primitive", "conventional", "quaint", "rustic"],
    "antiseptic": ["squalid", "fetid", "contaminated", "pristine", "immaculate", "austere", "clinical", "spartan", "barren", "sterile", "arid", "desolate", "stark", "bleak"],
    "apathetic": ["passionate", "zealous", "fervent", "ardent", "nonchalant", "complacent", "dispassionate", "detached", "stoic", "impassive", "listless", "lethargic", "resigned"],
    "apocryphal": ["authentic", "verified", "substantiated", "dubious", "speculative", "legendary", "mythical", "fictitious", "plausible", "credible", "empirical", "anecdotal", "conjectural"],
    "appalling": ["commendable", "admirable", "exemplary", "laudable", "deplorable", "egregious", "heinous", "reprehensible", "unconscionable", "atrocious", "flagrant", "abhorrent"],
    "aquatic": ["terrestrial", "arboreal", "aerial", "subterranean", "maritime", "coastal", "tropical", "arid", "temperate", "pastoral", "riparian", "amphibious", "barren"],
    "arable": ["barren", "desolate", "arid", "verdant", "lush", "cultivated", "temperate", "tropical", "pastoral", "fertile", "rustic", "agrarian", "bucolic", "fallow"],
    "arbitrary": ["systematic", "methodical", "deliberate", "calculated", "capricious", "erratic", "impulsive", "spontaneous", "indiscriminate", "haphazard", "whimsical", "mercurial"],
    "arboreal": ["aquatic", "terrestrial", "subterranean", "aerial", "tropical", "verdant", "pastoral", "rustic", "perennial", "botanical", "deciduous", "agrarian", "bucolic"],
    "arcane": ["commonplace", "transparent", "accessible", "rudimentary", "cryptic", "enigmatic", "occult", "mystical", "clandestine", "inscrutable", "cerebral", "pedantic", "erudite"],
    "archaic": ["contemporary", "innovative", "modern", "progressive", "antiquated", "obsolete", "medieval", "primitive", "outmoded", "decrepit", "rudimentary", "conventional", "rustic"],
    "archetypal": ["atypical", "anomalous", "aberrant", "unique", "canonical", "iconic", "seminal", "emblematic", "paradigmatic", "definitive", "normative", "preeminent", "consummate"],
    "arid": ["lush", "verdant", "fertile", "temperate", "barren", "desolate", "austere", "bleak", "stark", "inhospitable", "scorched", "parched", "sparse", "rugged"],
    "ascetic": ["indulgent", "hedonistic", "opulent", "lavish", "spartan", "stoic", "monastic", "devout", "pious", "rigorous", "austere", "frugal", "abstemious", "puritanical"],
    "assiduous": ["negligent", "indolent", "lackadaisical", "complacent", "fastidious", "scrupulous", "methodical", "relentless", "tenacious", "exacting", "punctilious", "pedantic"],
}

# Generate output
output = {}

for word in chunk0_words:
    pos = pos_map[word]
    definition = word_info[word]["d"]
    word_sentences = sentences.get(word, [])
    
    if word in curated:
        pool = build_pool(word, curated[word])
    else:
        # Fallback: random same-POS words
        syns = get_synonyms(word)
        pool = [w for w in all_words_by_pos[pos] if w != word and w not in syns]
        random.shuffle(pool)
        pool = pool[:20]
    
    used_distractor_sets = set()
    entries = []
    
    for i, sent in enumerate(word_sentences[:8]):
        # Pick 3 from pool, ensuring variety
        attempts = 0
        best = None
        while attempts < 200:
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
            if d not in pos_map:
                print(f"ERROR: {word}[{i}]: distractor '{d}' not in word list")
                errors += 1
            elif pos_map[d] != pos_map[word]:
                print(f"ERROR: {word}[{i}]: distractor '{d}' POS mismatch")
                errors += 1

# Check synonyms
syn_errors = 0
for word, entries in output.items():
    syns = get_synonyms(word)
    for i, entry in enumerate(entries):
        for d in entry[1:4]:
            if d in syns:
                print(f"SYNONYM ERROR: {word}[{i}]: '{d}'")
                syn_errors += 1

# Check variety
low_variety = 0
for word, entries in output.items():
    all_d = set()
    for entry in entries:
        for d in entry[1:4]:
            all_d.add(d)
    if len(all_d) < 5:
        print(f"LOW VARIETY: {word} uses only {len(all_d)} unique distractors")
        low_variety += 1

print(f"\nValidation errors: {errors}")
print(f"Synonym errors: {syn_errors}")
print(f"Low variety words: {low_variety}")

# Write output
import os
os.makedirs('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp', exist_ok=True)
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_0_output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nWritten to tmp/chunk_0_output.json")

# File size
fsize = os.path.getsize('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_0_output.json')
print(f"File size: {fsize} bytes ({fsize/1024:.1f} KB)")
