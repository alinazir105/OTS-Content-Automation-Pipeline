# -*- coding: utf-8 -*-
"""Generate English Language skill course: standalone levels 01–12."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
OUT = ROOT / "output" / "Skill Based" / "english-language"
ASSETS_SRC = TOOLS / "assets"

FONTS = (
    '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800'
    '&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">'
)
SCRIPTS = """<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.29/dist/lenis.min.js"></script>"""


def read_theme() -> str:
    theme = (TOOLS / "shared-theme.css").read_text(encoding="utf-8")
    extra = (TOOLS / "content_styles.css").read_text(encoding="utf-8")
    return theme + "\n" + extra


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def stars_html(n: int) -> str:
    return "★" * n + "☆" * (3 - n)


# ─── Level metadata & content ───────────────────────────────────────────────

LEVELS: list[dict] = [
    {
        "num": 1,
        "title": "Letters & Sounds",
        "game": "Letter Pop",
        "skill": "CVC words",
        "difficulty": 1,
        "objective": "Hear and pop letter bubbles in order to build simple CVC words like cat, dog, and sun.",
        "teach": [
            ("What is a CVC word?", "A <strong>CVC</strong> word has a consonant, a vowel, then a consonant: <em>c-a-t</em>, <em>d-o-g</em>, <em>s-u-n</em>."),
            ("Say the sounds", "Stretch each sound: /c/ /a/ /t/ blends into <strong>cat</strong>. Pop bubbles in sound order!"),
        ],
        "examples": [("cat", "c → a → t"), ("dog", "d → o → g"), ("sun", "s → u → n")],
        "vocab": ["CVC", "consonant", "vowel", "blend", "sound", "letter"],
        "tip": "Say each sound aloud before you pop the next bubble.",
        "quiz": [
            ("Which word is CVC?", ["cat", "tree", "play"], 0),
            ("First sound in <em>dog</em>?", ["/d/", "/o/", "/g/"], 0),
            ("How many sounds in <em>sun</em>?", ["3", "2", "4"], 0),
        ],
    },
    {
        "num": 2,
        "title": "Rhyming Words",
        "game": "Rhyme Bridge",
        "skill": "Rhymes",
        "difficulty": 1,
        "objective": "Match words that end with the same sound, like cat and hat.",
        "teach": [
            ("Rhyme means same ending", "Words rhyme when their <strong>ending sounds</strong> match: cat / hat, log / dog."),
            ("Listen to the last part", "Say both words. Do you hear the same chunk at the end?"),
        ],
        "examples": [("cat ↔ hat", "both end in -at"), ("pen ↔ hen", "both end in -en")],
        "vocab": ["rhyme", "ending", "match", "pair", "sound", "word family"],
        "tip": "Clap on the rhyming part: cat-HAT, pen-HEN.",
        "quiz": [
            ("Which rhymes with <em>log</em>?", ["dog", "leg", "lap"], 0),
            ("Which pair rhymes?", ["sun–fun", "cat–cup", "pen–pig"], 0),
            ("Rhyme for <em>hat</em>?", ["mat", "hot", "hit"], 0),
        ],
    },
    {
        "num": 3,
        "title": "Articles a, an, the",
        "game": "Article Toss",
        "skill": "Articles",
        "difficulty": 2,
        "objective": "Choose a, an, or the before nouns in short phrases.",
        "teach": [
            ("Use <strong>a</strong> before consonant sounds", "a ball, a book, a cricket bat"),
            ("Use <strong>an</strong> before vowel sounds", "an apple, an egg, an umbrella"),
            ("Use <strong>the</strong> when we mean one special thing", "the sun, the teacher, the park gate"),
        ],
        "examples": [("a cat", "consonant /k/"), ("an owl", "vowel /o/")],
        "vocab": ["article", "a", "an", "the", "noun", "sound"],
        "tip": "Say the next word aloud — does it start with a vowel sound?",
        "quiz": [
            ("___ apple", ["a", "an", "the"], 1),
            ("___ book on my desk", ["A", "An", "The"], 2),
            ("I saw ___ elephant.", ["a", "an", "the"], 1),
        ],
    },
    {
        "num": 4,
        "title": "Sentence Order",
        "game": "Sentence Train",
        "skill": "Word order",
        "difficulty": 2,
        "objective": "Put words in Subject–Verb–Object order to make clear sentences.",
        "teach": [
            ("Subject first", "Who or what? <em>Ali</em>, <em>The cat</em>, <em>We</em>"),
            ("Verb next", "What happened? <em>plays</em>, <em>runs</em>, <em>ate</em>"),
            ("Object last", "What or whom? <em>cricket</em>, <em>home</em>, <em>rice</em>"),
        ],
        "examples": [("Ali / plays / cricket.", "Subject → Verb → Object"), ("We / went / home.", "SVO order")],
        "vocab": ["subject", "verb", "object", "sentence", "order", "train"],
        "tip": "Ask: Who? Did what? To what?",
        "quiz": [
            ("Correct order?", ["Sara reads books.", "Reads Sara books.", "Books Sara reads."], 0),
            ("Subject in 'The dog barks.'?", ["The dog", "barks", "The"], 0),
            ("Verb in 'We eat lunch.'?", ["We", "eat", "lunch"], 1),
        ],
    },
    {
        "num": 5,
        "title": "End Punctuation",
        "game": "Punctuation Pop",
        "skill": "Punctuation",
        "difficulty": 2,
        "objective": "Pop bubbles that show the correct end mark: full stop, question mark, or exclamation.",
        "teach": [
            ("<strong>.</strong> for statements", "The sky is blue."),
            ("<strong>?</strong> for questions", "Where is my bag?"),
            ("<strong>!</strong> for strong feeling", "What a goal!"),
        ],
        "examples": [("She runs fast.", "statement → ."), ("Are you ready?", "question → ?")],
        "vocab": ["full stop", "question mark", "exclamation", "statement", "sentence", "mark"],
        "tip": "Read aloud — does your voice go up at the end?",
        "quiz": [
            ("End mark for 'What time is it'", ["?", ".", "!"], 0),
            ("'Close the door.' needs", [".", "?", "!"], 0),
            ("'Wow, what a match!'", ["!", ".", "?"], 0),
        ],
    },
    {
        "num": 6,
        "title": "Nouns & Verbs",
        "game": "Noun Verb Sort",
        "skill": "Word types",
        "difficulty": 2,
        "objective": "Sort words quickly into noun lanes (things/people) and verb lanes (actions).",
        "teach": [
            ("Nouns name things", "school, ball, sister, Karachi"),
            ("Verbs show actions", "run, eat, think, play"),
        ],
        "examples": [("teacher → noun", "a person"), ("jump → verb", "an action")],
        "vocab": ["noun", "verb", "action", "thing", "person", "sort"],
        "tip": "Can you picture it? Likely a noun. Can you do it? Likely a verb.",
        "quiz": [
            ("<em>cricket</em> here is a", ["noun (sport)", "verb", "adjective"], 0),
            ("Action word?", ["swim", "table", "green"], 0),
            ("Person noun?", ["doctor", "quickly", "happy"], 0),
        ],
    },
    {
        "num": 7,
        "title": "Adjectives",
        "game": "Paint the Picture",
        "skill": "Describing words",
        "difficulty": 3,
        "objective": "Pick adjectives to paint a scene — bright sky, tall tree, fluffy clouds.",
        "teach": [
            ("Adjectives describe", "They tell <strong>what kind</strong> or <strong>how many</strong>: red kite, three books."),
            ("Order can stack", "a <em>big brown</em> dog — more than one adjective is OK!"),
        ],
        "examples": [("cold wind", "adjective + noun"), ("two mangoes", "number adjective")],
        "vocab": ["adjective", "describe", "colour", "size", "number", "scene"],
        "tip": "Add one adjective at a time and read the whole phrase.",
        "quiz": [
            ("Adjective in 'blue sky'?", ["blue", "sky", "the"], 0),
            ("Describes size?", ["tiny", "jump", "park"], 0),
            ("'Three goats' — adjective?", ["Three", "goats", "ate"], 0),
        ],
    },
    {
        "num": 8,
        "title": "Plurals & 's",
        "game": "Grammar Detective",
        "skill": "Grammar spot",
        "difficulty": 3,
        "objective": "Find the wrong word in a short passage about plurals and possessives.",
        "teach": [
            ("Plurals often add -s", "one cat → two cats"),
            ("Possessive shows ownership", "Sara's bag = the bag belongs to Sara"),
            ("Don't mix them up!", "The dogs bowl ❌ → The dog's bowl ✓"),
        ],
        "examples": [("boys' room", "more than one boy"), ("girl's hat", "one girl")],
        "vocab": ["plural", "possessive", "apostrophe", "ownership", "error", "detective"],
        "tip": "Ask: one owner or many? Singular or plural?",
        "quiz": [
            ("Correct?", ["The girls' team", "The girl's team (many girls)", "The girls team"], 0),
            ("One boy, his kite:", ["boy's kite", "boys kite", "boy kite"], 0),
            ("Two cats, one bowl:", ["cats' bowl", "cat's bowl", "cats bowl"], 0),
        ],
    },
    {
        "num": 9,
        "title": "Past Tense",
        "game": "Time Machine",
        "skill": "Regular past",
        "difficulty": 3,
        "objective": "Turn present verbs into regular past tense with -ed on the Time Machine dial.",
        "teach": [
            ("Regular past adds -ed", "walk → walked, play → played"),
            ("Double the consonant sometimes", "stop → stopped (one syllable, one vowel)"),
        ],
        "examples": [("I play → I played", "yesterday"), ("She helps → She helped", "-ed")],
        "vocab": ["past tense", "present", "yesterday", "-ed", "regular", "verb"],
        "tip": "Say 'yesterday I…' — the verb usually needs -ed.",
        "quiz": [
            ("Past of <em>jump</em>?", ["jumped", "jumping", "jumps"], 0),
            ("Past of <em>help</em>?", ["helped", "help", "helps"], 0),
            ("Yesterday we ___ (walk).", ["walked", "walks", "walking"], 0),
        ],
    },
    {
        "num": 10,
        "title": "Connectors",
        "game": "Story Bridge",
        "skill": "and, but, because",
        "difficulty": 3,
        "objective": "Drag connector words to join comic-strip panels into smooth stories.",
        "teach": [
            ("<strong>and</strong> adds", "I ate lunch and played cricket."),
            ("<strong>but</strong> shows contrast", "It rained, but we played indoors."),
            ("<strong>because</strong> gives a reason", "We stayed home because it was hot."),
        ],
        "examples": [("and", "joins similar ideas"), ("because", "explains why")],
        "vocab": ["connector", "and", "but", "because", "clause", "story"],
        "tip": "Read both parts — does it need addition, contrast, or reason?",
        "quiz": [
            ("Reason connector?", ["because", "and", "but"], 0),
            ("Contrast?", ["but", "and", "the"], 0),
            ("I was tired ___ I slept.", ["so/because", "and", "the"], 0),
        ],
    },
    {
        "num": 11,
        "title": "Speaking & Listening",
        "game": "Echo Chamber",
        "skill": "Say & match",
        "difficulty": 3,
        "objective": "Repeat phrases clearly — use your voice or tap the words in order.",
        "teach": [
            ("Speak clearly", "Short phrases are easier: 'Good morning, teacher.'"),
            ("Listen then echo", "Hear the phrase, then say it back the same way."),
        ],
        "examples": [("'Please open the door.'", "polite request"), ("'I love cricket!'", "excited statement")],
        "vocab": ["speak", "listen", "phrase", "clear", "echo", "repeat"],
        "tip": "If the mic does not work, tap each word chip in order.",
        "quiz": [
            ("Polite phrase?", ["Please help me.", "Help me now!", "Me help."], 0),
            ("Question?", ["Where is the library?", "The library.", "Library there."], 0),
            ("Complete: 'Thank you ___'", ["very much", "very", "much very"], 0),
        ],
    },
    {
        "num": 12,
        "title": "Story Editing",
        "game": "Story Architect",
        "skill": "Write & fix",
        "difficulty": 3,
        "objective": "Build a four-sentence story, then fix grammar and punctuation errors like a boss round.",
        "teach": [
            ("Plan four sentences", "Beginning, two middle events, ending."),
            ("Check capitals & stops", "Every sentence starts big and ends with . ? or !"),
            ("Boss edit", "Find wrong articles, tense, and punctuation together."),
        ],
        "examples": [("Sentence 1: setting", "On Saturday we went to the park."), ("Sentence 4: ending", "We walked home happily.")],
        "vocab": ["story", "edit", "capital", "punctuation", "revise", "paragraph"],
        "tip": "Read your whole story aloud once — errors are easier to hear.",
        "quiz": [
            ("Needs capital fix?", ["the cat sat.", "The cat sat.", "the Cat sat."], 1),
            ("Best ending mark for 'What a day'", ["!", ".", "?"], 0),
            ("Past tense fix:", ["We played.", "We play.", "We playing."], 0),
        ],
    },
]


# ─── Per-level game fragments ───────────────────────────────────────────────

def game_css(num: int) -> str:
    games = {
        1: """
.game-area{position:relative;width:min(100%,520px);height:320px;margin:0 auto;background:linear-gradient(180deg,#87CEEB 0%,#e8f4fc 100%);border-radius:var(--border-radius);overflow:hidden;border:3px solid var(--navy)}
.letter-bubble{position:absolute;width:56px;height:56px;border-radius:50%;background:var(--amber);color:#fff;font-family:'Poppins',sans-serif;font-weight:800;font-size:1.4rem;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 6px 16px rgba(0,0,0,.2);user-select:none;transition:transform .15s}
.letter-bubble.popped{pointer-events:none;opacity:0;transform:scale(1.8)}
.word-display{font-family:'Poppins',sans-serif;font-size:2rem;font-weight:800;color:var(--navy);margin-bottom:12px;letter-spacing:.2em}
""",
        2: """
.rhyme-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;max-width:480px;margin:0 auto}
.rhyme-card{background:#fff;border:3px solid #dde4ec;border-radius:var(--border-radius);padding:20px;font-family:'Poppins',sans-serif;font-weight:700;font-size:1.3rem;cursor:pointer;text-align:center;transition:all .2s}
.rhyme-card.selected{border-color:var(--amber);background:var(--light-amber)}
.rhyme-card.matched{border-color:var(--green);background:var(--light-green);opacity:.7;pointer-events:none}
""",
        3: """
.toss-bins{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-bottom:20px}
.toss-bin{flex:1;min-width:100px;max-width:140px;min-height:100px;border:3px dashed var(--navy);border-radius:var(--border-radius);display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:'Poppins',sans-serif;font-weight:800;font-size:1.5rem;background:#fff}
.toss-bin.over{background:var(--light-green);border-color:var(--green)}
.toss-words{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:16px}
.toss-word{background:var(--navy);color:#fff;padding:12px 18px;border-radius:999px;cursor:grab;font-weight:700;font-family:'Poppins',sans-serif;touch-action:none}
""",
        4: """
.train-track{background:linear-gradient(90deg,#8B7355,#6B5344);height:8px;border-radius:4px;margin:24px 0;position:relative}
.train-carriages{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;min-height:80px}
.train-car{background:var(--amber);color:#fff;padding:14px 20px;border-radius:10px 10px 4px 4px;font-family:'Poppins',sans-serif;font-weight:700;cursor:grab;border:2px solid #d17a1a;touch-action:none}
.train-car.correct-slot{box-shadow:0 0 0 3px var(--green)}
""",
        5: """
#punctCanvas{display:block;margin:0 auto;border-radius:var(--border-radius);background:#1a2b3c;cursor:pointer;max-width:100%}
""",
        6: """
.sort-lanes{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:560px;margin:0 auto}
.sort-lane{min-height:200px;border-radius:var(--border-radius);padding:12px;border:3px dashed}
.sort-lane.nouns{border-color:var(--green);background:var(--light-green)}
.sort-lane.verbs{border-color:var(--amber);background:var(--light-amber)}
.sort-lane h4{text-align:center;font-family:'Poppins',sans-serif;margin-bottom:8px}
.sort-tile{background:#fff;border:2px solid var(--navy);border-radius:10px;padding:14px;margin:8px;font-family:'Poppins',sans-serif;font-weight:700;font-size:1.1rem;cursor:pointer;text-align:center}
.sort-tile.sorted{opacity:.5;pointer-events:none}
.sort-pool{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:16px}
""",
        7: """
.paint-scene{width:min(100%,400px);height:280px;margin:0 auto;position:relative;background:#87CEEB;border-radius:var(--border-radius);overflow:hidden}
.paint-layer{position:absolute;inset:0;opacity:0;transition:opacity .4s;pointer-events:none}
.paint-layer.visible{opacity:1}
.paint-adjs{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:16px}
.paint-adj{background:#fff;border:2px solid var(--green);padding:10px 16px;border-radius:999px;cursor:pointer;font-weight:600;font-family:'Poppins',sans-serif}
.paint-adj.used{background:var(--light-green);opacity:.6}
""",
        8: """
.detective-passage{background:#fff;padding:24px;border-radius:var(--border-radius);font-size:1.15rem;line-height:2;max-width:560px;margin:0 auto}
.detective-passage .w{cursor:pointer;padding:2px 4px;border-radius:4px;transition:background .2s}
.detective-passage .w:hover{background:var(--light-amber)}
.detective-passage .w.wrong-hit{background:#ffe0e0;animation:shake .4s}
.detective-passage .w.correct-hit{background:var(--light-green)}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}
""",
        9: """
.time-dial-wrap{text-align:center;max-width:400px;margin:0 auto}
.time-verb{font-family:'Poppins',sans-serif;font-size:2.5rem;font-weight:800;color:var(--navy);margin:16px 0}
.time-slider{width:100%;height:12px;accent-color:var(--amber);margin:20px 0}
.time-labels{display:flex;justify-content:space-between;font-weight:600;color:#666}
""",
        10: """
.comic-strip{display:flex;flex-direction:column;gap:16px;max-width:480px;margin:0 auto}
.comic-panel{background:#fff;border:3px solid var(--navy);border-radius:var(--border-radius);padding:16px;min-height:70px}
.comic-slot{border:2px dashed var(--amber);min-height:36px;border-radius:8px;padding:8px;margin-top:8px;display:flex;align-items:center;justify-content:center;color:#888;font-size:.9rem}
.comic-slot.filled{border-style:solid;border-color:var(--green);color:var(--navy);font-weight:700}
.connector-bank{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:16px}
.connector-chip{background:var(--navy);color:#fff;padding:10px 18px;border-radius:999px;cursor:grab;font-weight:700;font-family:'Poppins',sans-serif}
""",
        11: """
.echo-phrase{font-family:'Poppins',sans-serif;font-size:1.5rem;font-weight:700;text-align:center;margin:16px 0;color:var(--navy)}
.echo-chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:16px 0}
.echo-chip{background:#fff;border:2px solid var(--green);padding:12px 16px;border-radius:10px;cursor:pointer;font-weight:600}
.echo-chip.tapped{background:var(--light-green)}
.echo-mic{background:var(--amber);color:#fff;border:none;width:80px;height:80px;border-radius:50%;font-size:2rem;cursor:pointer;margin:16px auto;display:block}
.echo-status{text-align:center;font-weight:600;min-height:1.5em}
""",
        12: """
.architect-steps{display:flex;gap:8px;justify-content:center;margin-bottom:20px;flex-wrap:wrap}
.arch-step{padding:8px 14px;border-radius:999px;background:#eee;font-weight:700;font-size:.85rem;font-family:'Poppins',sans-serif}
.arch-step.active{background:var(--amber);color:#fff}
.arch-step.done{background:var(--green);color:#fff}
.arch-panel{max-width:520px;margin:0 auto;background:#fff;padding:20px;border-radius:var(--border-radius);box-shadow:var(--shadow)}
.arch-input{width:100%;padding:12px;border:2px solid #dde4ec;border-radius:10px;font-size:1rem;margin:8px 0;font-family:'Inter',sans-serif}
.arch-error{background:#fff5f5;border-left:4px solid #e74c3c;padding:12px;margin:8px 0;border-radius:0 8px 8px 0;cursor:pointer}
.arch-error.fixed{opacity:.5;text-decoration:line-through}
""",
    }
    return games.get(num, "")



def game_html(num: int) -> str:
    g = {
        1: '<div class="word-display" id="gameWord">_ _ _</div><div class="game-area" id="gameArea" aria-live="polite"></div>',
        2: '<div class="rhyme-grid" id="rhymeGrid"></div>',
        3: '<div class="toss-bins"><div class="toss-bin" data-bin="a">a</div><div class="toss-bin" data-bin="an">an</div><div class="toss-bin" data-bin="the">the</div></div><div class="toss-words" id="tossWords"></div>',
        4: '<p id="trainPrompt" style="text-align:center;font-weight:600"></p><div class="train-track"></div><div class="train-carriages" id="trainCars"></div>',
        5: '<canvas id="punctCanvas" width="560" height="300" aria-label="Pop correct sentences"></canvas>',
        6: '<div class="sort-lanes"><div class="sort-lane nouns" data-lane="noun"><h4>Nouns</h4></div><div class="sort-lane verbs" data-lane="verb"><h4>Verbs</h4></div></div><div class="sort-pool" id="sortPool"></div>',
        7: '<div class="paint-scene" id="paintScene"><svg class="paint-layer" id="layerSky" viewBox="0 0 400 280"><rect width="400" height="280" fill="#87CEEB"/></svg><svg class="paint-layer" id="layerSun" viewBox="0 0 400 280"><circle cx="320" cy="60" r="40" fill="#F0932B"/></svg><svg class="paint-layer" id="layerTree" viewBox="0 0 400 280"><rect x="60" y="120" width="30" height="120" fill="#5D4037"/><ellipse cx="75" cy="110" rx="55" ry="50" fill="#2E7D32"/></svg><svg class="paint-layer" id="layerCloud" viewBox="0 0 400 280"><ellipse cx="200" cy="80" rx="50" ry="28" fill="#fff"/></svg></div><div class="paint-adjs" id="paintAdjs"></div>',
        8: '<div class="detective-passage" id="detectivePassage"></div>',
        9: '<div class="time-dial-wrap"><div class="time-labels"><span>Present</span><span>Past</span></div><input type="range" class="time-slider" id="timeSlider" min="0" max="100" value="0"><div class="time-verb" id="timeVerb">play</div><button type="button" id="timeCheck" class="playlab-launch" style="margin-top:8px">Lock in!</button></div>',
        10: '<div class="comic-strip" id="comicStrip"></div><div class="connector-bank" id="connectorBank"></div>',
        11: '<div class="echo-phrase" id="echoPhrase"></div><button type="button" class="echo-mic" id="echoMic" aria-label="Speak">🎤</button><div class="echo-status" id="echoStatus" aria-live="polite"></div><div class="echo-chips" id="echoChips"></div>',
        12: '<div class="architect-steps" id="archSteps"></div><div class="arch-panel" id="archPanel"></div>',
    }
    return g.get(num, "<p>Play!</p>").replace("<div", "<div").replace("</div>", "</div>")


def game_js(num: int) -> str:
    scripts = {
        1: r"""
var G={words:[{w:'cat',letters:['c','a','t']},{w:'dog',letters:['d','o','g']},{w:'sun',letters:['s','u','n']}],wi:0,li:0,score:0};
function spawnBubbles(){
  var area=document.getElementById('gameArea'); if(!area)return;
  area.innerHTML='';
  var wd=G.words[G.wi]; var letters=wd.letters.slice().sort(function(){return Math.random()-.5;});
  letters.forEach(function(ch,i){
    var b=document.createElement('button'); b.type='button'; b.className='letter-bubble'; b.textContent=ch;
    b.style.left=(15+Math.random()*70)+'%'; b.style.top=(15+Math.random()*65)+'%';
    b.dataset.letter=ch;
    b.onclick=function(){popLetter(b,ch,wd);};
    area.appendChild(b);
  });
  document.getElementById('gameWord').textContent=wd.letters.map(function(_,i){return i<G.li?wd.letters[i]:'_';}).join(' ');
}
function popLetter(el,ch,wd){
  if(ch!==wd.letters[G.li]){try{gsap.to(el,{x:'+=8',yoyo:true,repeat:3,duration:.08});}catch(e){}return;}
  el.classList.add('popped'); G.li++; G.score+=10;
  document.getElementById('gameWord').textContent=wd.letters.map(function(c,i){return i<G.li?c:'_';}).join(' ');
  document.getElementById('gameScore').textContent=G.score;
  if(G.li>=wd.letters.length){
    setTimeout(function(){
      G.wi++; G.li=0;
      if(G.wi>=G.words.length){endGame(Math.min(3,1+Math.floor(G.score/30)));return;}
      spawnBubbles();
    },600);
  }
}
function initGame(){G.wi=0;G.li=0;G.score=0;document.getElementById('gameScore').textContent='0';spawnBubbles();}
""",
        2: r"""
var G={pairs:[['cat','hat'],['dog','log'],['pen','hen'],['sun','fun']],sel:null,matched:0,score:0};
function initGame(){
  var grid=document.getElementById('rhymeGrid'); if(!grid)return; grid.innerHTML='';
  var words=[]; G.pairs.forEach(function(p){words.push(p[0],p[1]);});
  words.sort(function(){return Math.random()-.5;});
  words.forEach(function(w){
    var c=document.createElement('button'); c.type='button'; c.className='rhyme-card'; c.textContent=w; c.dataset.word=w;
    c.onclick=function(){pickRhyme(c,w);}; grid.appendChild(c);
  });
  G.sel=null;G.matched=0;G.score=0;document.getElementById('gameScore').textContent='0';
}
function pickRhyme(el,w){
  if(el.classList.contains('matched'))return;
  if(!G.sel){G.sel={el:el,w:w};el.classList.add('selected');return;}
  if(G.sel.el===el){el.classList.remove('selected');G.sel=null;return;}
  var ok=G.pairs.some(function(p){return(p[0]===G.sel.w&&p[1]===w)||(p[1]===G.sel.w&&p[0]===w);});
  if(ok){G.sel.el.classList.add('matched');el.classList.add('matched');G.matched++;G.score+=20;document.getElementById('gameScore').textContent=G.score;
    if(G.matched>=G.pairs.length)endGame(3);}else{el.classList.add('selected');setTimeout(function(){G.sel.el.classList.remove('selected');el.classList.remove('selected');G.sel=null;},500);}
  G.sel=null;
}
""",
        3: r"""
var G={items:[{w:'apple',a:'an'},{w:'ball',a:'a'},{w:'egg',a:'an'},{w:'park',a:'the'},{w:'umbrella',a:'an'},{w:'book',a:'a'}],done:0,score:0,drag:null};
function initGame(){
  var pool=document.getElementById('tossWords'); if(!pool)return; pool.innerHTML='';
  G.items.slice().sort(function(){return Math.random()-.5;}).forEach(function(it){
    var d=document.createElement('div'); d.className='toss-word'; d.textContent=it.w; d.dataset.answer=it.a; d.draggable=true;
    d.addEventListener('dragstart',function(e){G.drag=d;e.dataTransfer.setData('text','1');});
    pool.appendChild(d);
  });
  document.querySelectorAll('.toss-bin').forEach(function(bin){
    bin.ondragover=function(e){e.preventDefault();bin.classList.add('over');};
    bin.ondragleave=function(){bin.classList.remove('over');};
    bin.ondrop=function(e){e.preventDefault();bin.classList.remove('over');
      if(!G.drag)return;
      if(G.drag.dataset.answer===bin.dataset.bin){G.score+=15;G.done++;G.drag.remove();document.getElementById('gameScore').textContent=G.score;
        if(G.done>=G.items.length)endGame(3);}else{try{gsap.to(G.drag,{x:10,yoyo:true,repeat:3});}catch(x){}}
      G.drag=null;
    };
  });
  G.done=0;G.score=0;document.getElementById('gameScore').textContent='0';
}
""",
        4: r"""
var G={rounds:[['Ali','plays','cricket.'],['We','went','home.'],['The cat','sits','quietly.']],ri:0,score:0};
function loadTrain(){
  var cars=document.getElementById('trainCars'); var prompt=document.getElementById('trainPrompt');
  if(!cars)return;
  var parts=G.rounds[G.ri].slice().sort(function(){return Math.random()-.5;});
  prompt.textContent='Drag carriages into Subject → Verb → Object order';
  cars.innerHTML='';
  parts.forEach(function(p){
    var c=document.createElement('div'); c.className='train-car'; c.textContent=p; c.draggable=true;
    c.addEventListener('dragstart',function(e){e.dataTransfer.setData('text',p);});
    c.addEventListener('dragover',function(e){e.preventDefault();});
    c.addEventListener('drop',function(e){e.preventDefault();var t=e.dataTransfer.getData('text');if(!t)return;
      var nodes=[].slice.call(cars.children);nodes.sort(function(a,b){return a.offsetLeft-b.offsetLeft;});
      var built=nodes.map(function(n){return n.textContent;});
      if(built.join(' ')==='')built=[];
    });
    cars.appendChild(c);
  });
  cars.ondragover=function(e){e.preventDefault();};
  cars.ondrop=function(e){e.preventDefault();};
  enableTrainReorder();
}
function enableTrainReorder(){
  var cars=document.getElementById('trainCars'); var dragged=null;
  cars.querySelectorAll('.train-car').forEach(function(car){
    car.ondragstart=function(){dragged=car;};
    car.ondragover=function(e){e.preventDefault();};
    car.ondrop=function(e){e.preventDefault();if(!dragged||dragged===car)return;cars.insertBefore(dragged,car);checkTrain();};
  });
  var btn=document.createElement('button'); btn.type='button'; btn.className='playlab-launch'; btn.textContent='Check order';
  btn.style.marginTop='12px'; btn.onclick=checkTrain;
  if(!document.getElementById('trainCheck')){btn.id='trainCheck';cars.parentNode.appendChild(btn);}
}
function checkTrain(){
  var nodes=[].slice.call(document.getElementById('trainCars').children);
  var built=nodes.map(function(n){return n.textContent.replace('.','');});
  var target=G.rounds[G.ri].map(function(s){return s.replace('.','');});
  if(built.join('|')===target.join('|')){G.score+=25;G.ri++;document.getElementById('gameScore').textContent=G.score;
    if(G.ri>=G.rounds.length)endGame(3);else loadTrain();}
}
function initGame(){G.ri=0;G.score=0;document.getElementById('gameScore').textContent='0';loadTrain();}
""",
        5: r"""
var G={bubbles:[],score:0,round:0,sets:[
  [{t:'The dog runs fast.',ok:true},{t:'The dog runs fast',ok:false},{t:'the dog runs fast.',ok:false}],
  [{t:'Where is my bag?',ok:true},{t:'Where is my bag',ok:false},{t:'Where is my bag.',ok:false}],
  [{t:'What a goal!',ok:true},{t:'What a goal',ok:false},{t:'What a goal.',ok:false}]
]};
function initGame(){
  G.round=0;G.score=0;document.getElementById('gameScore').textContent='0';
  nextPunctRound();
}
function nextPunctRound(){
  if(G.round>=G.sets.length){endGame(3);return;}
  var cv=document.getElementById('punctCanvas'); if(!cv)return;
  var ctx=cv.getContext('2d'); G.bubbles=[];
  var set=G.sets[G.round];
  set.forEach(function(s,i){
    G.bubbles.push({x:40+((i*170)%480),y:60+i*70,r:55,text:s.t,ok:s.ok,alive:true});
  });
  drawPunct();
  cv.onclick=function(e){
    var r=cv.getBoundingClientRect(); var x=(e.clientX-r.left)*(cv.width/r.width); var y=(e.clientY-r.top)*(cv.height/r.height);
    G.bubbles.forEach(function(b){
      if(!b.alive)return;
      var dx=x-b.x,dy=y-b.y;
      if(dx*dx+dy*dy<b.r*b.r){
        if(b.ok){b.alive=false;G.score+=20;document.getElementById('gameScore').textContent=G.score;G.round++;setTimeout(nextPunctRound,500);}
        else{try{gsap.to(cv,{x:5,yoyo:true,repeat:3,duration:.06});}catch(z){}}
        drawPunct();
      }
    });
  };
}
function drawPunct(){
  var cv=document.getElementById('punctCanvas'); var ctx=cv.getContext('2d');
  ctx.fillStyle='#1a2b3c'; ctx.fillRect(0,0,cv.width,cv.height);
  G.bubbles.forEach(function(b){
    if(!b.alive)return;
    ctx.beginPath(); ctx.arc(b.x,b.y,b.r,0,Math.PI*2);
    ctx.fillStyle=b.ok?'#6AB04C':'#F0932B'; ctx.fill();
    ctx.fillStyle='#fff'; ctx.font='bold 13px Poppins,sans-serif'; ctx.textAlign='center';
    wrapText(ctx,b.text,b.x,b.y,b.r*1.5);
  });
}
function wrapText(ctx,text,x,y,maxW){
  var words=text.split(' '),line='',lines=[],ly=y-10;
  words.forEach(function(w){var test=line+w+' ';if(ctx.measureText(test).width>maxW&&line){lines.push(line);line=w+' ';}else line=test;});
  lines.push(line);
  lines.forEach(function(ln,i){ctx.fillText(ln.trim(),x,ly+i*16);});
}
""",
        6: r"""
var G={tiles:[{w:'run',t:'verb'},{w:'school',t:'noun'},{w:'eat',t:'verb'},{w:'sister',t:'noun'},{w:'jump',t:'verb'},{w:'ball',t:'noun'}],done:0,score:0};
function initGame(){
  var pool=document.getElementById('sortPool'); if(!pool)return;
  document.querySelectorAll('.sort-lane').forEach(function(l){while(l.children.length>1)l.lastChild.remove();});
  pool.innerHTML=''; G.done=0; G.score=0; document.getElementById('gameScore').textContent='0';
  G.tiles.slice().sort(function(){return Math.random()-.5;}).forEach(function(t){
    var el=document.createElement('button'); el.type='button'; el.className='sort-tile'; el.textContent=t.w;
    el.onclick=function(){sortTile(el,t);}; pool.appendChild(el);
  });
}
function sortTile(el,t){
  var lane=document.querySelector('.sort-lane[data-lane="'+t.t+'"]');
  if(!lane||el.classList.contains('sorted'))return;
  lane.appendChild(el); el.classList.add('sorted'); G.done++; G.score+=15;
  document.getElementById('gameScore').textContent=G.score;
  if(G.done>=G.tiles.length)endGame(3);
}
""",
        7: r"""
var G={map:{bright:'layerSun',tall:'layerTree',fluffy:'layerCloud',blue:'layerSky'},picked:0,score:0,need:['bright','tall','fluffy']};
function initGame(){
  var adj=document.getElementById('paintAdjs'); if(!adj)return;
  adj.innerHTML=''; G.picked=0; G.score=0; document.getElementById('gameScore').textContent='0';
  document.querySelectorAll('.paint-layer').forEach(function(l){l.classList.remove('visible');});
  ['bright','tall','fluffy','blue'].forEach(function(a){
    var b=document.createElement('button'); b.type='button'; b.className='paint-adj'; b.textContent=a;
    b.onclick=function(){paintAdj(b,a);}; adj.appendChild(b);
  });
}
function paintAdj(btn,a){
  if(btn.classList.contains('used'))return;
  var layer=document.getElementById(G.map[a]); if(layer)layer.classList.add('visible');
  btn.classList.add('used'); G.score+=20; document.getElementById('gameScore').textContent=G.score;
  if(G.need.indexOf(a)>=0)G.picked++;
  if(G.picked>=G.need.length)endGame(3);
}
""",
        8: r"""
var G={passage:'At the park the dogs bowl was empty. The boys kite flew high. Sara fed her cats.',wrong:'dogs',score:0};
function initGame(){
  var p=document.getElementById('detectivePassage'); if(!p)return;
  p.innerHTML=''; G.score=0; document.getElementById('gameScore').textContent='0';
  G.passage.split(/(\s+)/).forEach(function(tok){
    if(!tok.trim()){p.appendChild(document.createTextNode(tok));return;}
    var clean=tok.replace(/[.,]/g,'');
    var span=document.createElement('span'); span.className='w'; span.textContent=tok;
    span.onclick=function(){
      if(clean===G.wrong){span.classList.add('correct-hit');G.score=50;document.getElementById('gameScore').textContent=G.score;endGame(3);}
      else{span.classList.add('wrong-hit');setTimeout(function(){span.classList.remove('wrong-hit');},400);}
    };
    p.appendChild(span);
  });
}
""",
        9: r"""
var G={verbs:['play','walk','help','jump'],vi:0,score:0};
function initGame(){
  G.vi=0;G.score=0;document.getElementById('gameScore').textContent='0';
  var sl=document.getElementById('timeSlider'); var v=document.getElementById('timeVerb');
  if(sl){sl.value=0;sl.oninput=function(){v.textContent=G.verbs[G.vi]+(sl.value>50?' → '+G.verbs[G.vi]+'ed':'');};}
  document.getElementById('timeCheck').onclick=checkTime;
  showVerb();
}
function showVerb(){document.getElementById('timeVerb').textContent=G.verbs[G.vi];document.getElementById('timeSlider').value=0;}
function checkTime(){
  var sl=document.getElementById('timeSlider');
  if(sl.value>60){G.score+=20;document.getElementById('gameScore').textContent=G.score;G.vi++;
    if(G.vi>=G.verbs.length)endGame(3);else showVerb();}
}
""",
        10: r"""
var G={panels:[{text:'I was tired',slot:'',ans:'and'},{text:'It rained',slot:'',ans:'but'},{text:'We stayed in',slot:'',ans:'because'}],chips:['and','but','because'],done:0,score:0,drag:null};
function initGame(){
  var strip=document.getElementById('comicStrip'); var bank=document.getElementById('connectorBank');
  if(!strip)return; strip.innerHTML=''; bank.innerHTML=''; G.done=0; G.score=0;
  document.getElementById('gameScore').textContent='0';
  G.panels.forEach(function(p,i){
    var pan=document.createElement('div'); pan.className='comic-panel';
    pan.innerHTML='<div>'+p.text+'</div><div class="comic-slot" data-i="'+i+'">Drop connector</div>';
    strip.appendChild(pan);
  });
  G.chips.forEach(function(c){
    var ch=document.createElement('div'); ch.className='connector-chip'; ch.textContent=c; ch.draggable=true;
    ch.ondragstart=function(){G.drag=ch;};
    bank.appendChild(ch);
  });
  document.querySelectorAll('.comic-slot').forEach(function(slot){
    slot.ondragover=function(e){e.preventDefault();};
    slot.ondrop=function(e){e.preventDefault();if(!G.drag)return;
      var i=+slot.dataset.i; if(G.drag.textContent===G.panels[i].ans){slot.textContent=G.drag.textContent;slot.classList.add('filled');G.done++;G.score+=20;document.getElementById('gameScore').textContent=G.score;if(G.done>=G.panels.length)endGame(3);}
      G.drag=null;
    };
  });
}
""",
        11: r"""
var G={phrase:['Good','morning,','teacher.'],tapIdx:0,score:0,rec:null};
function initGame(){
  G.tapIdx=0;G.score=0;document.getElementById('gameScore').textContent='0';
  document.getElementById('echoPhrase').textContent=G.phrase.join(' ');
  var chips=document.getElementById('echoChips'); chips.innerHTML='';
  G.phrase.forEach(function(w,i){
    var c=document.createElement('button'); c.type='button'; c.className='echo-chip'; c.textContent=w;
    c.onclick=function(){tapEcho(c,i);}; chips.appendChild(c);
  });
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  var mic=document.getElementById('echoMic');
  document.getElementById('echoStatus').textContent=SR?'Tap mic or tap words in order':'Tap each word in order';
  if(SR&&mic){
    G.rec=new SR(); G.rec.lang='en-GB'; G.rec.interimResults=false;
    mic.onclick=function(){
      document.getElementById('echoStatus').textContent='Listening…';
      G.rec.onresult=function(ev){
        var said=(ev.results[0][0].transcript||'').toLowerCase();
        var target=G.phrase.join(' ').toLowerCase().replace(/[^a-z, ]/g,'');
        if(said.indexOf('good')>=0&&said.indexOf('morning')>=0){G.score=50;document.getElementById('gameScore').textContent=G.score;endGame(3);}
        else document.getElementById('echoStatus').textContent='Try again or tap words';
      };
      G.rec.onerror=function(){document.getElementById('echoStatus').textContent='Mic blocked — tap words';};
      try{G.rec.start();}catch(e){document.getElementById('echoStatus').textContent='Tap words below';};
    };
  }
}
function tapEcho(el,i){
  if(i!==G.tapIdx){document.getElementById('echoStatus').textContent='Wrong order — start again';G.tapIdx=0;document.querySelectorAll('.echo-chip').forEach(function(c){c.classList.remove('tapped');});return;}
  el.classList.add('tapped'); G.tapIdx++; G.score+=10; document.getElementById('gameScore').textContent=G.score;
  if(G.tapIdx>=G.phrase.length){document.getElementById('echoStatus').textContent='Great echo!';endGame(3);}
}
""",
        12: r"""
var G={step:0,score:0,sentences:['','','',''],errors:['the cat sat.','We go to school yesterday.','It was fun','We walk home.'],fixed:0};
function initGame(){
  G.step=0;G.score=0;G.fixed=0;document.getElementById('gameScore').textContent='0';
  renderArch();
}
function renderArch(){
  var steps=document.getElementById('archSteps'); var panel=document.getElementById('archPanel');
  steps.innerHTML=''; ['Build','Build','Build','Build','Fix'].forEach(function(l,i){
    var s=document.createElement('span'); s.className='arch-step'+(i===G.step?' active':i<G.step?' done':'');
    s.textContent=(i<4?'S'+(i+1):'Edit'); steps.appendChild(s);
  });
  panel.innerHTML='';
  if(G.step<4){
    var inp=document.createElement('input'); inp.className='arch-input'; inp.placeholder='Write sentence '+(G.step+1);
    inp.value=G.sentences[G.step];
    var btn=document.createElement('button'); btn.type='button'; btn.className='playlab-launch'; btn.textContent='Next';
    btn.onclick=function(){G.sentences[G.step]=inp.value;G.step++;G.score+=10;document.getElementById('gameScore').textContent=G.score;renderArch();};
    panel.appendChild(inp); panel.appendChild(btn);
  }else{
    var fixes=['The cat sat.','We went to school yesterday.','It was fun!','We walked home.'];
    G.errors.forEach(function(err,i){
      var d=document.createElement('div'); d.className='arch-error'; d.textContent=err;
      d.onclick=function(){d.classList.add('fixed');d.textContent=fixes[i];G.fixed++;G.score+=15;document.getElementById('gameScore').textContent=G.score;if(G.fixed>=4)endGame(3);};
      panel.appendChild(d);
    });
  }
}
""",
    }
    js = scripts.get(num, "function initGame(){document.getElementById('gameScore').textContent='0';}")
    return js.replace("createElement('motion.div')", "createElement('div')")


def shell_js(level_num: int) -> str:
    return f"""
const CURRENT_LEVEL_NUM={level_num};
function endGame(stars, score, combo) {{
  var end = document.getElementById('playlabEnd');
  var area = document.getElementById('playlabGameArea');
  if (end) end.classList.add('show');
  if (area) area.style.display = 'none';
  var st = document.getElementById('playlabStars');
  if (st) st.textContent = '★'.repeat(stars) + '☆'.repeat(3 - stars);
  var es = document.getElementById('endStats');
  if (es) es.textContent = 'Score: ' + (score || 0) + ' · Best combo: ×' + (combo || 1);
}}
function openPlaylab() {{
  var shell = document.getElementById('playlabShell');
  if (!shell) return;
  shell.hidden = false;
  shell.classList.add('is-open');
  document.body.classList.add('playlab-no-scroll');
  var end = document.getElementById('playlabEnd');
  if (end) end.classList.remove('show');
  var area = document.getElementById('playlabGameArea');
  if (area) area.style.display = 'flex';
  if (typeof initSkillGame === 'function') initSkillGame(CURRENT_LEVEL_NUM);
}}
function closePlaylab() {{
  var shell = document.getElementById('playlabShell');
  if (!shell) return;
  shell.classList.remove('is-open');
  shell.hidden = true;
  document.body.classList.remove('playlab-no-scroll');
  if (window._activeSkillGame) window._activeSkillGame.destroy();
}}
document.addEventListener('DOMContentLoaded', function() {{
  var lenis;
  try {{
    lenis = new Lenis({{ duration: 1.1 }});
    function raf(t) {{ lenis.raf(t); requestAnimationFrame(raf); }}
    requestAnimationFrame(raf);
  }} catch (e) {{}}
  try {{
    if (typeof gsap !== 'undefined') {{
      gsap.registerPlugin(ScrollTrigger);
      gsap.to('#curtain', {{
        opacity: 0, duration: 0.6, delay: 0.8,
        onComplete: function() {{ var c = document.getElementById('curtain'); if (c) c.style.display = 'none'; }}
      }});
    }}
  }} catch (e) {{
    setTimeout(function() {{ var c = document.getElementById('curtain'); if (c) c.style.display = 'none'; }}, 1200);
  }}
  var secIds = ['sec-hero','sec-learn','sec-examples','sec-worked','sec-reading','sec-try','sec-play','sec-quiz'];
  document.querySelectorAll('.progress-dots span').forEach(function(dot, i) {{
    dot.onclick = function() {{
      var s = dot.dataset.section || secIds[i];
      if (s) {{ var el = document.getElementById(s); if (el) el.scrollIntoView({{ behavior: 'smooth' }}); }}
    }};
  }});
  secIds.forEach(function(id) {{
    var el = document.getElementById(id);
    if (!el) return;
    new IntersectionObserver(function(entries) {{
      entries.forEach(function(e) {{
        if (e.isIntersecting) {{
          document.querySelectorAll('.progress-dots span').forEach(function(d) {{ d.classList.remove('active'); }});
          var d = document.querySelector('.progress-dots span[data-section="' + id + '"]');
          if (d) d.classList.add('active');
        }}
      }});
    }}, {{ threshold: 0.25 }}).observe(el);
  }});
  var openBtn = document.getElementById('openPlaylab');
  var closeBtn = document.getElementById('closePlaylab');
  if (openBtn) openBtn.onclick = openPlaylab;
  if (closeBtn) closeBtn.onclick = closePlaylab;
  var close2 = document.getElementById('closePlaylab2');
  if (close2) close2.onclick = closePlaylab;
  var restart = document.getElementById('playlabRestart');
  if (restart) restart.onclick = function() {{
    document.getElementById('playlabEnd').classList.remove('show');
    document.getElementById('playlabGameArea').style.display = 'flex';
    if (typeof restartSkillGame === 'function') restartSkillGame();
  }};
  var answers = {{}};
  document.querySelectorAll('.quiz-q').forEach(function(q) {{
    var qi = q.dataset.q;
    answers[qi] = null;
    q.querySelectorAll('.quiz-opt').forEach(function(opt) {{
      opt.onclick = function() {{
        q.querySelectorAll('.quiz-opt').forEach(function(o) {{ o.classList.remove('selected'); }});
        opt.classList.add('selected');
        answers[qi] = parseInt(opt.dataset.idx, 10);
      }};
    }});
  }});
  var quizBtn = document.getElementById('quizSubmit');
  if (quizBtn) quizBtn.onclick = function() {{
    var correct = 0, total = 0;
    document.querySelectorAll('.quiz-q').forEach(function(q) {{
      total++;
      var qi = q.dataset.q;
      var ok = parseInt(q.dataset.correct, 10);
      q.querySelectorAll('.quiz-opt').forEach(function(o) {{
        var idx = parseInt(o.dataset.idx, 10);
        o.classList.remove('correct', 'wrong');
        if (answers[qi] === idx) {{
          if (idx === ok) {{ o.classList.add('correct'); correct++; }}
          else o.classList.add('wrong');
        }} else if (idx === ok) o.classList.add('correct');
      }});
    }});
    var res = document.getElementById('quizResult');
    if (res) {{
      res.classList.add('show');
      var need = Math.ceil(total * 0.6);
      res.textContent = 'You got ' + correct + '/' + total + ' correct! (Pass: ' + need + '/' + total + ')';
    }}
  }};
  document.querySelectorAll('.try-reveal').forEach(function(btn) {{
    btn.onclick = function() {{
      var el = document.getElementById('tryAns' + btn.dataset.try);
      if (el) {{ el.classList.add('show'); btn.textContent = 'Answer shown'; btn.disabled = true; }}
    }};
  }});
}});
"""


def copy_assets() -> None:
    dest = OUT / "assets"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ASSETS_SRC, dest)


def showcase_html(level: dict) -> str:
    items = level.get("showcase") or level.get("examples", [])
    tiles = []
    for i, item in enumerate(items):
        if len(item) == 3:
            main, sub, accent = item
        else:
            main, sub = item[0], item[1]
            accent = ["green", "amber", "navy"][i % 3]
        tiles.append(
            f'<div class="example-tile {accent}"><div class="ex-main">{main}</div>'
            f'<p class="ex-sub">{sub}</p></div>'
        )
    return (
        '<div class="example-grid">'
        + "".join(tiles).replace("<div", "<div").replace("</div>", "</div>")
        + "</div>"
    ).replace("<div", "<div").replace("</div>", "</div>")


def worked_html(level: dict) -> str:
    blocks = []
    for title, steps in level.get("worked", []):
        steps_h = "".join(
            f'<div class="worked-step"><span class="step-num">{i+1}</span>'
            f'<div class="step-body">{s}</div></div>'
            for i, s in enumerate(steps)
        )
        blocks.append(
            f'<div class="worked-example"><h3>{title}</h3>{steps_h}</div>'
        )
    return "\n".join(blocks)


def try_it_html(level: dict) -> str:
    items = []
    for i, (q, a) in enumerate(level.get("try_it", [])):
        items.append(
            f'<div class="try-item"><p class="try-q">{i+1}. {q}</p>'
            f'<button type="button" class="try-reveal" data-try="{i}">Show answer</button>'
            f'<div class="try-answer" id="tryAns{i}">{esc(a)}</div></div>'
        )
    return '<div class="try-it-list">' + "\n".join(items) + "</div>"


def reading_html(level: dict) -> str:
    text = level.get("reading", "")
    if not text:
        return ""
    return (
        f'<div class="reading-passage"><div class="reading-label">Read &amp; notice</div>'
        f"<p>{text}</p></div>"
    ).replace("<div", "<div").replace("</div>", "</div>")


def quiz_html(level: dict) -> str:
    parts = []
    for i, (q, opts, correct) in enumerate(level["quiz"]):
        opts_html = "".join(
            f'<button type="button" class="quiz-opt" data-idx="{j}">{esc(o)}</button>'
            for j, o in enumerate(opts)
        )
        parts.append(
            f'<div class="quiz-q" data-q="{i}" data-correct="{correct}">'
            f'<div class="q-text">{i + 1}. {q}</div>'
            f'<div class="quiz-options">{opts_html}</div></div>'
        )
    return "\n".join(parts)


def teach_html(level: dict) -> str:
    blocks = []
    for title, body in level["teach"]:
        blocks.append(
            f'<div class="highlight-box"><h3>{title}</h3><p>{body}</p></div>'
        )
    return "\n".join(blocks)


def vocab_html(level: dict) -> str:
    items = "".join(f"<li><strong>{esc(v)}</strong></li>" for v in level["vocab"])
    return f'<div class="sidebar-card"><h4>Key Words</h4><ul>{items}</ul></div>'


def generate_level(level: dict, theme: str) -> str:
    n = level["num"]

    sec_ids = ["sec-hero", "sec-learn", "sec-examples", "sec-worked", "sec-reading", "sec-try", "sec-play", "sec-quiz"]
    pdots = "".join(
        (f'<span data-section="{sid}"' + (' class="active"' if i == 0 else "") + f' title="{sid.replace("sec-","")}"></span>')
        for i, sid in enumerate(sec_ids)
    )
    pills = level.get("pills", f'<span class="playlab-pill">{esc(level["skill"])}</span>')
    if isinstance(pills, list):
        pills = "".join(f'<span class="playlab-pill">{p}</span>' for p in pills)

    return f"""<!-- TRACK: Skill Based | COURSE: English Language | LEVEL: {n} | VERSION: 2.0 -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(level["title"])} | English Language Skill</title>
{FONTS}
{SCRIPTS}
<link rel="stylesheet" href="assets/playlab.css">
<style>
{theme}
</style>
</head>
<body>
<div id="curtain"><div class="logo">English Skills</div><div class="sub">{esc(level["game"])}</div><div class="curtain-spinner"></div></div>

<header class="sticky-header">
  <h1>{esc(level["title"])}</h1>
  <div class="progress-dots" id="headerDots">{pdots}</div>
</header>

<section class="hero" id="sec-hero">
  <span class="hero-badge">{esc(level["skill"])}</span>
  <h1>{esc(level["title"])}</h1>
  <p>{esc(level["objective"])}</p>
  <div class="hero-stars">{stars_html(level["difficulty"])}</div>
</section>

<main class="page-wrapper">
<section class="content-section" id="sec-learn">
  <div class="container two-col">
    <div class="main-col">
      <span class="section-label">Learn</span>
      <h2 class="section-title">Rules &amp; Ideas</h2>
      <p class="section-subtitle">Skill: {esc(level["skill"])} — read carefully before the examples and quiz.</p>
      {teach_html(level)}
    </div>
    <aside class="sidebar-col">
      {vocab_html(level)}
      <div class="sidebar-card"><h4>Remember</h4><p>{esc(level["tip"])}</p></div>
    </aside>
  </div>
</section>

<section class="content-section" id="sec-examples">
  <div class="container">
    <span class="section-label">Examples</span>
    <h2 class="section-title">See It in Action</h2>
    <p class="section-subtitle">Study these examples before you practise on your own.</p>
    {showcase_html(level)}
  </div>
</section>

<section class="content-section" id="sec-worked">
  <div class="container">
    <span class="section-label">Worked examples</span>
    <h2 class="section-title">Step by Step</h2>
    <p class="section-subtitle">Follow each step — the same thinking helps in the quiz.</p>
    {worked_html(level)}
  </div>
</section>

<section class="content-section" id="sec-reading">
  <div class="container">
    <span class="section-label">Reading</span>
    <h2 class="section-title">Short Passage</h2>
    {reading_html(level)}
  </div>
</section>

<section class="content-section" id="sec-try">
  <div class="container">
    <span class="section-label">Try it yourself</span>
    <h2 class="section-title">Quick Checks</h2>
    <p class="section-subtitle">Think first, then tap Show answer.</p>
    {try_it_html(level)}
  </div>
</section>

<section class="content-section playlab-teaser" id="sec-play">
  <div class="container">
    <div class="playlab-teaser-card">
      <div class="playlab-game-icon">🎮</div>
      <span class="section-label">Interactive Game</span>
      <h2 class="section-title">{esc(level["game"])}</h2>
      <p class="section-subtitle">Arcade practice with score, combos, and lives.</p>
      <div class="playlab-pills">{pills}</div>
      <button type="button" class="playlab-launch" id="openPlaylab">Launch Game</button>
    </div>
  </div>
</section>

<section class="content-section" id="sec-quiz">
  <div class="container">
    <span class="section-label">Practice Quiz</span>
    <h2 class="section-title">Check Understanding</h2>
    <p class="quiz-section-intro">Answer all {len(level["quiz"])} questions, then submit. You need at least 60% to pass.</p>
    {quiz_html(level)}
    <button type="button" class="quiz-submit" id="quizSubmit">Check Answers</button>
    <div class="quiz-result" id="quizResult" aria-live="polite"></div>
    <p class="level-footer">Standalone lesson — open any level file directly in your browser.</p>
  </div>
</section>
</main>

<div class="playlab-shell" id="playlabShell" hidden>
  <header class="playlab-topbar">
    <button type="button" class="playlab-close" id="closePlaylab">✕ Exit</button>
    <h2>{esc(level["game"])}</h2>
    <div class="playlab-stats">
      <span class="playlab-stat"><span class="lbl">Score</span><span class="val" id="plScore">0</span></span>
      <span class="playlab-stat combo"><span class="lbl">Combo</span><span class="val" id="plCombo">—</span></span>
      <span class="playlab-stat"><span class="lbl">Lives</span><span class="val" id="plLives">♥♥♥</span></span>
      <span class="playlab-stat"><span class="lbl">Time</span><span class="val" id="plTimer">—</span></span>
    </div>
  </header>
  <div class="playlab-objective" id="gameObjective"></div>
  <div class="playlab-stage-wrap" id="playlabGameArea">
    <div class="playlab-stage" id="gameStage"></div>
    <div class="pl-toast" id="plToast"></div>
  </div>
  <footer class="playlab-footer">
    <div class="pl-progress-track"><div class="pl-progress-bar" id="plProgressBar"></div></div>
  </footer>
  <div class="playlab-end" id="playlabEnd">
    <h3>Mission Complete!</h3>
    <div class="stars" id="playlabStars">★★★</div>
    <p class="end-stats" id="endStats"></p>
    <button type="button" class="playlab-launch" id="playlabRestart">Play Again</button>
    <button type="button" class="playlab-launch" id="closePlaylab2" style="background:transparent;border:2px solid rgba(255,255,255,.4);box-shadow:none">Back to Lesson</button>
  </div>
</div>

<nav id="mobile-bottom-nav" aria-label="Lesson sections">
  <div class="nav-inner">
    <a href="#sec-learn"><span class="nav-icon">📖</span>Learn</a>
    <a href="#sec-examples"><span class="nav-icon">💡</span>Examples</a>
    <a href="#sec-play"><span class="nav-icon">🎮</span>Game</a>
    <a href="#sec-quiz"><span class="nav-icon">✓</span>Quiz</a>

  </div>
</nav>

<script src="assets/game-engine.js"></script>
<script src="assets/games/level-{n:02d}.js"></script>
<script>
{shell_js(n)}
</script>
</body>
</html>
""".replace("<div", "<div").replace("</div>", "</div>")


def generate_hub(theme: str) -> str:
    cards = []
    for lv in LEVELS:
        n = lv["num"]
        nn = f"{n:02d}"
        cards.append(
            f"""<article class="hub-card" data-level="{n}" id="card-{n}">
  <span class="hub-level">Level {n}</span>
  <h3>{esc(lv["title"])}</h3>
  <p class="hub-skill">{esc(lv["skill"])} · {esc(lv["game"])}</p>
  <div class="hub-stars">{stars_html(lv["difficulty"])}</div>
  <a class="hub-play" href="{nn}.html" data-link="{nn}.html">Play</a>
  <span class="hub-lock" aria-hidden="true">🔒 Complete Level {n-1} first</span>
</article>"""
        )
    cards_html = "\n".join(cards)

    return f"""<!-- TRACK: Skill Based | COURSE: English Language | LEVEL: Hub | VERSION: 1.0 -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>English Language Skills | 12 Levels</title>
{FONTS}
{SCRIPTS}
<style>
{theme}
.hub-hero{{min-height:45vh}}
.hub-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px;padding:40px 0 80px}}
.hub-card{{background:#fff;border-radius:var(--border-radius);box-shadow:var(--shadow);padding:22px;position:relative;transition:transform .2s}}
.hub-card:hover{{transform:translateY(-4px)}}
.hub-card.locked{{opacity:.55}}
.hub-card.locked .hub-play{{pointer-events:none;opacity:.5}}
.hub-card.locked .hub-lock{{display:block}}
.hub-lock{{display:none;font-size:.85rem;color:#888;margin-top:8px}}
.hub-level{{font-size:.8rem;font-weight:700;color:var(--green);text-transform:uppercase}}
.hub-card h3{{font-size:1.2rem;margin:8px 0;color:var(--navy)}}
.hub-skill{{font-size:.9rem;color:#666;margin-bottom:8px}}
.hub-stars{{color:var(--amber);margin-bottom:12px}}
.hub-play{{display:inline-block;background:var(--green);color:#fff;text-decoration:none;padding:10px 22px;border-radius:999px;font-family:'Poppins',sans-serif;font-weight:700}}
.hub-card.done .hub-level::after{{content:' ✓';color:var(--green)}}
</style>
</head>
<body>
<div id="curtain"><div class="logo">English Language</div><div class="sub">12 Skill Levels</div><div class="curtain-spinner"></div></div>
<header class="sticky-header"><h1>English Language Skills</h1><a class="hub-link" href="../">OTS Skills</a></header>
<section class="hero hub-hero">
  <span class="hero-badge">Skill Based Course</span>
  <h1>English Language</h1>
  <p>Twelve levels from letters and sounds to story editing. Progress saves on this device.</p>
</section>
<main class="container">
  <div class="hub-grid" id="hubGrid">{cards_html}</div>
</main>
<nav id="mobile-bottom-nav"><div class="nav-inner"><a href="#" class="active"><span class="nav-icon">⊞</span>Levels</a></div></nav>
<script>
const STORAGE_KEY='{STORAGE_KEY}';
const SOFT_LOCK=true;
function getProgress(){{try{{return JSON.parse(localStorage.getItem(STORAGE_KEY)||'{{}}');}}catch(e){{return {{}};}}}}
document.addEventListener('DOMContentLoaded',function(){{
  try{{if(typeof gsap!=='undefined')gsap.to('#curtain',{{opacity:0,duration:.6,delay:.5,onComplete:function(){{var c=document.getElementById('curtain');if(c)c.style.display='none';}}}});}}catch(e){{setTimeout(function(){{var c=document.getElementById('curtain');if(c)c.style.display='none';}},900);}}
  var p=getProgress();
  document.querySelectorAll('.hub-card').forEach(function(card){{
    var n=parseInt(card.dataset.level,10);
    var link=card.querySelector('.hub-play');
    if(p[String(n)]&&p[String(n)].completed) card.classList.add('done');
    if(SOFT_LOCK&&n>1&&!((p[String(n-1)]||{{}}).completed||(p[String(n-1)]||{{}}).quizDone)){{card.classList.add('locked');if(link)link.addEventListener('click',function(e){{e.preventDefault();alert('Finish Level '+(n-1)+' first!');}});}}
  }});
}});
</script>
</body>
</html>
""".replace("<div", "<div").replace("</div>", "</div>")


def main() -> None:
    from levels_data import merge_into_level

    theme = read_theme()
    OUT.mkdir(parents=True, exist_ok=True)
    created = []
    copy_assets()
    created.append(str(OUT / "assets"))
    idx = OUT / "index.html"
    if idx.exists():
        idx.unlink()
    for lv in LEVELS:
        merged = merge_into_level(lv)
        path = OUT / f"{merged['num']:02d}.html"
        path.write_text(generate_level(merged, theme), encoding="utf-8")
        created.append(str(path))
    print("Created files:")
    for f in created:
        print(" ", f)
    print(f"Total: {len(created)} files")


if __name__ == "__main__":
    main()
