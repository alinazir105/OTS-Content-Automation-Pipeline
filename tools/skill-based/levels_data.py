# -*- coding: utf-8 -*-
"""Rich lesson content for English Language skill levels 1–12."""

# Each level extends base LEVELS in build_all with:
# teach, showcase, worked, reading, try_it, quiz (7-8 Qs), pills, example (hero card text)

def _q(question, options, correct_index):
    return (question, options, correct_index)


RICH = {
    1: {
        "teach": [
            ("What is a CVC word?", "A <strong>CVC</strong> word has three sounds: <strong>C</strong>onsonant – <strong>V</strong>owel – <strong>C</strong>onsonant. Examples: <em>c-a-t</em>, <em>d-o-g</em>, <em>s-u-n</em>, <em>p-e-n</em>."),
            ("Stretch the sounds", "Say each sound slowly, then blend: /c/ … /a/ … /t/ → <strong>cat</strong>. Blending means pushing sounds together without pausing too long."),
            ("Letters you know", "English has 26 letters. Vowels are <strong>a, e, i, o, u</strong>. All other letters are consonants. CVC words use one vowel in the middle."),
            ("Why order matters", "When spelling, we write letters in the same order we say sounds. <em>t-a-c</em> is not the same word as <em>c-a-t</em>!"),
        ],
        "pills": ["CVC words", "Sound blending", "Letter order", "Tap to pop"],
        "showcase": [
            ("cat", "c → a → t", "green"),
            ("dog", "d → o → g", "green"),
            ("sun", "s → u → n", "amber"),
            ("pen", "p → e → n", "amber"),
            ("big", "b → i → g", "navy"),
            ("hat", "h → a → t", "navy"),
        ],
        "worked": [
            ("Spell <em>cat</em>", [
                "Say the first sound: /c/ → write <strong>c</strong>",
                "Say the middle sound: /a/ → write <strong>a</strong>",
                "Say the last sound: /t/ → write <strong>t</strong>",
                "Read the whole word: <strong>cat</strong>",
            ]),
            ("Spell <em>dog</em>", [
                "First sound /d/ → <strong>d</strong>",
                "Middle /o/ → <strong>o</strong>",
                "Last /g/ → <strong>g</strong>",
                "Blend: <strong>dog</strong>",
            ]),
        ],
        "reading": "Ali has a <em>red hat</em> and a <em>big dog</em>. The <em>sun</em> is hot. He sits on a <em>mat</em> with his dog. Can you find four CVC words in this story?",
        "try_it": [
            ("How many sounds in <strong>pen</strong>?", "Three: /p/ /e/ /n/"),
            ("First letter of <strong>sun</strong>?", "s"),
            ("Which is CVC: <em>tree</em> or <em>cat</em>?", "cat (three sounds only)"),
            ("Blend: /h/ /a/ /t/ = ?", "hat"),
        ],
        "quiz": [
            _q("Which word is a CVC word?", ["cat", "tree", "play", "school"], 0),
            _q("First sound in <em>dog</em>?", ["/d/", "/o/", "/g/", "/og/"], 0),
            _q("How many sounds in <em>sun</em>?", ["3", "2", "4", "1"], 0),
            _q("Middle sound in <em>pen</em>?", ["/e/", "/p/", "/n/", "/pen/"], 0),
            _q("Which word rhymes with <em>cat</em>?", ["hat", "cup", "dog", "can"], 0),
            _q("Blend /m/ /a/ /t/ to make:", ["mat", "tam", "amt", "atm"], 0),
            _q("Last letter in <em>big</em>?", ["g", "b", "i", "big"], 0),
            _q("Vowel in <em>dog</em>?", ["o", "d", "g", "none"], 0),
        ],
    },
    2: {
        "teach": [
            ("What is a rhyme?", "Words <strong>rhyme</strong> when their <strong>ending sounds</strong> match: cat/hat, log/dog, pen/hen."),
            ("Listen to the ending", "Say both words aloud. Clap on the part that sounds the same: cat-<strong>HAT</strong>."),
            ("Word families", "Rhyming words often share letters at the end: -at (cat, hat, mat), -en (pen, hen, ten)."),
            ("Rhyme in poems", "Poems and songs use rhymes so lines sound musical and are easier to remember."),
        ],
        "pills": ["Same ending", "Word families", "Listen & match", "Rhyme pairs"],
        "showcase": [
            ("cat ↔ hat", "-at family", "green"),
            ("log ↔ dog", "-og family", "green"),
            ("pen ↔ hen", "-en family", "amber"),
            ("sun ↔ fun", "-un family", "amber"),
            ("ball ↔ tall", "-all family", "navy"),
            ("night ↔ light", "-ight family", "navy"),
        ],
        "worked": [
            ("Find a rhyme for <em>cat</em>", [
                "Say <strong>cat</strong> and listen: …at",
                "Try <strong>hat</strong> — ending sounds match!",
                "Not <strong>cup</strong> — different ending",
            ]),
            ("Find a rhyme for <em>tree</em>", [
                "Ending of tree is …ee",
                "<strong>bee</strong> rhymes with tree",
                "<strong>dog</strong> does not rhyme",
            ]),
        ],
        "reading": "The <em>hen</em> sat on her <em>pen</em>. A <em>fun</em> day in the <em>sun</em>. The children sang a song about a <em>hat</em> and a <em>cat</em>. Circle the rhyming pairs!",
        "try_it": [
            ("Rhyme for <strong>log</strong>?", "dog (or fog)"),
            ("Do <em>cat</em> and <em>cup</em> rhyme?", "No — different endings"),
            ("Rhyme for <strong>ball</strong>?", "tall, call, fall"),
            ("Same family as <em>hen</em>?", "pen, ten, den"),
        ],
        "quiz": [
            _q("Which rhymes with <em>log</em>?", ["dog", "leg", "lap", "loge"], 0),
            _q("Which pair rhymes?", ["sun–fun", "cat–cup", "pen–pig", "big–bag"], 0),
            _q("Rhyme for <em>hat</em>?", ["mat", "hot", "hit", "hut"], 0),
            _q("Rhyme for <em>night</em>?", ["light", "net", "note", "knight only — light works"], 0),
            _q("Words in -at family?", ["cat", "dog", "sun", "pen"], 0),
            _q("<em>tree</em> rhymes with:", ["bee", "try", "three", "trek"], 0),
            _q("Do <em>hen</em> and <em>pen</em> rhyme?", ["Yes", "No", "Sometimes", "Never"], 0),
            _q("Rhyme for <em>play</em>?", ["day", "plow", "plea", "plate"], 0),
        ],
    },
    3: {
        "teach": [
            ("Use <strong>a</strong>", "Before words that start with a <strong>consonant sound</strong>: a ball, a book, a cricket bat, a university (sounds like 'yoo')."),
            ("Use <strong>an</strong>", "Before words that start with a <strong>vowel sound</strong>: an apple, an egg, an hour (silent h)."),
            ("Use <strong>the</strong>", "When we mean one special thing both people know: the sun, the teacher, the door we already talked about."),
            ("No article?", "We skip articles with names: <em>Ali</em> (not a Ali), and many plurals in general statements."),
        ],
        "pills": ["a / an / the", "Drag to bins", "Vowel sound test", "Special nouns"],
        "showcase": [
            ("a cat", "consonant /k/", "green"),
            ("an owl", "vowel /o/", "green"),
            ("the moon", "one special moon", "amber"),
            ("a book", "one of many books", "amber"),
            ("an egg", "vowel sound", "navy"),
            ("the teacher", "our teacher", "navy"),
        ],
        "worked": [
            ("Choose for <em>apple</em>", [
                "Say 'apple' — first sound is /a/ (vowel)",
                "Use <strong>an</strong> → an apple",
            ]),
            ("Choose for <em>book</em>", [
                "First sound /b/ — consonant",
                "Use <strong>a</strong> → a book",
            ]),
        ],
        "reading": "Sara ate <em>an apple</em> before <em>a cricket</em> match. <em>The sun</em> was bright. She gave <em>the ball</em> to her friend. Find a, an, and the!",
        "try_it": [
            ("___ umbrella", "an"),
            ("___ dog", "a"),
            ("___ sky (we all know it)", "the"),
            ("___ hour (sounds like 'our')", "an"),
        ],
        "quiz": [
            _q("___ apple", ["a", "an", "the", "some"], 1),
            _q("___ book on my desk (specific)", ["A", "An", "The", "Many"], 2),
            _q("I saw ___ elephant.", ["a", "an", "the", "no article"], 1),
            _q("___ university (sounds like 'yoo')", ["a", "an", "the", "an university"], 0),
            _q("___ orange", ["a", "an", "the", "oranges"], 1),
            _q("Look at ___ moon tonight.", ["a", "an", "the", "some"], 2),
            _q("She is ___ doctor.", ["a", "an", "the", "doctor"], 0),
            _q("___ honest man (silent h)", ["a", "an", "the", "honest"], 1),
        ],
    },
    4: {
        "teach": [
            ("Subject first", "The <strong>subject</strong> tells who or what: <em>Ali</em>, <em>The cat</em>, <em>We</em>, <em>My sister</em>."),
            ("Verb next", "The <strong>verb</strong> tells the action or state: <em>plays</em>, <em>runs</em>, <em>is</em>, <em>ate</em>."),
            ("Object last", "The <strong>object</strong> receives the action: <em>cricket</em>, <em>homework</em>, <em>the ball</em>."),
            ("Questions for order", "Ask: <strong>Who?</strong> <strong>Did what?</strong> <strong>To what?</strong> — that is usually SVO in English."),
        ],
        "pills": ["Subject", "Verb", "Object", "Train order"],
        "showcase": [
            ("Ali / plays / cricket.", "S → V → O", "green"),
            ("We / eat / lunch.", "S → V → O", "green"),
            ("The bird / sings.", "S → V", "amber"),
            ("I / read / books.", "S → V → O", "amber"),
            ("They / went / home.", "S → V → O", "navy"),
            ("She / likes / mangoes.", "S → V → O", "navy"),
        ],
        "worked": [
            ("Order: plays / Sara / tennis", [
                "Who? <strong>Sara</strong> (subject)",
                "Did what? <strong>plays</strong> (verb)",
                "What? <strong>tennis</strong> (object)",
                "→ Sara plays tennis.",
            ]),
        ],
        "reading": "<em>My brother</em> <em>kicks</em> <em>the ball</em>. <em>We</em> <em>watch</em> <em>the match</em>. <em>The team</em> <em>scores</em> <em>a goal</em>. Label subject, verb, and object!",
        "try_it": [
            ("Subject in 'Dogs bark.'?", "Dogs"),
            ("Verb in 'I sleep.'?", "sleep"),
            ("Correct order?", "The cat drinks milk."),
            ("Object in 'We love cricket.'?", "cricket"),
        ],
        "quiz": [
            _q("Correct sentence order?", ["Sara reads books.", "Reads Sara books.", "Books Sara reads.", "Sara books reads."], 0),
            _q("Subject in 'The dog barks.'?", ["The dog", "barks", "The", "dog barks"], 0),
            _q("Verb in 'We eat lunch.'?", ["We", "eat", "lunch", "eat lunch"], 1),
            _q("Object in 'Ali kicked the ball.'?", ["Ali", "kicked", "the ball", "the"], 2),
            _q("Who did what in 'Birds fly.'?", ["Birds = subject, fly = verb", "fly = subject", "Birds = object", "No verb"], 0),
            _q("Best order: homework / finished / I", ["I finished homework.", "Finished I homework.", "Homework I finished.", "I homework finished."], 0),
            _q("Subject in 'They are happy.'?", ["They", "are", "happy", "They are"], 0),
            _q("Verb in 'She writes a letter.'?", ["writes", "She", "letter", "a letter"], 0),
        ],
    },
    5: {
        "teach": [
            ("Full stop <strong>.</strong>", "Use for <strong>statements</strong> — telling facts: The sky is blue. I like mangoes."),
            ("Question mark <strong>?</strong>", "Use when asking: Where is my bag? Are you ready?"),
            ("Exclamation <strong>!</strong>", "Use for strong feeling or surprise: What a goal! Watch out!"),
            ("Don't mix them", "A question usually needs <strong>?</strong> even if you are excited: Are we late? (not Are we late!)"),
        ],
        "pills": [". ? !", "Statement vs question", "Pop correct", "Read aloud"],
        "showcase": [
            ("She runs fast.", "statement → .", "green"),
            ("Are you ready?", "question → ?", "green"),
            ("What a match!", "feeling → !", "amber"),
            ("We went home.", "statement → .", "amber"),
            ("Where is Ali?", "question → ?", "navy"),
            ("Stop!", "command → !", "navy"),
        ],
        "worked": [
            ("Punctuate: The cat sat on the mat", [
                "Is it asking something? No → not ?",
                "Strong surprise? No → not !",
                "Statement → <strong>The cat sat on the mat.</strong>",
            ]),
        ],
        "reading": "It was a sunny day. Where did my friends go? They were at the park! We played cricket. Did you see the six? What a shot!",
        "try_it": [
            ("End mark for 'What time is it'", "?"),
            ("'Close the door' needs", "."),
            ("'Wow we won' needs", "!"),
            ("'Is this your bag' needs", "?"),
        ],
        "quiz": [
            _q("End mark for 'What time is it'", ["?", ".", "!", ","], 0),
            _q("'Close the door.' needs", [".", "?", "!", "nothing"], 0),
            _q("'Wow, what a match!'", ["!", ".", "?", ","], 0),
            _q("'Where are you going'", ["?", ".", "!", "..."], 0),
            _q("Statement punctuation:", [".", "?", "!", "all"], 0),
            _q("'Help me' (shouted) often uses:", ["!", ".", "?", "—"], 0),
            _q("'I have two brothers'", [".", "?", "!", ":"], 0),
            _q("Question word at start → usually:", ["?", ".", "!", "no mark"], 0),
        ],
    },
    6: {
        "teach": [
            ("Nouns name", "People, places, animals, things, ideas: <strong>teacher</strong>, <strong>Karachi</strong>, <strong>cat</strong>, <strong>love</strong>."),
            ("Verbs show action or state", "<strong>run</strong>, <strong>think</strong>, <strong>is</strong>, <strong>were</strong>, <strong>play</strong>."),
            ("Same word, different jobs", "<em>play</em> can be verb (I play) or noun (a play). Look at the sentence!"),
            ("Quick test", "Can you <strong>do</strong> it? → verb. Can you <strong>picture</strong> it? → noun."),
        ],
        "pills": ["Noun lane", "Verb lane", "Fast sort", "Action vs thing"],
        "showcase": [
            ("teacher → noun", "person", "green"),
            ("jump → verb", "action", "green"),
            ("cricket → noun", "sport/thing", "amber"),
            ("swim → verb", "action", "amber"),
            ("happiness → noun", "idea", "navy"),
            ("write → verb", "action", "navy"),
        ],
        "worked": [
            ("Sort <em>school</em>", [
                "Can you go to school? It is a place.",
                "Places are <strong>nouns</strong>.",
            ]),
            ("Sort <em>eat</em>", [
                "Can you eat? It is something you do.",
                "Actions are <strong>verbs</strong>.",
            ]),
        ],
        "reading": "The <em>children</em> <em>run</em> in the <em>park</em>. Their <em>teacher</em> <em>smiles</em>. A <em>dog</em> <em>barks</em> near the <em>gate</em>.",
        "try_it": [
            ("<em>table</em> is a", "noun"),
            ("<em>sing</em> is a", "verb"),
            ("<em>quickly</em> is not noun/verb here — it's an adverb", "adverb (bonus!)"),
            ("<em>book</em> in 'I read a book'?", "noun (thing)"),
        ],
        "quiz": [
            _q("<em>cricket</em> in 'We play cricket' is a", ["noun (game)", "verb", "adjective", "article"], 0),
            _q("Action word?", ["swim", "table", "green", "Ali"], 0),
            _q("Person noun?", ["doctor", "quickly", "happy", "run"], 0),
            _q("<em>think</em> is a", ["verb", "noun", "both always", "neither"], 0),
            _q("Place noun?", ["school", "jump", "bright", "ate"], 0),
            _q("<em>happiness</em> is a", ["noun (idea)", "verb", "adjective", "pronoun"], 0),
            _q("Which is a verb?", ["write", "writer", "writing (noun)", "written (adj)"], 0),
            _q("<em>bird</em> is a", ["noun", "verb", "article", "sound"], 0),
        ],
    },
    7: {
        "teach": [
            ("Adjectives describe nouns", "They tell <strong>what kind</strong>, <strong>which one</strong>, or <strong>how many</strong>: red kite, three books, fluffy cloud."),
            ("Colours and sizes", "blue sky, tiny ant, huge stadium — these are adjectives."),
            ("Order of adjectives", "We often say size before colour: a <em>big red</em> ball."),
            ("More than one", "You can use two adjectives: cold, windy day."),
        ],
        "pills": ["Describe", "Paint scene", "Colours & size", "SVG layers"],
        "showcase": [
            ("red kite", "colour", "green"),
            ("three goats", "number", "green"),
            ("cold wind", "feel", "amber"),
            ("tall tree", "size", "amber"),
            ("fluffy cloud", "texture", "navy"),
            ("bright sun", "quality", "navy"),
        ],
        "worked": [
            ("Describe the sky", [
                "Pick colour: <strong>blue</strong>",
                "Pick brightness: <strong>bright</strong>",
                "→ bright blue sky",
            ]),
        ],
        "reading": "On a <em>clear</em> morning, a <em>small</em> <em>brown</em> bird sat on a <em>green</em> branch. The <em>warm</em> <em>golden</em> sun rose slowly.",
        "try_it": [
            ("Adjective in 'blue sky'?", "blue"),
            ("Describes size?", "tiny"),
            ("'Three chairs' — adjective?", "Three"),
            ("Two adjectives:", "big red ball"),
        ],
        "quiz": [
            _q("Adjective in 'blue sky'?", ["blue", "sky", "the", "in"], 0),
            _q("Describes size?", ["tiny", "jump", "park", "run"], 0),
            _q("'Three goats' — adjective?", ["Three", "goats", "ate", "the"], 0),
            _q("Which is an adjective?", ["happy", "happily", "happiness", "happen"], 0),
            _q("Colour word?", ["green", "grass", "grow", "grape"], 0),
            _q("'The old wooden door' has ___ adjectives.", ["2", "1", "3", "0"], 0),
            _q("Adjective describes a:", ["noun", "verb only", "article", "punctuation"], 0),
            _q("'Fluffy' describes:", ["texture/look", "action", "place", "time"], 0),
        ],
    },
    8: {
        "teach": [
            ("Plurals often add -s", "one cat → two <strong>cats</strong>, one book → many <strong>books</strong>."),
            ("Possessive with 's", "<strong>Sara's bag</strong> = the bag belongs to Sara (one Sara)."),
            ("Plural possessive", "<strong>the boys' room</strong> = the room for many boys."),
            ("Common mistakes", "The dogs bowl ❌ → The <strong>dog's</strong> bowl ✓ (one dog)"),
        ],
        "pills": ["Spot the error", "Plural vs 's", "Click wrong word", "Detective"],
        "showcase": [
            ("one cat → cats", "plural -s", "green"),
            ("girl's hat", "one owner", "green"),
            ("boys' team", "many owners", "amber"),
            ("dog's bowl", "one dog", "amber"),
            ("teachers' staffroom", "many teachers", "navy"),
            ("the cat's tail", "belongs to cat", "navy"),
        ],
        "worked": [
            ("Fix: the dogs bone", [
                "One dog or many? One dog's bone",
                "→ the <strong>dog's</strong> bone",
            ]),
        ],
        "reading": "The <em>girls'</em> classroom was tidy. <em>Ahmad's</em> pencil was sharp. The <em>cats</em> slept. One <em>cat's</em> tail twitched. Find plural and possessive forms!",
        "try_it": [
            ("Many dogs → ___ bowls", "dogs'"),
            ("One girl → ___ dress", "girl's"),
            ("Plural of box?", "boxes"),
            ("The ___ tail (one lion)", "lion's"),
        ],
        "quiz": [
            _q("Correct?", ["The girls' team", "The girl's team (many girls)", "The girls team"], 0),
            _q("One boy, his kite:", ["boy's kite", "boys kite", "boy kite", "boys' kite"], 0),
            _q("Two cats, one bowl:", ["cats' bowl", "cat's bowl", "cats bowl", "cat bowl"], 0),
            _q("Plural of child?", ["children", "childs", "childes", "child"], 0),
            _q("The teacher ___ desk", ["'s", "s", "s'", "no apostrophe"], 0),
            _q("Many books → the ___", ["books'", "book's", "books", "book"], 0),
            _q("Possessive shows:", ["ownership", "plural only", "past tense", "question"], 0),
            _q("Fix: the students bags", ["students' bags", "student's bags always", "students bags OK"], 0),
        ],
    },
    9: {
        "teach": [
            ("Regular past: add -ed", "walk → walked, play → played, help → helped."),
            ("Spelling rules", "hike → hiked, dance → danced, stop → stopped (double p)."),
            ("Time words", "Use with yesterday, last week, ago: <em>Yesterday I played cricket.</em>"),
            ("Present vs past", "Today I <strong>play</strong>. Yesterday I <strong>played</strong>."),
        ],
        "pills": ["Time Machine", "Slider -ed", "Yesterday", "Regular verbs"],
        "showcase": [
            ("play → played", "regular", "green"),
            ("walk → walked", "regular", "green"),
            ("jump → jumped", "regular", "amber"),
            ("help → helped", "regular", "amber"),
            ("watch → watched", "regular", "navy"),
            ("clean → cleaned", "regular", "navy"),
        ],
        "worked": [
            ("Past of <em>jump</em>", [
                "Regular verb → add -ed",
                "<strong>jumped</strong>",
            ]),
        ],
        "reading": "Last Saturday we <em>played</em> cricket. Ali <em>bowled</em> fast. We <em>cheered</em> loudly. The sun <em>shined</em> — oops! <em>shone</em> is irregular; we <em>enjoyed</em> the day.",
        "try_it": [
            ("Past of <em>walk</em>?", "walked"),
            ("Yesterday I ___ (play)", "played"),
            ("Past of <em>help</em>?", "helped"),
            ("Today / yesterday: play →", "played"),
        ],
        "quiz": [
            _q("Past of <em>jump</em>?", ["jumped", "jumping", "jumps", "jump"], 0),
            _q("Past of <em>help</em>?", ["helped", "help", "helps", "helping"], 0),
            _q("Yesterday we ___ (walk).", ["walked", "walks", "walking", "walk"], 0),
            _q("Past of <em>play</em>?", ["played", "plaid", "playing", "plays"], 0),
            _q("Past of <em>watch</em>?", ["watched", "watch", "watching", "watches"], 0),
            _q("She ___ yesterday. (clean)", ["cleaned", "cleans", "clean", "cleaning"], 0),
            _q("Regular past usually adds:", ["-ed", "-ing", "-s", "-er"], 0),
            _q("Last week I ___ cricket. (play)", ["played", "play", "playing", "plays"], 0),
        ],
    },
    10: {
        "teach": [
            ("<strong>and</strong> joins", "Adds similar ideas: I ate lunch <strong>and</strong> played cricket."),
            ("<strong>but</strong> contrasts", "Shows difference: It rained, <strong>but</strong> we played indoors."),
            ("<strong>because</strong> explains why", "We stayed home <strong>because</strong> it was hot."),
            ("Comma tip", "Long sentences often use a comma before <strong>but</strong> and <strong>because</strong>."),
        ],
        "pills": ["and / but / because", "Comic panels", "Drag connector", "Story flow"],
        "showcase": [
            ("and", "add ideas", "green"),
            ("but", "contrast", "green"),
            ("because", "reason", "amber"),
            ("so", "result (bonus)", "amber"),
            ("and then", "sequence", "navy"),
            ("but still", "contrast", "navy"),
        ],
        "worked": [
            ("Pick connector: I was tired ___ I slept.", [
                "Reason → <strong>because</strong> or result → so",
                "Best: <strong>so</strong> I slept / <strong>because</strong> I was tired",
            ]),
        ],
        "reading": "We wanted to play outside, <em>but</em> it rained. We stayed in <em>and</em> read books. We were happy <em>because</em> we were together.",
        "try_it": [
            ("Reason word?", "because"),
            ("Contrast word?", "but"),
            ("Join similar ideas?", "and"),
            ("I studied ___ I passed.", "and / so"),
        ],
        "quiz": [
            _q("Reason connector?", ["because", "and", "but", "the"], 0),
            _q("Contrast?", ["but", "and", "because", "or"], 0),
            _q("I was tired ___ I slept.", ["so / because", "and", "the", "but"], 0),
            _q("Adds similar ideas?", ["and", "but", "because", "if"], 0),
            _q("It was cold ___ we wore coats.", ["so / because", "but", "and", "the"], 0),
            _q("She tried ___ she failed.", ["but", "and", "because", "so"], 0),
            _q("We left early ___ the bus was late.", ["because", "and", "but", "if"], 0),
            _q("Connector for 'also'?", ["and", "but", "because", "nor"], 0),
        ],
    },
    11: {
        "teach": [
            ("Speak clearly", "Short phrases work best. Face the mic. Not too fast!"),
            ("Listen first", "Hear the whole phrase, then echo it back."),
            ("Polite phrases", "Please … Thank you … Excuse me … Good morning …"),
            ("Tap fallback", "If speech does not work, tap each word in order."),
        ],
        "pills": ["Speak & listen", "Web Speech", "Tap fallback", "Clear phrases"],
        "showcase": [
            ("Good morning.", "greeting", "green"),
            ("Please help me.", "polite", "green"),
            ("Thank you very much.", "thanks", "amber"),
            ("Where is the library?", "question", "amber"),
            ("I love cricket!", "excited", "navy"),
            ("Excuse me.", "polite", "navy"),
        ],
        "worked": [
            ("Say: Please open the door.", [
                "Listen to each word",
                "Speak clearly: Please — open — the — door",
            ]),
        ],
        "reading": "At school we greet teachers. We ask questions politely. We thank friends. Good speakers listen before they speak.",
        "try_it": [
            ("Polite request?", "Please open the window."),
            ("Greeting?", "Good morning, teacher."),
            ("Thanks?", "Thank you very much."),
            ("Question?", "Where is the canteen?"),
        ],
        "quiz": [
            _q("Polite phrase?", ["Please help me.", "Help me now!", "Me help.", "Help!"], 0),
            _q("Question?", ["Where is the library?", "The library.", "Library there.", "Library?"], 0),
            _q("Complete: 'Thank you ___'", ["very much", "very", "much very", "thank"], 0),
            _q("Morning greeting?", ["Good morning.", "Good night.", "Good cricket.", "Morning good."], 0),
            _q("Excuse me is:", ["polite", "rude", "a verb", "past tense"], 0),
            _q("Listen then ___", ["speak/echo", "run", "write", "sleep"], 0),
            _q("Clear speech is:", ["slow and loud enough", "very fast", "whisper only", "optional"], 0),
            _q("'Could I have water?' is:", ["polite request", "exclamation", "noun", "rhyme"], 0),
        ],
    },
    12: {
        "teach": [
            ("Plan four sentences", "1) Setting 2) Event 3) Problem or action 4) Ending."),
            ("Capital letters", "Start every sentence with a capital. Names too: Ali, Karachi."),
            ("End marks", "Every sentence needs . or ? or !"),
            ("Edit like a boss", "Check articles, tense, plurals, and punctuation together."),
        ],
        "pills": ["Build story", "Fix errors", "Boss edit", "Four sentences"],
        "showcase": [
            ("Sentence 1: setting", "On Saturday we went to the park.", "green"),
            ("Sentence 2: action", "We played cricket.", "green"),
            ("Sentence 3: detail", "Ali scored a six.", "amber"),
            ("Sentence 4: ending", "We walked home happily.", "amber"),
            ("Capital fix", "The cat sat.", "navy"),
            ("Tense fix", "We played.", "navy"),
        ],
        "worked": [
            ("Edit: the cat sat on a mat", [
                "Capital T → <strong>The</strong> cat sat on a mat.",
                "End mark → …mat<strong>.</strong>",
            ]),
        ],
        "reading": "Stories need a beginning, middle, and end. Good writers read twice: once for fun, once to fix mistakes. Your Play Lab builds and edits a mini story!",
        "try_it": [
            ("Capital fix?", "The dog ran."),
            ("Past tense: We ___ home.", "walked"),
            ("End mark for 'What a day'", "!"),
            ("Story order: setting → action → ending", "yes"),
        ],
        "quiz": [
            _q("Needs capital fix?", ["the cat sat.", "The cat sat.", "the Cat sat.", "THE cat sat."], 1),
            _q("Best ending for 'What a day'", ["!", ".", "?", ","], 0),
            _q("Past tense fix:", ["We played.", "We play.", "We playing.", "We plays."], 0),
            _q("Every sentence needs:", ["an end mark", "only nouns", "no verbs", "rhyme"], 0),
            _q("First sentence often:", ["introduces setting", "ends story", "has no verb", "uses ! only"], 0),
            _q("Edit means:", ["find and fix mistakes", "delete everything", "only draw", "add rhyme"], 0),
            _q("'ali went home' fix:", ["Ali went home.", "ali Went home", "Ali went home", "both first and cap"], 0),
            _q("Four-sentence story has:", ["beginning, middle, end parts", "one word", "no punctuation", "only questions"], 0),
        ],
    },
}


def merge_into_level(base: dict) -> dict:
    """Merge rich content into a base level dict from build_all LEVELS."""
    n = base["num"]
    rich = RICH.get(n, {})
    out = dict(base)
    if rich.get("teach"):
        out["teach"] = rich["teach"]
    if rich.get("quiz"):
        out["quiz"] = rich["quiz"]
    for key in ("showcase", "worked", "reading", "try_it", "pills"):
        if rich.get(key):
            out[key] = rich[key]
    return out
