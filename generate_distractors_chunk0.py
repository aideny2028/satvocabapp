import re
import json
import random

random.seed(42)

# Parse words.js
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/words.js') as f:
    content = f.read()

words_data = re.findall(r'\{w:"([^"]+)",p:"([^"]+)",d:"([^"]+)"\}', content)
print(f"Parsed {len(words_data)} words")

# Build POS map and word info
pos_map = {}
word_info = {}
all_words_by_pos = {"v": [], "n": [], "adj": []}

for w, p, d in words_data:
    pos_key = p.replace(".", "")  # "v." -> "v", "n." -> "n", "adj." -> "adj"
    pos_map[w] = pos_key
    word_info[w] = {"w": w, "p": pos_key, "d": d}
    if pos_key in all_words_by_pos:
        all_words_by_pos[pos_key].append(w)

print(f"Verbs: {len(all_words_by_pos['v'])}, Nouns: {len(all_words_by_pos['n'])}, Adj: {len(all_words_by_pos['adj'])}")

# Parse sentences.js
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/sentences.js') as f:
    sent_content = f.read()

# Parse the JS object
sentences = {}
current_word = None
current_sentences = []

for line in sent_content.split('\n'):
    line = line.strip()
    # Match word key like "abase":[
    m = re.match(r'"([^"]+)":\[', line)
    if m:
        if current_word and current_sentences:
            sentences[current_word] = current_sentences
        current_word = m.group(1)
        current_sentences = []
        continue
    # Match sentence line
    m = re.match(r'"(.+)"[,]?$', line)
    if m:
        current_sentences.append(m.group(1))
        continue
    if line == '],':
        if current_word and current_sentences:
            sentences[current_word] = current_sentences
        current_word = None
        current_sentences = []

# Handle last word
if current_word and current_sentences:
    sentences[current_word] = current_sentences

print(f"Parsed sentences for {len(sentences)} words")

# Chunk 0: abase through assiduous (indices 0-125)
chunk0_words = [w for w, p, d in words_data[:126]]
print(f"Chunk 0: {len(chunk0_words)} words, from {chunk0_words[0]} to {chunk0_words[-1]}")

# Define synonym groups to avoid picking synonyms as distractors
# We'll define these manually for the chunk 0 words and their likely distractors
synonym_groups = {
    # humiliate/degrade group
    "abase": {"debase", "demean", "degrade", "humiliate"},
    "debase": {"abase", "demean", "degrade"},
    # reduce/lessen group
    "abate": {"diminish", "lessen", "wane", "ebb", "subside", "dwindle", "alleviate", "mitigate"},
    "alleviate": {"abate", "assuage", "mitigate", "palliate", "ameliorate"},
    "ameliorate": {"alleviate", "improve"},
    "assuage": {"alleviate", "mitigate", "palliate", "appease", "allay"},
    "allay": {"assuage", "alleviate", "mitigate", "appease"},
    # give up position
    "abdicate": {"renounce", "relinquish", "resign", "abjure"},
    "abjure": {"abdicate", "renounce", "forswear", "recant"},
    # kidnap
    "abduct": {"kidnap", "seize", "snatch"},
    # help/aid
    "abet": {"assist", "aid", "facilitate", "foment"},
    # hate/detest
    "abhor": {"detest", "loathe", "despise", "execrate"},
    # praise
    "acclaim": {"accolade", "approbation", "adulation", "commendation", "kudos"},
    "accolade": {"acclaim", "approbation", "adulation"},
    "approbation": {"acclaim", "accolade", "adulation"},
    "adulation": {"acclaim", "accolade", "approbation"},
    # agree
    "accede": {"acquiesce", "assent", "concur", "consent"},
    "acquiesce": {"accede", "assent", "concur"},
    # bitter
    "acerbic": {"caustic", "mordant", "acrimonious", "sardonic", "trenchant"},
    # hostile
    "antagonism": {"antipathy", "acrimony", "enmity", "hostility"},
    "antipathy": {"antagonism", "acrimony", "aversion", "enmity"},
    "acrimony": {"antagonism", "antipathy", "enmity"},
    "aversion": {"antipathy", "repugnance", "distaste"},
    # skillful
    "adept": {"adroit", "proficient", "dexterous", "skilled"},
    "adroit": {"adept", "proficient", "dexterous"},
    # friendly
    "affable": {"amiable", "amicable", "genial", "cordial", "convivial"},
    "amiable": {"affable", "amicable", "genial", "cordial"},
    "amicable": {"affable", "amiable", "cordial"},
    # old/outdated
    "antiquated": {"archaic", "antediluvian", "obsolete"},
    "archaic": {"antiquated", "antediluvian", "obsolete"},
    "antediluvian": {"antiquated", "archaic", "obsolete"},
    "anachronistic": {"antiquated", "archaic", "antediluvian"},
    # anomaly/aberration
    "aberration": {"anomaly", "deviation"},
    "anomaly": {"aberration", "deviation"},
    # attack
    "assail": {"assault", "berate", "lambaste"},
    # evaluate
    "assess": {"appraise", "evaluate"},
    "appraise": {"assess", "evaluate"},
    # hard-working
    "assiduous": {"diligent", "industrious", "sedulous", "meticulous"},
    # calm/soothe
    "appease": {"assuage", "mollify", "placate", "pacify", "allay", "conciliate"},
    # bold
    "audacious": {"brazen", "intrepid"},
    # eager
    "alacrity": {"ardor", "fervor", "zeal"},
    "ardor": {"alacrity", "fervor", "zeal", "passion"},
    # wretched
    "abject": {"deplorable", "wretched", "appalling"},
    "appalling": {"abject", "deplorable", "atrocious", "egregious", "heinous"},
    # dry
    "arid": {"barren", "austere"},
    "austere": {"arid", "spartan", "ascetic"},
    "ascetic": {"austere", "spartan"},
    # wealth
    "affluent": {"opulent", "prosperous"},
    "avarice": {"cupidity", "greed"},
    # ancient
    "arcane": {"esoteric", "abstruse", "recondite", "cryptic"},
    "abstruse": {"arcane", "esoteric", "recondite"},
    # insult
    "affront": {"indignity", "slight"},
    # anxiety
    "anxiety": {"anguish", "trepidation", "apprehension"},
    "anguish": {"anxiety", "torment", "agony"},
    # take
    "appropriate": {"arrogate", "usurp", "commandeer"},
    "arrogate": {"appropriate", "usurp"},
    # credit/assign
    "ascribe": {"attribute", "impute"},
    # shape
    "amorphous": {"nebulous", "vague"},
    # similar
    "analogous": {"comparable", "akin"},
}

def get_synonyms(word):
    """Get synonyms for a word to avoid as distractors"""
    syns = set()
    if word in synonym_groups:
        syns = synonym_groups[word]
    # Also check reverse: if word appears in another word's synonym set
    for k, v in synonym_groups.items():
        if word in v:
            syns.add(k)
            syns.update(v)
    syns.discard(word)
    return syns

# Thematic categories for better distractor selection
thematic_categories = {
    "speech_criticism": ["accost", "admonish", "berate", "chastise", "censure", "castigate", "denounce", "disparage", "harangue", "rebuke", "reprimand", "reproach", "upbraid", "vilify", "malign", "impugn", "decry", "lambaste", "excoriate"],
    "praise_approval": ["acclaim", "accolade", "approbation", "adulation", "commend", "extol", "eulogize", "exalt", "laud", "venerate", "revere", "glorify", "lionize", "tout", "herald"],
    "agreement_compliance": ["accede", "acquiesce", "capitulate", "concede", "concur", "comply", "consent", "defer", "relent", "yield", "submit"],
    "deception_trickery": ["beguile", "bilk", "dupe", "delude", "hoodwink", "bamboozle", "swindle", "deceive", "mislead", "dissemble", "fabricate", "feign", "counterfeit"],
    "destruction_reduction": ["abate", "abridge", "abrogate", "annul", "demolish", "eradicate", "expunge", "obliterate", "rescind", "revoke", "nullify", "quash", "repeal", "curtail", "truncate"],
    "improvement_growth": ["aggrandize", "augment", "bolster", "enhance", "fortify", "cultivate", "foster", "nurture", "proliferate", "amplify", "magnify", "escalate"],
    "investigation_understanding": ["ascertain", "discern", "scrutinize", "fathom", "perceive", "apprehend", "comprehend", "construe", "elucidate", "explicate", "illuminate"],
    "escape_hiding": ["abscond", "elude", "evade", "flee", "circumvent", "eschew", "secrete"],
    "attack_conflict": ["assail", "accost", "antagonize", "besiege", "bombard", "buffet", "pillage", "ravage", "vanquish"],
    "emotion_feeling": ["abhor", "cherish", "covet", "disdain", "relish", "resent", "revile", "rue", "savor", "deplore", "lament"],
    "restraint_denial": ["abstain", "abnegation", "abjure", "eschew", "forgo", "refrain", "renounce", "relinquish"],
    "wealth_status": ["affluent", "bourgeois", "opulent", "impoverished", "destitute", "indigent"],
    "character_personality": ["affable", "amiable", "amicable", "aloof", "austere", "benevolent", "callous", "cantankerous", "congenial", "cordial", "docile", "gregarious", "magnanimous", "taciturn"],
}

def pick_distractors(word, sentence_idx, pos, definition, all_same_pos, used_sets):
    """Pick 3 distractors for a word's sentence"""
    synonyms = get_synonyms(word)
    
    # Filter candidates: same POS, not the word itself, not a synonym
    candidates = [w for w in all_same_pos if w != word and w not in synonyms]
    
    # Try to get thematically adjacent words first
    thematic = []
    for cat_name, cat_words in thematic_categories.items():
        if word in cat_words:
            for cw in cat_words:
                if cw in candidates and cw != word:
                    thematic.append(cw)
    
    # Avoid reusing the same set across all 8 sentences
    # Try to pick different distractors each time
    attempts = 0
    while attempts < 50:
        picked = []
        # Start with 1-2 thematic words if available
        thematic_available = [t for t in thematic if t not in picked]
        random.shuffle(thematic_available)
        n_thematic = min(random.randint(1, 2), len(thematic_available))
        picked.extend(thematic_available[:n_thematic])
        
        # Fill remaining from general pool
        remaining = [c for c in candidates if c not in picked]
        random.shuffle(remaining)
        while len(picked) < 3 and remaining:
            picked.append(remaining.pop())
        
        if len(picked) == 3:
            picked_set = frozenset(picked)
            if picked_set not in used_sets:
                used_sets.add(picked_set)
                return picked
        attempts += 1
    
    # Fallback: just pick any 3
    remaining = [c for c in candidates if c not in picked]
    random.shuffle(remaining)
    while len(picked) < 3:
        if remaining:
            picked.append(remaining.pop())
        else:
            break
    return picked[:3]

# Generate output
output = {}

for word in chunk0_words:
    pos = pos_map[word]
    definition = word_info[word]["d"]
    word_sentences = sentences.get(word, [])
    
    if len(word_sentences) != 8:
        print(f"WARNING: {word} has {len(word_sentences)} sentences, expected 8")
    
    same_pos_words = all_words_by_pos[pos]
    used_distractor_sets = set()
    
    entries = []
    for i, sent in enumerate(word_sentences[:8]):
        distractors = pick_distractors(word, i, pos, definition, same_pos_words, used_distractor_sets)
        entries.append([sent] + distractors)
    
    # Pad if fewer than 8 sentences
    while len(entries) < 8:
        entries.append(["", "", "", ""])
    
    output[word] = entries

# Write output
with open('/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/tmp/chunk_0_output.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nGenerated distractors for {len(output)} words")
print("Output written to tmp/chunk_0_output.json")

# Verify structure
for w in list(output.keys())[:3]:
    print(f"\n{w}:")
    for entry in output[w]:
        print(f"  [{entry[0][:50]}..., {entry[1]}, {entry[2]}, {entry[3]}]")
