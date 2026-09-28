"""
Krushi Sakha — full feature parity, HTML + Python (Flask) version.
Run with:  pip install flask pillow
           python app.py
Then open: http://localhost:5000
"""

from flask import Flask, request, render_template_string
from PIL import Image, ImageStat
import io

app = Flask(__name__)

# ---------- Data ----------

CROP_ORDER = ["tomato", "potato", "chili", "brinjal", "onion", "mango", "banana"]
CROP_EMOJI = {"tomato": "🍅", "potato": "🥔", "chili": "🌶️", "brinjal": "🍆",
              "onion": "🧅", "mango": "🥭", "banana": "🍌"}

SAMPLE_ORDER = ["healthy", "blight", "nutrient", "water", "pest", "poor"]
SAMPLE_VISUAL = {
    "healthy": {"yellow": .05, "spot": .03, "wilt": .05, "holes": .02, "quality": .92},
    "blight":  {"yellow": .2,  "spot": .78, "wilt": .12, "holes": .03, "quality": .88},
    "nutrient":{"yellow": .72, "spot": .04, "wilt": .08, "holes": .02, "quality": .88},
    "water":   {"yellow": .5,  "spot": .05, "wilt": .6,  "holes": .02, "quality": .85},
    "pest":    {"yellow": .12, "spot": .08, "wilt": .08, "holes": .68, "quality": .88},
    "poor":    {"yellow": .4,  "spot": .32, "wilt": .28, "holes": .1,  "quality": .22},
}
SAMPLE_FILL = {"healthy": "#4C8C4A", "blight": "#7E9A55", "nutrient": "#C7B23A",
               "water": "#B99A3E", "pest": "#4C8C4A", "poor": "#8E9A6A"}
SAMPLE_OVERLAY = {"blight": "spot", "pest": "hole", "poor": "blur"}

EXPERT = {"name": "Dr. Ramesh Patil", "phone": "+919876543210",
          "phone_display": "+91 98765 43210"}

I18N = {
"en": {
  "heroTitle": "One photo rarely tells the whole story",
  "heroLead": "A yellow leaf can mean disease, pests, hunger, or thirst. Krushi Sakha reads the picture alongside your field's own conditions — rainfall, humidity, what you've already noticed — before it says what it thinks is wrong.",
  "heroNote": 'Try it: pick "Yellowing leaf" below, analyze with rainfall set to Normal, then switch rainfall to None and analyze again — the verdict changes.',
  "stepCropTitle": "1. Which crop is this?", "stepCropSub": "Krushi Sakha works across multiple crops, not just one",
  "crops": {"tomato":"Tomato","potato":"Potato","chili":"Chili","brinjal":"Brinjal","onion":"Onion","mango":"Mango","banana":"Banana"},
  "step1Title": "2. Choose a leaf", "step1Sub": "Use a sample, or upload your own field photo", "orUpload": "or upload a photo",
  "step2Title": "3. Tell us about the field", "step2Sub": "This context is what lets Krushi Sakha tell similar-looking symptoms apart",
  "rainfallLabel": "Rainfall this week", "rain": {"none":"None — dry spell","light":"Light","normal":"Normal","heavy":"Heavy"},
  "humidityLabel": "Humidity (%)", "symptomsLabel": "What have you noticed? (optional — reinforces the photo)",
  "chips": {"yellow":"Yellowing leaves","spot":"Brown/dark spots","wilt":"Wilting or drooping","holes":"Holes or chewed edges"},
  "samples": {"healthy":"Healthy","blight":"Spotted leaf","nutrient":"Yellowing leaf","water":"Wilting leaf","pest":"Chewed leaf","poor":"Blurry photo"},
  "analyze": "Analyze", "confidence": "Confidence",
  "badgeOk": "Confident assessment", "badgeWarn": "Needs expert review",
  "actionsDefault": "Recommended next step", "actionsWarn": "Leading possibility — don't treat yet",
  "expertRole": "Agriculture Extension Officer · Mon–Sat, 9am–6pm",
  "expertNote": "The photo and field conditions don't clearly agree — confirming with an expert before treating is the safer step.",
  "callBtn": "📞 Call", "disclaimer": "This is guidance based on the photo and the details you entered — not a yield or crop-loss estimate. For treatment decisions with real cost at stake, confirm with a local expert.",
  "footer": "Krushi Sakha · HTML + Python advisory demo",
  "rainCtx": {"none":"very low this week","light":"light this week","normal":"normal","heavy":"heavy"},
  "causes": {
    "healthy": {"name":"Healthy plant", "explain": lambda ctx, rl: "The leaf shows even, strong colour with no spotting, wilting or holes, and nothing you entered about the field points to stress either.", "actions": ["Keep your current watering and care routine","Check again in about a week"]},
    "blight": {"name":"Likely fungal disease (early blight)", "explain": lambda ctx, rl: f"Dark, irregular spotting is visible, and humidity is around {ctx['humidity']}% — fungal disease spreads fastest in warm, humid air, which fits what's showing here.", "actions": ["Remove and destroy the affected leaves","Apply a fungicide suited to early blight","Water at the base, not over the leaves"]},
    "nutrient": {"name":"Likely nutrient deficiency", "explain": lambda ctx, rl: f"The leaf is yellowing with no spotting or wilting, and rainfall has been {rl} — when watering isn't the issue, yellowing like this usually points to a nutrient gap, often nitrogen.", "actions": ["Apply a balanced, nitrogen-rich fertiliser","Recheck 7–10 days after feeding"]},
    "water": {"name":"Likely water stress", "explain": lambda ctx, rl: f"The leaf is yellowing and wilting together, and rainfall has been {rl} — that combination points to the roots not getting enough water.", "actions": ["Water more frequently, especially through dry spells","Check soil moisture at root depth before the next watering"]},
    "pest": {"name":"Likely pest damage", "explain": lambda ctx, rl: "Holes and chewed edges point to pest feeding rather than disease or a water/nutrient issue.", "actions": ["Check the underside of leaves for insects","Use a pest-control step suited to what you find there"]},
  },
},
"hi": {
  "heroTitle": "एक फोटो पूरी कहानी नहीं बताता",
  "heroLead": "पीली पत्ती बीमारी, कीट, पोषण की कमी या पानी की कमी — किसी भी वजह से हो सकती है। Krushi Sakha फोटो के साथ आपके खेत की असली स्थिति — बारिश, नमी, आपने जो देखा — सब मिलाकर बताता है।",
  "heroNote": 'आज़माएं: नीचे "पीली पत्ती" चुनें, बारिश "सामान्य" रखकर विश्लेषण करें, फिर बारिश "नहीं" पर बदलकर दोबारा विश्लेषण करें — नतीजा बदल जाएगा।',
  "stepCropTitle": "१. फसल कौन सी है?", "stepCropSub": "Krushi Sakha सिर्फ एक नहीं, कई फसलों पर काम करता है",
  "crops": {"tomato":"टमाटर","potato":"आलू","chili":"मिर्च","brinjal":"बैंगन","onion":"प्याज़","mango":"आम","banana":"केला"},
  "step1Title": "२. एक पत्ती चुनें", "step1Sub": "नमूना इस्तेमाल करें, या अपने खेत की फोटो अपलोड करें", "orUpload": "या फोटो अपलोड करें",
  "step2Title": "३. खेत के बारे में बताएं", "step2Sub": "यही जानकारी Krushi Sakha को मिलते-जुलते लक्षणों में फर्क बताने में मदद करती है",
  "rainfallLabel": "इस हफ्ते बारिश", "rain": {"none":"नहीं — सूखा","light":"हल्की","normal":"सामान्य","heavy":"भारी"},
  "humidityLabel": "नमी (%)", "symptomsLabel": "आपने क्या देखा है? (वैकल्पिक)",
  "chips": {"yellow":"पीली पत्तियां","spot":"भूरे/काले धब्बे","wilt":"मुरझाना या झुकना","holes":"छेद या कटे किनारे"},
  "samples": {"healthy":"स्वस्थ","blight":"धब्बेदार पत्ती","nutrient":"पीली पत्ती","water":"मुरझाई पत्ती","pest":"कटी पत्ती","poor":"धुंधली फोटो"},
  "analyze": "विश्लेषण करें", "confidence": "विश्वास स्तर",
  "badgeOk": "पक्का आकलन", "badgeWarn": "विशेषज्ञ की राय ज़रूरी",
  "actionsDefault": "अगला कदम", "actionsWarn": "संभावित कारण — अभी इलाज न करें",
  "expertRole": "कृषि विस्तार अधिकारी · सोम–शनि, सुबह ९ – शाम ६",
  "expertNote": "फोटो और खेत की स्थिति पूरी तरह मेल नहीं खा रही — इलाज से पहले विशेषज्ञ से पुष्टि करना सुरक्षित है।",
  "callBtn": "📞 कॉल करें", "disclaimer": "यह सलाह फोटो और आपकी दी गई जानकारी पर आधारित है — यह उपज या नुकसान का अनुमान नहीं है। बड़े खर्च वाले फैसलों के लिए स्थानीय विशेषज्ञ से पुष्टि करें।",
  "footer": "Krushi Sakha · HTML + Python डेमो",
  "rainCtx": {"none":"बहुत कम","light":"हल्की","normal":"सामान्य","heavy":"भारी"},
  "causes": {
    "healthy": {"name":"स्वस्थ पौधा", "explain": lambda ctx, rl: "पत्ती का रंग एक समान और मज़बूत है, कोई धब्बा, मुरझाना या छेद नहीं है — और आपकी दी गई जानकारी में भी तनाव का कोई संकेत नहीं है।", "actions": ["पानी और देखभाल का मौजूदा तरीका जारी रखें","एक हफ्ते बाद दोबारा जांचें"]},
    "blight": {"name":"संभावित फफूंद रोग (अर्ली ब्लाइट)", "explain": lambda ctx, rl: f"गहरे, बेढंगे धब्बे दिख रहे हैं, और नमी लगभग {ctx['humidity']}% है — गर्म, नम मौसम में फफूंद रोग सबसे तेज़ फैलता है।", "actions": ["प्रभावित पत्तियों को हटाकर नष्ट करें","अर्ली ब्लाइट के लिए उपयुक्त फफूंदनाशक डालें","ऊपर से नहीं, जड़ में पानी दें"]},
    "nutrient": {"name":"संभावित पोषण की कमी", "explain": lambda ctx, rl: f"पत्ती बिना धब्बे या मुरझाए पीली हो रही है, और बारिश {rl} रही है — यह पोषण की कमी, अक्सर नाइट्रोजन, की ओर इशारा करता है।", "actions": ["संतुलित, नाइट्रोजन युक्त खाद डालें","खाद देने के ७–१० दिन बाद दोबारा जांचें"]},
    "water": {"name":"संभावित पानी की कमी", "explain": lambda ctx, rl: f"पत्ती पीली भी हो रही है और मुरझा भी रही है, और बारिश {rl} रही है — यह जड़ों तक पानी न पहुंचने की ओर इशारा करता है।", "actions": ["सूखे समय में पानी अधिक बार दें","अगली सिंचाई से पहले मिट्टी की नमी जांचें"]},
    "pest": {"name":"संभावित कीट नुकसान", "explain": lambda ctx, rl: "पत्ती पर छेद और कटे किनारे कीट के खाने का संकेत देते हैं।", "actions": ["पत्तियों के नीचे कीट जांचें","उपयुक्त उपाय करें"]},
  },
},
"mr": {
  "heroTitle": "एक फोटो संपूर्ण कहाणी सांगत नाही",
  "heroLead": "पिवळे पान रोग, कीड, अन्नद्रव्यांची कमतरता किंवा पाण्याच्या कमतरतेमुळे असू शकते. Krushi Sakha फोटोसोबत तुमच्या शेतातील खरी परिस्थिती एकत्र करून सांगतं.",
  "heroNote": 'करून पहा: खाली "पिवळं पान" निवडा, पाऊस "सामान्य" ठेवून विश्लेषण करा, नंतर पाऊस "नाही" वर बदलून पुन्हा विश्लेषण करा — निकाल बदलेल.',
  "stepCropTitle": "१. कोणते पीक आहे?", "stepCropSub": "Krushi Sakha फक्त एका नव्हे, अनेक पिकांसाठी काम करतं",
  "crops": {"tomato":"टोमॅटो","potato":"बटाटा","chili":"मिरची","brinjal":"वांगं","onion":"कांदा","mango":"आंबा","banana":"केळं"},
  "step1Title": "२. एक पान निवडा", "step1Sub": "नमुना वापरा, किंवा तुमच्या शेतातील फोटो अपलोड करा", "orUpload": "किंवा फोटो अपलोड करा",
  "step2Title": "३. शेताबद्दल सांगा", "step2Sub": "हीच माहिती Krushi Sakha ला लक्षणांमध्ये फरक ओळखायला मदत करते",
  "rainfallLabel": "या आठवड्यातील पाऊस", "rain": {"none":"नाही — कोरडा हंगाम","light":"हलका","normal":"सामान्य","heavy":"जास्त"},
  "humidityLabel": "आर्द्रता (%)", "symptomsLabel": "तुम्ही काय पाहिलं आहे? (ऐच्छिक)",
  "chips": {"yellow":"पिवळी पाने","spot":"तपकिरी/काळे डाग","wilt":"कोमेजणे किंवा लटकणे","holes":"छिद्रे किंवा कापलेल्या कडा"},
  "samples": {"healthy":"निरोगी","blight":"डाग असलेलं पान","nutrient":"पिवळं पान","water":"कोमेजलेलं पान","pest":"कापलेलं पान","poor":"अस्पष्ट फोटो"},
  "analyze": "विश्लेषण करा", "confidence": "विश्वासार्हता",
  "badgeOk": "खात्रीशीर निष्कर्ष", "badgeWarn": "तज्ञांचा सल्ला आवश्यक",
  "actionsDefault": "पुढील पायरी", "actionsWarn": "शक्य कारण — अजून उपचार करू नका",
  "expertRole": "कृषी विस्तार अधिकारी · सोम–शनि, सकाळी ९ – संध्याकाळी ६",
  "expertNote": "फोटो आणि शेतातील परिस्थिती पूर्णपणे जुळत नाही — उपचार करण्यापूर्वी तज्ञांकडून खात्री करणं सुरक्षित आहे.",
  "callBtn": "📞 कॉल करा", "disclaimer": "हा सल्ला फोटो आणि तुम्ही दिलेल्या माहितीवर आधारित आहे — हे उत्पन्न किंवा नुकसानाचा अंदाज नाही. मोठ्या खर्चाच्या निर्णयांसाठी स्थानिक तज्ञांकडून खात्री करा.",
  "footer": "Krushi Sakha · HTML + Python डेमो",
  "rainCtx": {"none":"खूप कमी","light":"हलका","normal":"सामान्य","heavy":"जास्त"},
  "causes": {
    "healthy": {"name":"निरोगी रोप", "explain": lambda ctx, rl: "पानाचा रंग एकसमान आणि मजबूत आहे, कोणतेही डाग, कोमेजणे किंवा छिद्रे नाहीत.", "actions": ["सध्याची पाणी आणि काळजी पद्धत सुरू ठेवा","एका आठवड्यानंतर पुन्हा तपासा"]},
    "blight": {"name":"शक्य बुरशीजन्य रोग (अर्ली ब्लाइट)", "explain": lambda ctx, rl: f"गडद, अनियमित डाग दिसत आहेत, आणि आर्द्रता सुमारे {ctx['humidity']}% आहे — बुरशीजन्य रोग दमट हवामानात वेगाने पसरतो.", "actions": ["बाधित पाने काढून नष्ट करा","अर्ली ब्लाइटसाठी योग्य बुरशीनाशक फवारा","वरून नाही, मुळाशी पाणी द्या"]},
    "nutrient": {"name":"शक्य अन्नद्रव्यांची कमतरता", "explain": lambda ctx, rl: f"पान डाग किंवा कोमेजल्याशिवाय पिवळं पडत आहे, आणि पाऊस {rl} आहे — हे अन्नद्रव्यांच्या कमतरतेकडे निर्देश करतं.", "actions": ["संतुलित, नायट्रोजनयुक्त खत द्या","७–१० दिवसांनी पुन्हा तपासा"]},
    "water": {"name":"शक्य पाण्याचा ताण", "explain": lambda ctx, rl: f"पान पिवळं पडत आहे आणि कोमेजतही आहे, आणि पाऊस {rl} आहे — हे मुळांना पुरेसं पाणी न मिळाल्याकडे निर्देश करतं.", "actions": ["कोरड्या काळात पाणी जास्त वेळा द्या","मातीतील ओलावा तपासा"]},
    "pest": {"name":"शक्य कीड नुकसान", "explain": lambda ctx, rl: "पानावरील छिद्रे आणि कापलेल्या कडा कीड खाल्ल्याचं दर्शवतात.", "actions": ["पानांच्या खालच्या बाजूला कीड तपासा","योग्य उपाय करा"]},
  },
},
}

# ---------- Vision + rule engine ----------

def analyze_image(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB").resize((60, 60))
    r, g, b = ImageStat.Stat(img).mean
    yellow = max(0.0, min(1.0, ((r + g) / 2 - b) / 255 * 1.4))
    gray_std = ImageStat.Stat(img.convert("L")).stddev[0]
    quality = max(0.0, min(1.0, gray_std / 60))
    spot = max(0.0, min(1.0, (1 - (r + g + b) / (3 * 180)) * 0.6))
    return {"yellow": round(yellow, 3), "spot": round(spot, 3),
            "wilt": round(yellow * 0.4, 3), "holes": 0.05,
            "quality": round(0.3 + quality * 0.7, 3)}

def clamp(x): return max(0.0, min(1.0, x))

def score_causes(v, ctx):
    humid = ctx["humidity"] / 100
    sym = ctx["symptoms"]
    bump = lambda k: 0.15 if k in sym else 0
    scores = {
        "healthy": clamp(1 - max(v["yellow"], v["spot"], v["wilt"], v["holes"]) - (1 - v["quality"]) * 0.3),
        "blight": clamp(v["spot"] * 0.65 + humid * 0.3 + bump("spot")),
        "nutrient": clamp(v["yellow"] * 0.6 - v["spot"] * 0.4 + (0.2 if ctx["rainfall"] in ("normal", "heavy") else 0) + bump("yellow")),
        "water": clamp(v["yellow"] * 0.35 + v["wilt"] * 0.4 + (0.35 if ctx["rainfall"] == "none" else 0.15 if ctx["rainfall"] == "light" else 0) + bump("wilt")),
        "pest": clamp(v["holes"] * 0.75 + bump("holes")),
    }
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_key, top_score = ranked[0]
    margin = top_score - ranked[1][1]
    confidence = clamp(top_score * (0.5 + 0.5 * v["quality"]) * (0.6 + 0.4 * min(margin / 0.25, 1)))
    needs_expert = confidence < 0.55 or v["quality"] < 0.4 or margin < 0.1
    return top_key, confidence, needs_expert

def leaf_svg(fill, overlay=None):
    s = f'<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="#E4EFD6"/><path d="M50 18 C78 21,90 42,83 66 C76 88,54 92,32 82 C24 64,30 38,50 18 Z" fill="{fill}"/></svg>'
    if overlay == "spot":
        s += '<div class="spotoverlay"></div>'
    elif overlay == "hole":
        s += '<div class="holeoverlay"></div>'
    elif overlay == "blur":
        s += '<div class="bluroverlay"></div>'
    return s

# ---------- Template ----------

PAGE = """
<!doctype html><html lang="{{ lang }}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Krushi Sakha</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{--cream:#E4EFD6;--paper:#FBFCF6;--ink:#233821;--green:#3B6B3E;--green-deep:#1E3D24;--rust:#B5533C;--line:rgba(30,61,36,.16);--shadow:0 10px 30px rgba(20,40,20,.12)}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter','Noto Sans Devanagari',sans-serif;color:var(--ink);line-height:1.5;
 background:radial-gradient(700px 420px at 90% -8%,rgba(255,255,255,.35),transparent 60%),radial-gradient(900px 500px at -10% 10%,rgba(59,107,62,.18),transparent 55%),var(--cream)}
h1,h2{font-family:'Fraunces','Noto Sans Devanagari',serif;color:var(--green-deep);margin:0}
.wrap{max-width:720px;margin:0 auto;padding:0 20px 40px}
header{display:flex;align-items:center;gap:12px;padding:16px 20px}
.brand{font-family:'Fraunces',serif;font-weight:700;font-size:20px;color:var(--green-deep)}
.langsel{margin-left:auto}
select{padding:7px 10px;border-radius:8px;border:1px solid var(--line);background:var(--paper);font-family:inherit}
h1{font-size:clamp(26px,5vw,38px);margin:20px 0 10px;max-width:18ch}
.lead{max-width:58ch;opacity:.85}
.note{margin-top:14px;font-size:14px;display:inline-block;background:rgba(139,94,60,.1);border:1px solid rgba(139,94,60,.25);padding:9px 13px;border-radius:10px;color:#5E3E27}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:var(--shadow);margin-top:16px}
.sub{font-size:14px;opacity:.7;margin:4px 0 14px}
.row{display:flex;flex-wrap:wrap;gap:10px}
.chip{display:block;border:1px solid var(--line);background:var(--cream);border-radius:12px;padding:9px 12px;text-align:center;cursor:pointer;font-size:13px}
.chip .emoji,.chip .icon{font-size:20px;display:block;margin-bottom:4px}
.chip .icon svg{width:34px;height:34px}
input[type=radio],input[type=checkbox]{display:none}
input:checked + .chip{border-color:var(--green);outline:2px solid var(--green);background:rgba(59,107,62,.1)}
.spotoverlay,.holeoverlay,.bluroverlay{width:34px;height:34px;margin:0 auto;border-radius:50%;position:relative;top:-34px}
.divider{margin:16px 0;font-size:12px;opacity:.55;text-align:center}
select,input[type=number],input[type=file]{width:100%;padding:9px 10px;border-radius:8px;border:1px solid var(--line);background:var(--cream);font-family:inherit;margin-top:6px}
label.field{display:block;margin-top:14px;font-weight:600;font-size:14px}
.analyze-btn{margin-top:18px;width:100%;padding:14px;border:none;border-radius:12px;background:var(--green-deep);color:#fff;font-family:'Fraunces',serif;font-size:16px;font-weight:700;cursor:pointer}
.badge{font-size:12px;padding:5px 10px;border-radius:999px;font-weight:700}
.badge.ok{background:rgba(59,107,62,.15);color:var(--green-deep)}
.badge.warn{background:rgba(181,83,60,.15);color:var(--rust)}
.confbar{height:8px;border-radius:99px;background:var(--line);margin:12px 0 4px;overflow:hidden}
.confbar div{height:100%;background:var(--green)}
.confbar.warn div{background:var(--rust)}
.expert-card{margin-top:14px;padding:14px;border-radius:12px;border:1px solid rgba(181,83,60,.3);background:rgba(181,83,60,.07)}
.expert-card a{display:inline-block;margin-top:6px;background:var(--rust);color:#fff;text-decoration:none;padding:8px 14px;border-radius:8px;font-size:14px;font-weight:700}
.disclaimer{font-size:12.5px;opacity:.65;margin-top:16px;border-top:1px solid var(--line);padding-top:12px}
footer{text-align:center;font-size:13px;opacity:.55;margin-top:20px}
</style></head><body>
<header>
  <span class="brand">🌿 Krushi Sakha</span>
  <span class="langsel">
    <form method="get" id="langform">
      <select name="lang" onchange="document.getElementById('langform').submit()">
        <option value="en" {{ 'selected' if lang=='en' }}>English</option>
        <option value="hi" {{ 'selected' if lang=='hi' }}>हिंदी</option>
        <option value="mr" {{ 'selected' if lang=='mr' }}>मराठी</option>
      </select>
    </form>
  </span>
</header>
<div class="wrap">
  <h1>{{ t.heroTitle }}</h1>
  <p class="lead">{{ t.heroLead }}</p><br>
  <span class="note">{{ t.heroNote }}</span>

  <form method="post" enctype="multipart/form-data">
    <input type="hidden" name="lang" value="{{ lang }}">
    <div class="panel">
      <h2>{{ t.stepCropTitle }}</h2>
      <p class="sub">{{ t.stepCropSub }}</p>
      <div class="row">
        {% for c in crop_order %}
        <input type="radio" name="crop" value="{{ c }}" id="crop_{{ c }}" {{ 'checked' if c==selected_crop }}>
        <label for="crop_{{ c }}" class="chip"><span class="emoji">{{ crop_emoji[c] }}</span>{{ t.crops[c] }}</label>
        {% endfor %}
      </div>
    </div>

    <div class="panel">
      <h2>{{ t.step1Title }}</h2>
      <p class="sub">{{ t.step1Sub }}</p>
      <div class="row">
        {% for s in sample_order %}
        <input type="radio" name="sample" value="{{ s }}" id="s_{{ s }}" {{ 'checked' if s==selected_sample }}>
        <label for="s_{{ s }}" class="chip"><span class="icon">{{ sample_icons[s]|safe }}</span>{{ t.samples[s] }}</label>
        {% endfor %}
      </div>
      <p class="divider">{{ t.orUpload }}</p>
      <input type="file" name="photo" accept="image/*">
    </div>

    <div class="panel">
      <h2>{{ t.step2Title }}</h2>
      <p class="sub">{{ t.step2Sub }}</p>
      <label class="field">{{ t.rainfallLabel }}</label>
      <select name="rainfall">
        {% for k,v in t.rain.items() %}<option value="{{ k }}" {{ 'selected' if k==selected_rainfall }}>{{ v }}</option>{% endfor %}
      </select>
      <label class="field">{{ t.humidityLabel }}</label>
      <input type="number" name="humidity" min="10" max="95" value="{{ selected_humidity }}">
      <label class="field">{{ t.symptomsLabel }}</label>
      <div class="row">
        {% for k,v in t.chips.items() %}
        <input type="checkbox" name="symptoms" value="{{ k }}" id="sym_{{ k }}" {{ 'checked' if k in selected_symptoms }}>
        <label for="sym_{{ k }}" class="chip">{{ v }}</label>
        {% endfor %}
      </div>
      <button type="submit" class="analyze-btn">{{ t.analyze }}</button>
    </div>
  </form>

  {% if result %}
  <div class="panel">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">
      <h2>{{ result.name }}</h2>
      <span class="badge {{ 'warn' if result.needs_expert else 'ok' }}">{{ t.badgeWarn if result.needs_expert else t.badgeOk }}</span>
    </div>
    <div class="confbar {{ 'warn' if result.needs_expert else '' }}"><div style="width:{{ result.confidence }}%"></div></div>
    <p class="sub">{{ t.confidence }}: {{ result.confidence }}%</p>
    <p>{{ result.explain }}</p>
    <p class="sub" style="margin-top:12px;font-weight:600">{{ t.actionsWarn if result.needs_expert else t.actionsDefault }}</p>
    <ul>{% for a in result.actions %}<li>{{ a }}</li>{% endfor %}</ul>
    {% if result.needs_expert %}
    <div class="expert-card">
      <p style="font-weight:700">{{ expert.name }}</p>
      <p class="sub">{{ t.expertRole }}</p>
      <p>{{ t.expertNote }}</p>
      <a href="tel:{{ expert.phone }}">{{ t.callBtn }} {{ expert.phone_display }}</a>
    </div>
    {% endif %}
    <p class="disclaimer">{{ t.disclaimer }}</p>
  </div>
  {% endif %}
  <footer>{{ t.footer }}</footer>
</div>
</body></html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.values.get("lang", "en")
    if lang not in I18N:
        lang = "en"
    t = I18N[lang]

    selected_crop = request.form.get("crop", "tomato")
    selected_sample = request.form.get("sample", "nutrient")
    selected_rainfall = request.form.get("rainfall", "normal")
    selected_humidity = request.form.get("humidity", "55")
    selected_symptoms = set(request.form.getlist("symptoms"))

    result = None
    if request.method == "POST":
        photo = request.files.get("photo")
        ctx = {"rainfall": selected_rainfall, "humidity": int(selected_humidity or 55),
               "symptoms": selected_symptoms}
        if photo and photo.filename:
            v = analyze_image(photo.read())
        else:
            v = SAMPLE_VISUAL[selected_sample]
        cause_key, confidence, needs_expert = score_causes(v, ctx)
        info = t["causes"][cause_key]
        rl = t["rainCtx"][ctx["rainfall"]]
        result = {"name": info["name"], "confidence": round(confidence * 100),
                   "explain": info["explain"](ctx, rl), "actions": info["actions"],
                   "needs_expert": needs_expert}

    sample_icons = {s: leaf_svg(SAMPLE_FILL[s], SAMPLE_OVERLAY.get(s)) for s in SAMPLE_ORDER}

    return render_template_string(PAGE, lang=lang, t=t, result=result, expert=EXPERT,
                                   crop_order=CROP_ORDER, crop_emoji=CROP_EMOJI,
                                   sample_order=SAMPLE_ORDER, sample_icons=sample_icons,
                                   selected_crop=selected_crop, selected_sample=selected_sample,
                                   selected_rainfall=selected_rainfall, selected_humidity=selected_humidity,
                                   selected_symptoms=selected_symptoms)

if __name__ == "__main__":
    app.run(debug=True)
