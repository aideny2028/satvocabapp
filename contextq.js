// Original SAT-style "Words in Context" passage questions (authored for this app).
// Format mirrors the digital SAT's Craft & Structure > Words in Context items:
// a short passage (25-60 words) with a blank, four same-POS choices, one of
// which is forced by an explicit context clue (restatement / contrast / cause-effect).
// Every passage and choice set here is original content.
// Entry: word -> [{p: passage-with-_____, d: [3 distractors], diff, clue}]
const CONTEXTQ = {
  "mitigate": [{
    p: "Coastal engineers cannot prevent hurricanes from striking the city, but the new system of levees and pumping stations should _____ the flooding they cause, reducing water damage in low-lying neighborhoods by more than half.",
    d: ["measure", "predict", "prolong"], diff: "easy", clue: "restatement"
  }],
  "ubiquitous": [{
    p: "Once a specialized tool used only in research laboratories, the sensor has become _____ in modern life: it is now found in phones, cars, thermostats, doorbells, and even running shoes.",
    d: ["fragile", "obsolete", "expensive"], diff: "easy", clue: "restatement"
  }],
  "ambivalent": [{
    p: "Reviewers were _____ about the museum's renovation: they praised the light-filled galleries as a triumph while lamenting that the intimate character of the original building had been lost.",
    d: ["indifferent", "enthusiastic", "dismissive"], diff: "medium", clue: "contrast"
  }],
  "corroborate": [{
    p: "The historian's account of the flood, once dismissed as exaggeration, gained credibility when tree-ring data and sediment cores from the river delta appeared to _____ her timeline of events.",
    d: ["contradict", "obscure", "predate"], diff: "medium", clue: "cause-effect"
  }],
  "undermine": [{
    p: "The senator argued that publishing the committee's internal disagreements would _____ public confidence in the final report, since readers might mistake ordinary debate for evidence that the conclusions were unsound.",
    d: ["restore", "reflect", "exceed"], diff: "easy", clue: "cause-effect"
  }],
  "bolster": [{
    p: "To _____ its claim that the painting was authentic, the auction house commissioned pigment analysis, infrared imaging, and a review of the work's ownership records — each of which supported the attribution.",
    d: ["withdraw", "complicate", "summarize"], diff: "medium", clue: "restatement"
  }],
  "arbitrary": [{
    p: "Critics called the new dress code _____, noting that the rules seemed to follow no consistent principle: sandals were banned while flip-flops were permitted, and hats were forbidden only on Tuesdays.",
    d: ["strict", "practical", "traditional"], diff: "easy", clue: "restatement"
  }],
  "ephemeral": [{
    p: "Unlike bronze sculptures, which can endure for millennia, the artist's ice installations are deliberately _____: each begins melting the moment it is unveiled and vanishes entirely within hours.",
    d: ["monumental", "abstract", "priceless"], diff: "medium", clue: "contrast"
  }],
  "pragmatic": [{
    p: "While her rivals debated the ideal design for the water system, the mayor took a more _____ approach, repairing the pipes the city already had with the budget it could actually afford.",
    d: ["idealistic", "cautious", "ambitious"], diff: "easy", clue: "contrast"
  }],
  "scrutinize": [{
    p: "Before approving the bridge design, inspectors will _____ every weld and cable specification, examining each detail line by line for flaws that a casual review might miss.",
    d: ["approve", "simplify", "duplicate"], diff: "medium", clue: "restatement"
  }],
  "benevolent": [{
    p: "Though the factory owner cultivated a _____ public image — funding orphanages and endowing hospitals — his workers knew a different man, one who cut wages at the first sign of falling profits.",
    d: ["modest", "shrewd", "flamboyant"], diff: "easy", clue: "contrast"
  }],
  "candid": [{
    p: "The memoir is strikingly _____: rather than polishing her past, the author admits her failures, names her regrets, and describes her ambitions with an honesty that reviewers found disarming.",
    d: ["nostalgic", "guarded", "lyrical"], diff: "medium", clue: "restatement"
  }],
  "prudent": [{
    p: "Given how quickly mountain weather can turn, the guide considered it _____ to pack extra fuel and food even for a day hike, a precaution that seemed excessive until the fog rolled in.",
    d: ["reckless", "generous", "customary"], diff: "medium", clue: "cause-effect"
  }],
  "lucid": [{
    p: "What sets the textbook apart is its _____ prose: concepts that other authors bury in jargon are laid out so clearly that first-year students can follow the argument unaided.",
    d: ["ornate", "terse", "scholarly"], diff: "easy", clue: "restatement"
  }],
  "tenuous": [{
    p: "The prosecution's case rested on a _____ chain of inference — a partial footprint, a witness who saw only a silhouette, and a receipt that placed the defendant merely in the same county.",
    d: ["compelling", "elaborate", "familiar"], diff: "medium", clue: "restatement"
  }],
  "exacerbate": [{
    p: "Officials worried that draining the wetlands would _____ the region's flooding rather than relieve it, since the marshes had long acted as a natural sponge during heavy rains.",
    d: ["resolve", "postpone", "reveal"], diff: "medium", clue: "contrast"
  }],
  "substantiate": [{
    p: "Extraordinary claims require more than eloquence: unless the laboratory can _____ its announcement with data that other researchers are able to reproduce, the discovery will remain in doubt.",
    d: ["publicize", "embellish", "retract"], diff: "medium", clue: "cause-effect"
  }],
  "capricious": [{
    p: "Sailors dreaded the strait's _____ winds, which might deliver a gentle following breeze in the morning and, without warning or pattern, a violent squall by afternoon.",
    d: ["steady", "frigid", "favorable"], diff: "medium", clue: "restatement"
  }],
  "prolific": [{
    p: "A remarkably _____ composer, she produced eleven symphonies, four operas, and more than two hundred songs in a career that lasted barely twenty-five years.",
    d: ["celebrated", "meticulous", "reclusive"], diff: "medium", clue: "restatement"
  }],
  "reticent": [{
    p: "In interviews the physicist was _____ about her private life, steering every question back to her research; colleagues joked that they learned of her marriage from a footnote.",
    d: ["boastful", "confused", "candid"], diff: "medium", clue: "restatement"
  }],
  "venerate": [{
    p: "Generations of engineers have come to _____ the bridge's designer, treating her notebooks as sacred texts and making pilgrimages to the small workshop where she drafted the original plans.",
    d: ["imitate", "question", "outshine"], diff: "hard", clue: "restatement"
  }],
  "obscure": [{
    p: "The professor delighted in championing _____ composers — figures so little known that even specialists in the period often could not place their names.",
    d: ["prolific", "beloved", "modern"], diff: "easy", clue: "restatement"
  }],
  "diligent": [{
    p: "The archive's catalog exists only because of one _____ librarian, who spent thirty years indexing every letter, ledger, and photograph the collection received.",
    d: ["fortunate", "reluctant", "temporary"], diff: "easy", clue: "restatement"
  }],
  "innocuous": [{
    p: "The compound looked _____ in early trials — volunteers reported nothing worse than mild drowsiness — but researchers cautioned that harmless short-term results do not guarantee long-term safety.",
    d: ["potent", "unstable", "synthetic"], diff: "medium", clue: "restatement"
  }],
  "tangible": [{
    p: "Investors grew impatient with the startup's talk of vision and momentum; they wanted _____ results — signed contracts, shipped products, revenue that could be counted.",
    d: ["ambitious", "theoretical", "gradual"], diff: "medium", clue: "restatement"
  }],
  "skeptical": [{
    p: "Astronomers were initially _____ of the signal's cosmic origin, suspecting instead that a microwave oven in the observatory's break room was to blame — a hypothesis that, embarrassingly, proved correct.",
    d: ["envious", "confident", "unaware"], diff: "medium", clue: "cause-effect"
  }],
  "meticulous": [{
    p: "Restoring the fresco required _____ labor: conservators worked with brushes the size of a pencil tip, cleaning a few square centimeters each day and logging every stroke.",
    d: ["improvised", "occasional", "strenuous"], diff: "easy", clue: "restatement"
  }],
  "resilient": [{
    p: "Ecologists chose the marsh grass precisely because it is so _____: trampled by storms, burned by salt, and grazed by geese, it nonetheless returns each spring as dense as before.",
    d: ["ornamental", "delicate", "invasive"], diff: "easy", clue: "restatement"
  }]
};
