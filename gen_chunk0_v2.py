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

# ===== MANUALLY CURATED DISTRACTOR POOLS =====
# For each word, provide a pool of 8-15 plausible distractors (same POS, not synonyms,
# but thematically adjacent/plausible). The script will rotate through them.

distractor_pools = {
    # VERBS
    "abase": ["accost", "appease", "chastise", "subjugate", "berate", "admonish", "reprimand", "censure", "exalt", "venerate", "commend", "laud"],
    "abate": ["augment", "escalate", "intensify", "curtail", "abrogate", "accentuate", "aggrandize", "diminish", "fluctuate", "persist", "proliferate", "wane"],
    "abdicate": ["appropriate", "arrogate", "usurp", "capitulate", "accede", "abstain", "relinquish", "attain", "inaugurate", "advocate", "delegate", "assume"],
    "abduct": ["accost", "apprehend", "assail", "detain", "arraign", "escort", "dispatch", "intercept", "imprison", "liberate", "sequester", "harbor"],
    "abet": ["impede", "thwart", "dissuade", "deter", "obstruct", "incite", "conspire", "advocate", "compel", "condemn", "admonish", "sanction"],
    "abhor": ["cherish", "revere", "esteem", "deplore", "resent", "tolerate", "relish", "endure", "covet", "disdain", "spurn", "adore"],
    "abide": ["abstain", "acquiesce", "protest", "defy", "succumb", "evade", "capitulate", "persist", "flee", "resist", "comply", "linger"],
    "abjure": ["espouse", "embrace", "uphold", "advocate", "abdicate", "abstain", "rescind", "repeal", "endorse", "pledge", "profess", "affirm"],
    "abort": ["commence", "initiate", "consummate", "expedite", "resume", "sustain", "undertake", "abandon", "defer", "postpone", "curtail", "launch"],
    "abridge": ["augment", "elaborate", "amplify", "annotate", "condense", "truncate", "append", "supplement", "consolidate", "distill", "redact", "extend"],
    "abrogate": ["enact", "ratify", "enforce", "uphold", "sanction", "institue", "amend", "decree", "invoke", "implement", "rescind", "repeal"],
    "abscond": ["loiter", "linger", "congregate", "emerge", "surface", "infiltrate", "trespass", "roam", "retreat", "migrate", "traverse", "wander"],
    "abstain": ["indulge", "partake", "imbibe", "gorge", "relish", "consume", "savor", "carouse", "revel", "yield", "succumb", "persevere"],
    "accede": ["dissent", "protest", "object", "resist", "abstain", "concede", "capitulate", "dispute", "contend", "comply", "defer", "rebuff"],
    "accentuate": ["obscure", "diminish", "undermine", "mitigate", "downplay", "embellish", "distort", "amplify", "exaggerate", "qualify", "supplement", "magnify"],
    "accost": ["evade", "shun", "beckon", "summon", "hail", "petition", "implore", "confront", "beseech", "interrogate", "acknowledge", "rebuff"],
    "acquiesce": ["protest", "dissent", "object", "resist", "defy", "relent", "capitulate", "concede", "contend", "dispute", "comply", "waiver"],
    "adhere": ["deviate", "diverge", "digress", "stray", "waver", "conform", "defer", "abstain", "persist", "aspire", "vacillate", "cling"],
    "admonish": ["commend", "extol", "laud", "acclaim", "applaud", "exalt", "berate", "censure", "exonerate", "console", "appease", "rebuke"],
    "adorn": ["deface", "tarnish", "embellish", "burnish", "garnish", "furnish", "mar", "disfigure", "illuminate", "lacquer", "enhance", "cultivate"],
    "adumbrate": ["elaborate", "elucidate", "expound", "articulate", "delineate", "intimate", "insinuate", "allude", "portend", "foreshadow", "imply", "stipulate"],
    "advocate": ["denounce", "oppose", "condemn", "discourage", "disparage", "champion", "promote", "endorse", "censure", "critique", "refute", "propose"],
    "aggrandize": ["diminish", "undermine", "curtail", "bolster", "fortify", "embellish", "inflate", "cultivate", "abate", "depreciate", "erode", "magnify"],
    "allay": ["exacerbate", "aggravate", "intensify", "provoke", "incite", "inflame", "mitigate", "compound", "amplify", "kindle", "escalate", "stoke"],
    "allege": ["verify", "substantiate", "confirm", "corroborate", "refute", "attest", "contend", "assert", "surmise", "postulate", "speculate", "insinuate"],
    "alleviate": ["exacerbate", "aggravate", "intensify", "compound", "worsen", "amplify", "curtail", "prolong", "diminish", "bolster", "rectify", "restore"],
    "allocate": ["confiscate", "appropriate", "hoard", "squander", "deplete", "consolidate", "disperse", "withhold", "amass", "disburse", "ration", "accumulate"],
    "amalgamate": ["segregate", "fracture", "fragment", "dissolve", "partition", "consolidate", "converge", "integrate", "disperse", "diverge", "splinter", "differentiate"],
    "ameliorate": ["exacerbate", "aggravate", "compound", "diminish", "impair", "undermine", "sustain", "bolster", "rectify", "restore", "revitalize", "intensify"],
    "annex": ["relinquish", "cede", "surrender", "appropriate", "confiscate", "commandeer", "liberate", "occupy", "allocate", "reclaim", "seize", "vacate"],
    "annul": ["ratify", "enact", "enforce", "validate", "sanction", "decree", "affirm", "uphold", "institute", "authorize", "amend", "revoke"],
    "appease": ["provoke", "antagonize", "incite", "inflame", "aggravate", "exacerbate", "console", "rebuke", "admonish", "placate", "cajole", "agitate"],
    "appraise": ["disregard", "overlook", "neglect", "estimate", "scrutinize", "discern", "calibrate", "survey", "quantify", "audit", "inventory", "tabulate"],
    "apprehend": ["liberate", "release", "exonerate", "detain", "evade", "elude", "ascertain", "discern", "overlook", "disregard", "misconceive", "surmise"],
    "appropriate": ["relinquish", "surrender", "forfeit", "bequeath", "bestow", "allocate", "dispense", "requisition", "donate", "distribute", "confiscate", "commandeer"],
    "arrogate": ["relinquish", "abdicate", "bestow", "delegate", "appropriate", "commandeer", "usurp", "forfeit", "cede", "surrender", "allocate", "confer"],
    "ascertain": ["surmise", "speculate", "conjecture", "presume", "postulate", "verify", "corroborate", "scrutinize", "discern", "deduce", "hypothesize", "assume"],
    "ascribe": ["deny", "disclaim", "disavow", "allege", "infer", "deduce", "impute", "designate", "stipulate", "assert", "contend", "presume"],
    "aspire": ["resign", "succumb", "abstain", "languish", "stagnate", "covet", "endeavor", "yearn", "crave", "pursue", "persist", "contend"],
    "assail": ["defend", "protect", "shield", "accost", "berate", "confront", "rebuke", "chastise", "denounce", "censure", "impugn", "bombard"],
    "assess": ["disregard", "overlook", "neglect", "estimate", "conjecture", "surmise", "calibrate", "scrutinize", "audit", "quantify", "tabulate", "survey"],

    # NOUNS
    "aberration": ["precedent", "paradigm", "phenomenon", "anomaly", "archetype", "antithesis", "anecdote", "artifact", "epitome", "manifestation", "deviation", "discrepancy"],
    "abnegation": ["indulgence", "avarice", "extravagance", "austerity", "abstinence", "sacrifice", "opulence", "fortitude", "temperance", "frugality", "moderation", "decadence"],
    "absolution": ["condemnation", "censure", "indictment", "retribution", "penance", "atonement", "reprieve", "amnesty", "pardon", "verdict", "exoneration", "clemency"],
    "acclaim": ["censure", "ridicule", "contempt", "derision", "scorn", "notoriety", "indifference", "scrutiny", "rebuke", "infamy", "disdain", "enmity"],
    "accolade": ["censure", "rebuke", "reprimand", "stigma", "criticism", "commendation", "tribute", "indictment", "honor", "sanction", "citation", "distinction"],
    "accord": ["discord", "dispute", "impasse", "schism", "rift", "consensus", "compromise", "concession", "pact", "mandate", "decree", "covenant"],
    "accretion": ["erosion", "depletion", "attrition", "diminution", "accumulation", "expansion", "aggregation", "reduction", "surplus", "deficit", "increment", "remnant"],
    "acrimony": ["camaraderie", "cordiality", "rapport", "civility", "friction", "discord", "rancor", "tension", "animosity", "malice", "resentment", "contention"],
    "acumen": ["naivete", "ignorance", "incompetence", "intuition", "sagacity", "prowess", "aptitude", "finesse", "prudence", "foresight", "discernment", "instinct"],
    "adulation": ["censure", "contempt", "derision", "scorn", "ridicule", "flattery", "reverence", "admiration", "criticism", "indifference", "rebuke", "disdain"],
    "affinity": ["aversion", "antipathy", "discord", "detachment", "apathy", "rapport", "kinship", "inclination", "bias", "predilection", "proclivity", "enmity"],
    "affront": ["compliment", "accolade", "tribute", "slight", "insult", "indignity", "transgression", "provocation", "grievance", "courtesy", "commendation", "gesture"],
    "aggregate": ["fragment", "fraction", "remnant", "component", "surplus", "deficit", "composite", "compilation", "inventory", "assortment", "array", "quota"],
    "agriculture": ["commerce", "industry", "infrastructure", "horticulture", "forestry", "husbandry", "cultivation", "enterprise", "manufacture", "craftsmanship", "conservation", "irrigation"],
    "aisle": ["corridor", "vestibule", "foyer", "atrium", "threshold", "alcove", "terrace", "balcony", "facade", "partition", "arcade", "promenade"],
    "alacrity": ["reluctance", "lethargy", "indifference", "apathy", "hesitation", "trepidation", "fervor", "diligence", "zeal", "haste", "vigor", "tenacity"],
    "alias": ["moniker", "epithet", "title", "acronym", "pseudonym", "designation", "surname", "credential", "emblem", "insignia", "trademark", "namesake"],
    "altercation": ["consensus", "accord", "reconciliation", "discourse", "dispute", "debacle", "confrontation", "feud", "quarrel", "skirmish", "commotion", "standoff"],
    "amenity": ["liability", "burden", "nuisance", "hindrance", "deficiency", "luxury", "commodity", "provision", "accessory", "fixture", "apparatus", "supplement"],
    "analgesic": ["stimulant", "sedative", "antidote", "toxin", "remedy", "palliative", "tonic", "elixir", "anesthetic", "compound", "supplement", "placebo"],
    "anarchist": ["autocrat", "tyrant", "despot", "monarch", "patriarch", "partisan", "insurgent", "radical", "zealot", "dissident", "idealist", "agitator"],
    "anathema": ["blessing", "boon", "godsend", "privilege", "pariah", "scourge", "nemesis", "heresy", "taboo", "stigma", "nuisance", "menace"],
    "anecdote": ["treatise", "manifesto", "chronicle", "testimony", "allegory", "parable", "fable", "proverb", "quip", "memoir", "excerpt", "vignette"],
    "anesthesia": ["sensation", "stimulus", "consciousness", "numbness", "paralysis", "sedation", "lethargy", "stupor", "torpor", "delirium", "vertigo", "malaise"],
    "anguish": ["bliss", "euphoria", "serenity", "composure", "melancholy", "resentment", "dismay", "indignation", "despair", "remorse", "tribulation", "adversity"],
    "anomaly": ["norm", "standard", "precedent", "paradigm", "archetype", "aberration", "peculiarity", "discrepancy", "phenomenon", "rarity", "inconsistency", "paradox"],
    "antagonism": ["camaraderie", "rapport", "solidarity", "affinity", "empathy", "acrimony", "friction", "animosity", "resentment", "contempt", "malice", "discord"],
    "antecedent": ["consequence", "aftermath", "sequel", "culmination", "outcome", "catalyst", "precursor", "predecessor", "harbinger", "origin", "genesis", "impetus"],
    "anthology": ["manuscript", "chronicle", "treatise", "compendium", "archive", "memoir", "journal", "gazette", "almanac", "digest", "volume", "tome"],
    "antithesis": ["complement", "corollary", "parallel", "counterpart", "analogy", "paradox", "contradiction", "anomaly", "deviation", "juxtaposition", "dichotomy", "inverse"],
    "anxiety": ["serenity", "composure", "confidence", "indifference", "trepidation", "melancholy", "apprehension", "unease", "foreboding", "dread", "paranoia", "consternation"],
    "approbation": ["censure", "condemnation", "disapproval", "reproach", "rebuke", "contempt", "derision", "scorn", "ridicule", "commendation", "endorsement", "sanction"],
    "arbiter": ["partisan", "advocate", "litigant", "adversary", "mediator", "delegate", "envoy", "proxy", "intermediary", "adjudicator", "magistrate", "counselor"],
    "arbitration": ["litigation", "confrontation", "impasse", "mediation", "negotiation", "deliberation", "tribunal", "proceeding", "verdict", "settlement", "reconciliation", "adjudication"],
    "ardor": ["apathy", "indifference", "lethargy", "complacency", "fervor", "tenacity", "devotion", "conviction", "passion", "intensity", "vigor", "resolve"],
    "artifact": ["replica", "counterfeit", "facsimile", "specimen", "relic", "remnant", "heirloom", "antiquity", "fossil", "monument", "vestige", "memento"],
    "artisan": ["novice", "apprentice", "amateur", "entrepreneur", "connoisseur", "virtuoso", "laborer", "merchant", "vendor", "curator", "patron", "maestro"],
    "aspersion": ["accolade", "commendation", "tribute", "compliment", "endorsement", "allegation", "innuendo", "slander", "insinuation", "reproach", "rebuke", "diatribe"],

    # ADJECTIVES
    "abject": ["exalted", "dignified", "resilient", "stoic", "desolate", "destitute", "forlorn", "squalid", "dismal", "austere", "harrowing", "grievous"],
    "abstruse": ["lucid", "transparent", "straightforward", "rudimentary", "convoluted", "cryptic", "esoteric", "ambiguous", "obscure", "enigmatic", "inscrutable", "perplexing"],
    "accessible": ["prohibitive", "elusive", "exclusive", "obscure", "remote", "esoteric", "ubiquitous", "conspicuous", "prevalent", "abundant", "sparse", "scarce"],
    "accommodating": ["obstinate", "inflexible", "intransigent", "petulant", "cantankerous", "amenable", "compliant", "gracious", "congenial", "indulgent", "officious", "perfunctory"],
    "acerbic": ["affable", "genial", "cordial", "amiable", "sardonic", "caustic", "scathing", "mordant", "venomous", "trenchant", "incisive", "wry"],
    "acute": ["obtuse", "dull", "superficial", "negligible", "chronic", "profound", "discerning", "astute", "perceptive", "shrewd", "incisive", "piercing"],
    "adamant": ["amenable", "pliant", "acquiescent", "malleable", "resolute", "steadfast", "obstinate", "tenacious", "unwavering", "intransigent", "staunch", "defiant"],
    "adept": ["inept", "clumsy", "incompetent", "mediocre", "versatile", "resourceful", "astute", "ingenious", "proficient", "masterful", "accomplished", "novice"],
    "adroit": ["inept", "clumsy", "awkward", "maladroit", "versatile", "astute", "resourceful", "shrewd", "nimble", "ingenious", "deft", "agile"],
    "adverse": ["favorable", "beneficial", "auspicious", "propitious", "hostile", "detrimental", "precarious", "perilous", "ominous", "formidable", "dire", "onerous"],
    "aerial": ["terrestrial", "subterranean", "aquatic", "nautical", "celestial", "orbital", "elevated", "lofty", "buoyant", "ethereal", "atmospheric", "vertical"],
    "aesthetic": ["utilitarian", "functional", "pragmatic", "mundane", "ornamental", "exquisite", "picturesque", "idyllic", "opulent", "lavish", "gaudy", "ostentatious"],
    "affable": ["aloof", "austere", "taciturn", "reserved", "brusque", "curt", "genial", "cordial", "gregarious", "congenial", "jovial", "personable"],
    "affluent": ["destitute", "impoverished", "indigent", "austere", "frugal", "lavish", "opulent", "extravagant", "prosperous", "ostentatious", "bourgeois", "privileged"],
    "aggrieved": ["content", "complacent", "gratified", "indifferent", "resentful", "embittered", "disgruntled", "indignant", "vindictive", "despondent", "dismayed", "incensed"],
    "agile": ["sluggish", "cumbersome", "lethargic", "unwieldy", "nimble", "deft", "lithe", "supple", "versatile", "fleet", "vigorous", "robust"],
    "agnostic": ["devout", "pious", "fervent", "dogmatic", "skeptical", "secular", "impartial", "ambivalent", "indifferent", "apathetic", "pragmatic", "empirical"],
    "aloof": ["gregarious", "sociable", "affable", "genial", "cordial", "reticent", "taciturn", "stoic", "indifferent", "detached", "nonchalant", "apathetic"],
    "altruistic": ["selfish", "avaricious", "mercenary", "opportunistic", "magnanimous", "benevolent", "philanthropic", "compassionate", "charitable", "selfless", "noble", "virtuous"],
    "ambiguous": ["explicit", "definitive", "unequivocal", "categorical", "cryptic", "nebulous", "enigmatic", "convoluted", "elusive", "tentative", "paradoxical", "misleading"],
    "ambivalent": ["resolute", "decisive", "adamant", "steadfast", "indecisive", "hesitant", "conflicted", "tentative", "apathetic", "indifferent", "vacillating", "uncertain"],
    "amenable": ["obstinate", "defiant", "intransigent", "recalcitrant", "compliant", "docile", "malleable", "receptive", "tractable", "acquiescent", "obliging", "reluctant"],
    "amiable": ["surly", "cantankerous", "brusque", "aloof", "affable", "cordial", "congenial", "gregarious", "jovial", "genial", "gracious", "sociable"],
    "amicable": ["hostile", "contentious", "belligerent", "antagonistic", "cordial", "congenial", "harmonious", "diplomatic", "equitable", "cooperative", "collegial", "civil"],
    "amorous": ["indifferent", "platonic", "aloof", "detached", "ardent", "fervent", "passionate", "devoted", "infatuated", "sentimental", "wistful", "enamored"],
    "amorphous": ["rigid", "crystalline", "defined", "structured", "nebulous", "diffuse", "fluid", "malleable", "ephemeral", "transient", "elusive", "intangible"],
    "anachronistic": ["contemporary", "modern", "current", "progressive", "antiquated", "archaic", "obsolete", "outmoded", "retrograde", "nostalgic", "traditional", "conventional"],
    "analogous": ["disparate", "dissimilar", "incongruent", "antithetical", "equivalent", "commensurate", "corresponding", "parallel", "comparable", "akin", "congruent", "homogeneous"],
    "animated": ["listless", "lethargic", "somber", "subdued", "spirited", "exuberant", "vivacious", "buoyant", "ebullient", "boisterous", "effervescent", "fervent"],
    "anonymous": ["renowned", "illustrious", "prominent", "conspicuous", "obscure", "enigmatic", "elusive", "nondescript", "inconspicuous", "unassuming", "discreet", "clandestine"],
    "antediluvian": ["contemporary", "innovative", "cutting-edge", "progressive", "antiquated", "archaic", "obsolete", "medieval", "primordial", "prehistoric", "fossilized", "decrepit"],
    "antiquated": ["contemporary", "innovative", "modern", "cutting-edge", "archaic", "obsolete", "dilapidated", "decrepit", "outmoded", "rudimentary", "primitive", "conventional"],
    "antiseptic": ["contaminated", "squalid", "fetid", "polluted", "sterile", "pristine", "immaculate", "austere", "clinical", "sanitary", "spartan", "barren"],
    "apathetic": ["passionate", "zealous", "fervent", "ardent", "indifferent", "nonchalant", "complacent", "dispassionate", "detached", "aloof", "stoic", "impassive"],
    "apocryphal": ["authentic", "verified", "substantiated", "documented", "spurious", "dubious", "fabricated", "unsubstantiated", "speculative", "legendary", "mythical", "fictitious"],
    "appalling": ["commendable", "admirable", "exemplary", "laudable", "deplorable", "egregious", "atrocious", "heinous", "ghastly", "abhorrent", "reprehensible", "unconscionable"],
    "aquatic": ["terrestrial", "arboreal", "aerial", "subterranean", "marine", "maritime", "coastal", "amphibious", "tropical", "arid", "temperate", "riparian"],
    "arable": ["barren", "desolate", "arid", "infertile", "fertile", "verdant", "lush", "cultivated", "temperate", "tropical", "irrigated", "pastoral"],
    "arbitrary": ["systematic", "methodical", "deliberate", "calculated", "haphazard", "capricious", "whimsical", "erratic", "impulsive", "spontaneous", "random", "indiscriminate"],
    "arboreal": ["aquatic", "terrestrial", "subterranean", "aerial", "tropical", "verdant", "pastoral", "rustic", "sylvan", "perennial", "deciduous", "botanical"],
    "arcane": ["commonplace", "transparent", "accessible", "rudimentary", "esoteric", "cryptic", "enigmatic", "abstruse", "occult", "mystical", "clandestine", "inscrutable"],
    "archaic": ["contemporary", "innovative", "modern", "progressive", "antiquated", "obsolete", "medieval", "primitive", "outmoded", "decrepit", "rudimentary", "conventional"],
    "archetypal": ["atypical", "anomalous", "aberrant", "unique", "quintessential", "prototypical", "emblematic", "canonical", "definitive", "iconic", "seminal", "paradigmatic"],
    "arid": ["lush", "verdant", "fertile", "temperate", "barren", "desolate", "austere", "bleak", "parched", "scorched", "inhospitable", "stark"],
    "ascetic": ["indulgent", "hedonistic", "opulent", "lavish", "austere", "spartan", "frugal", "stoic", "monastic", "devout", "pious", "rigorous"],
    "assiduous": ["negligent", "indolent", "lackadaisical", "complacent", "meticulous", "scrupulous", "conscientious", "fastidious", "methodical", "painstaking", "tireless", "relentless"],
}

# For words not in the manual pools, generate from POS list
def get_pool(word):
    if word in distractor_pools:
        # Filter pool to only include words in our master list
        return [w for w in distractor_pools[word] if w in pos_map and pos_map[w] == pos_map[word]]
    return []

def get_synonyms(word):
    """Words too close in meaning to use as distractors"""
    syn_map = {
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
        "ardor": {"passion", "fervor", "zeal", "enthusiasm", "intensity"},
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
        "adept": {"skilled", "proficient", "dexterous", "masterful", "accomplished"},
        "adroit": {"skilled", "deft", "nimble", "dexterous", "proficient"},
        "adverse": {"unfavorable", "detrimental", "hostile", "harmful"},
        "aerial": {"airborne"},
        "aesthetic": {"artistic", "beautiful"},
        "affable": {"friendly", "amiable", "genial", "cordial", "amicable", "sociable"},
        "affluent": {"wealthy", "rich", "prosperous", "opulent"},
        "aggrieved": {"wronged", "distressed", "hurt"},
        "agile": {"nimble", "quick", "lithe", "spry"},
        "agnostic": {"skeptical"},
        "aloof": {"distant", "detached", "remote", "standoffish", "reserved"},
        "altruistic": {"selfless", "charitable", "philanthropic", "magnanimous", "benevolent"},
        "ambiguous": {"vague", "unclear", "equivocal", "nebulous"},
        "ambivalent": {"conflicted", "undecided", "torn"},
        "amenable": {"willing", "compliant", "cooperative", "receptive", "agreeable", "acquiescent"},
        "amiable": {"friendly", "affable", "genial", "cordial", "amicable", "likable"},
        "amicable": {"friendly", "cordial", "harmonious", "affable", "amiable"},
        "amorous": {"romantic", "passionate", "loving"},
        "amorphous": {"shapeless", "formless", "nebulous"},
        "anachronistic": {"outdated", "outmoded"},
        "analogous": {"similar", "comparable", "akin", "parallel", "corresponding"},
        "animated": {"lively", "spirited", "vivacious", "vibrant", "exuberant", "energetic"},
        "anonymous": {"unnamed", "unknown", "unidentified"},
        "antediluvian": {"ancient", "archaic", "antiquated", "prehistoric", "primordial"},
        "antiquated": {"outdated", "archaic", "obsolete", "old-fashioned"},
        "antiseptic": {"sterile", "clean", "sanitary"},
        "apathetic": {"indifferent", "unconcerned", "unmoved", "dispassionate", "impassive"},
        "apocryphal": {"fictitious", "false", "fabricated", "spurious", "dubious", "unsubstantiated"},
        "appalling": {"horrifying", "shocking", "dreadful", "atrocious", "ghastly", "deplorable"},
        "aquatic": {"marine", "maritime", "nautical"},
        "arable": {"fertile", "cultivable"},
        "arbitrary": {"random", "capricious", "whimsical", "haphazard"},
        "arboreal": {"sylvan"},
        "arcane": {"esoteric", "obscure", "cryptic", "mysterious", "abstruse", "recondite"},
        "archaic": {"ancient", "antiquated", "obsolete", "antediluvian"},
        "archetypal": {"quintessential", "prototypical", "exemplary", "definitive"},
        "arid": {"dry", "parched", "barren"},
        "ascetic": {"austere", "spartan", "abstemious", "frugal"},
        "assiduous": {"diligent", "industrious", "tireless", "meticulous", "conscientious", "sedulous"},
    }
    return syn_map.get(word, set())

def pick_distractors_from_pool(word, pool, sentence_idx, used_sets):
    """Pick 3 from the curated pool, varying across sentences"""
    synonyms = get_synonyms(word)
    valid_pool = [w for w in pool if w != word and w not in synonyms and w in pos_map]
    
    if len(valid_pool) < 3:
        # Supplement from full POS list
        pos = pos_map[word]
        extras = [w for w in all_words_by_pos[pos] if w != word and w not in synonyms and w not in valid_pool]
        random.shuffle(extras)
        valid_pool.extend(extras[:20])
    
    # Try different combinations to avoid reusing same set
    attempts = 0
    best = None
    while attempts < 100:
        random.shuffle(valid_pool)
        picked = valid_pool[:3]
        if len(picked) < 3:
            break
        picked_set = frozenset(picked)
        if picked_set not in used_sets:
            used_sets.add(picked_set)
            return picked
        if best is None:
            best = picked
        attempts += 1
    
    # If we couldn't find a unique set, return whatever we have
    return best if best else valid_pool[:3]

# Generate output
output = {}

for word in chunk0_words:
    pos = pos_map[word]
    definition = word_info[word]["d"]
    word_sentences = sentences.get(word, [])
    
    pool = get_pool(word)
    
    # If no curated pool, build one from POS list
    if not pool:
        synonyms = get_synonyms(word)
        pool = [w for w in all_words_by_pos[pos] if w != word and w not in synonyms]
        random.shuffle(pool)
        pool = pool[:15]
    
    used_distractor_sets = set()
    entries = []
    
    for i, sent in enumerate(word_sentences[:8]):
        distractors = pick_distractors_from_pool(word, pool, i, used_distractor_sets)
        entries.append([sent] + distractors)
    
    while len(entries) < 8:
        entries.append(["", "", "", ""])
    
    output[word] = entries

# Validate
total_entries = sum(len(v) for v in output.values())
print(f"Generated output for {len(output)} words, {total_entries} total entries")

# Check all distractors are in master list
errors = 0
for word, entries in output.items():
    for i, entry in enumerate(entries):
        if entry[0] == "":
            continue
        for d in entry[1:4]:
            if d not in pos_map:
                print(f"ERROR: {word} sentence {i}: distractor '{d}' not in word list")
                errors += 1
            elif pos_map[d] != pos_map[word]:
                print(f"ERROR: {word} sentence {i}: distractor '{d}' has POS {pos_map[d]}, expected {pos_map[word]}")
                errors += 1

print(f"Validation errors: {errors}")

# Check no distractor is a synonym
syn_errors = 0
for word, entries in output.items():
    syns = get_synonyms(word)
    for i, entry in enumerate(entries):
        if entry[0] == "":
            continue
        for d in entry[1:4]:
            if d in syns:
                print(f"SYNONYM ERROR: {word} sentence {i}: distractor '{d}' is a synonym")
                syn_errors += 1

print(f"Synonym errors: {syn_errors}")

# Write output
import os
os.makedirs('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp', exist_ok=True)
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_0_output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Written to tmp/chunk_0_output.json")

# Sample output
for w in ["abase", "aberration", "assiduous"]:
    print(f"\n{w}:")
    for entry in output[w]:
        print(f"  [{entry[0][:60]}..., {entry[1]}, {entry[2]}, {entry[3]}]")
