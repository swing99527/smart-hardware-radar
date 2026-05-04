import base64
import hashlib
import http.client
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import l0_trend_engine
import market_thesis_engine

ROOT = SCRIPT_DIR.parent
CAT_FILE = ROOT / "data" / "categories.json"
SIGNAL_FILE = ROOT / "data" / "signals.json"
WATCH_TOPICS_FILE = ROOT / "data" / "watch_topics.json"
SOURCE_HEALTH_FILE = ROOT / "data" / "source_health.json"
TREND_RUN_FILE = ROOT / "data" / "trend_runs.json"
TREND_CLUSTER_FILE = ROOT / "data" / "trend_clusters.json"
MARKET_THESIS_FILE = ROOT / "data" / "market_theses.json"
METHODOLOGY_VERSION = "1.0"
REDDIT_TOKEN_CACHE = {"access_token": None, "expires_at": datetime.min}

GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS = [
    "stream deck",
    "zsa",
    "moonlander",
    "keychron",
    "wooting",
    "loupedeck",
    "work louder",
    "charachorder",
    "naya",
    "glove80",
    "qmk",
    "zmk",
    "split keyboard",
    "ergonomic keyboard",
    "mechanical keyboard",
    "programmable keyboard",
    "macro pad",
    "macropad",
    "modular keyboard",
    "creative console",
    "control console",
    "hall effect keyboard",
    "magnetic switch keyboard",
]

FEEDS = [
    {"name": "Product Hunt", "url": "https://www.producthunt.com/feed", "source_type": "product_launch", "source_language": "en"},
    {"name": "Kickstarter Tech", "url": "https://www.kickstarter.com/projects/feed.atom?category_id=16", "source_type": "crowdfunding", "source_language": "en"},
    {"name": "Kickstarter Design", "url": "https://www.kickstarter.com/projects/feed.atom?category_id=7", "source_type": "crowdfunding", "source_language": "en"},
    {"name": "Hacker News Show", "url": "https://news.ycombinator.com/showrss", "source_type": "community", "source_language": "en"},
    {"name": "Yanko Design", "url": "https://www.yankodesign.com/feed/", "source_type": "media", "source_language": "en"},
    {"name": "TechCrunch Hardware", "url": "https://techcrunch.com/category/hardware/feed/", "source_type": "media", "source_language": "en"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "source_type": "media", "source_language": "en"},
    {"name": "Engadget", "url": "https://www.engadget.com/rss.xml", "source_type": "media", "source_language": "en"},
    {
        "name": "Gizmodo",
        "url": "https://news.google.com/rss/search?q=site%3Agizmodo.com+%28gadget+OR+hardware+OR+smart+device+OR+robot+OR+wearable%29&hl=en-US&gl=US&ceid=US%3Aen",
        "source_type": "media",
        "source_language": "en",
    },
    {
        "name": "OpenClaw Hardware News",
        "url": "https://news.google.com/rss/search?q=%28OpenClaw+OR+%22Open+Claw%22%29+%28hardware+OR+camera+OR+robot+OR+%22edge+device%22+OR+keyboard+OR+recorder+OR+%22local+device%22+OR+%22terminal+box%22%29&hl=en-US&gl=US&ceid=US%3Aen",
        "source_type": "media",
        "source_language": "en",
        "candidate_category": "OpenClaw Hardware Bridge",
        "category_eligible": False,
        "extraction_engine": "QUERY",
    },
    {
        "name": "Agentic Edge Hardware News",
        "url": "https://news.google.com/rss/search?q=%28%22local+AI+agent%22+OR+%22edge+AI%22+OR+%22on-device+AI%22+OR+%22AI+agent%22+OR+MCP+OR+%22home+assistant%22%29+%28camera+OR+robot+OR+keyboard+OR+recorder+OR+microphone+OR+sensor+OR+%22edge+device%22+OR+%22AI+box%22+OR+gateway+OR+Jetson+OR+Hailo+OR+RK3588+OR+%22Ryzen+AI%22%29&hl=en-US&gl=US&ceid=US%3Aen",
        "source_type": "media",
        "source_language": "en",
        "candidate_category": "Agentic Edge Hardware",
        "category_eligible": False,
        "extraction_engine": "QUERY",
    },
    {
        "name": "Geek AI Productivity Hardware News",
        "url": "https://news.google.com/rss/search?q=%28%22Stream+Deck%22+OR+%22ZSA+Moonlander%22+OR+Keychron+OR+Wooting+OR+Loupedeck+OR+%22Work+Louder%22+OR+CharaChorder+OR+Glove80+OR+%22Naya+keyboard%22+OR+QMK+OR+ZMK+OR+VIA%29+%28keyboard+OR+macropad+OR+%22macro+pad%22+OR+%22creative+console%22+OR+%22control+console%22+OR+%22programmable+keyboard%22+OR+%22AI+workflow%22%29&hl=en-US&gl=US&ceid=US%3Aen",
        "source_type": "media",
        "source_language": "en",
        "candidate_category": "Geek AI Productivity Hardware",
        "category_eligible": False,
        "extraction_engine": "QUERY",
        "required_keywords": GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS,
    },
    {
        "name": "Kickstarter Geek Productivity Hardware",
        "url": "https://news.google.com/rss/search?q=site%3Akickstarter.com%2Fprojects+%28%22split+keyboard%22+OR+%22macro+pad%22+OR+macropad+OR+%22modular+keyboard%22+OR+%22creative+console%22+OR+%22programmable+keyboard%22%29&hl=en-US&gl=US&ceid=US%3Aen",
        "source_type": "crowdfunding",
        "source_language": "en",
        "candidate_category": "Geek AI Productivity Hardware",
        "category_eligible": False,
        "extraction_engine": "QUERY",
        "required_keywords": GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS,
    },
    {
        "name": "Indiegogo Geek Productivity Hardware",
        "url": "https://news.google.com/rss/search?q=site%3Aindiegogo.com%2Fprojects+%28%22split+keyboard%22+OR+%22macro+pad%22+OR+macropad+OR+%22modular+keyboard%22+OR+%22creative+console%22+OR+%22programmable+keyboard%22+OR+%22AI+gadget%22%29&hl=en-US&gl=US&ceid=US%3Aen",
        "source_type": "crowdfunding",
        "source_language": "en",
        "candidate_category": "Geek AI Productivity Hardware",
        "category_eligible": False,
        "extraction_engine": "QUERY",
        "required_keywords": GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS,
    },
    {"name": "SlashGear", "url": "https://www.slashgear.com/feed/", "source_type": "media", "source_language": "en"},
]

PRODUCT_REFERENCE_SOURCES = [
    {
        "name": "Elgato Stream Deck",
        "url": "https://www.elgato.com/us/en/s/welcome-to-stream-deck",
        "title": "Elgato Stream Deck programmable workflow controller with plugin marketplace",
    },
    {
        "name": "ZSA Moonlander",
        "url": "https://www.zsa.io/moonlander",
        "title": "ZSA Moonlander high-end split ergonomic programmable keyboard",
    },
    {
        "name": "Keychron",
        "url": "https://www.keychron.com",
        "title": "Keychron global DTC mechanical keyboard brand with QMK and VIA programmable keyboards",
    },
    {
        "name": "Wooting",
        "url": "https://wooting.io",
        "title": "Wooting high-end analog magnetic switch gaming keyboard",
    },
    {
        "name": "Loupedeck",
        "url": "https://loupedeck.com",
        "title": "Loupedeck creative control console for creator workflows",
    },
    {
        "name": "Work Louder",
        "url": "https://worklouder.cc",
        "title": "Work Louder creator keyboard and workflow controller hardware",
    },
    {
        "name": "CharaChorder",
        "url": "https://www.charachorder.com",
        "title": "CharaChorder high-speed text input keyboard device",
    },
    {
        "name": "Naya",
        "url": "https://naya.tech",
        "title": "Naya modular ergonomic keyboard and productivity controller",
    },
    {
        "name": "Glove80",
        "url": "https://www.moergo.com",
        "title": "Glove80 wireless split ergonomic keyboard",
    },
]

JSON_SOURCES = [
    {
        "name": "Indiegogo Tech",
        "url": "https://www.indiegogo.com/api/public/projects/getActiveCrowdfundingProjects",
        "source_type": "crowdfunding",
        "source_language": "en",
    },
]

CHINESE_FEEDS = [
    {"name": "少数派", "url": "https://sspai.com/feed", "source_type": "media", "source_language": "zh"},
    {"name": "36氪", "url": "https://36kr.com/feed", "source_type": "media", "source_language": "zh"},
]

REDDIT_SOURCES = [
    {"name": "Reddit r/gadgets", "url": "https://www.reddit.com/r/gadgets/top.json?t=week&limit=50"},
    {"name": "Reddit r/hardware", "url": "https://www.reddit.com/r/hardware/top.json?t=week&limit=50"},
    {"name": "Reddit r/smarthome", "url": "https://www.reddit.com/r/smarthome/top.json?t=week&limit=50"},
    {"name": "Reddit r/wearabletech", "url": "https://www.reddit.com/r/wearabletech/top.json?t=month&limit=50"},
    {"name": "Reddit r/MechanicalKeyboards", "url": "https://www.reddit.com/r/MechanicalKeyboards/top.json?t=week&limit=50"},
    {"name": "Reddit r/ErgoMechKeyboards", "url": "https://www.reddit.com/r/ErgoMechKeyboards/top.json?t=month&limit=50"},
    {"name": "Reddit r/olkb", "url": "https://www.reddit.com/r/olkb/top.json?t=month&limit=50"},
    {"name": "Reddit r/Workspaces", "url": "https://www.reddit.com/r/Workspaces/top.json?t=week&limit=50"},
    {"name": "Reddit r/unixporn", "url": "https://www.reddit.com/r/unixporn/top.json?t=week&limit=50"},
]

REDDIT_SEARCH_SOURCES = [
    {
        "name": "Reddit OpenClaw Hardware Search",
        "url": "https://www.reddit.com/search.json?q=%28openclaw+OR+%22open+claw%22%29+%28hardware+OR+camera+OR+robot+OR+%22edge+device%22+OR+keyboard+OR+recorder+OR+%22local+device%22+OR+%22terminal+box%22%29&sort=new&t=month&limit=50",
        "source_language": "en",
        "min_score": 1,
        "min_comments": 1,
        "candidate_category": "OpenClaw Hardware Bridge",
        "category_eligible": False,
        "extraction_engine": "QUERY",
    },
    {
        "name": "Reddit Agentic Edge Hardware Search",
        "url": "https://www.reddit.com/search.json?q=%28%22local+AI+agent%22+OR+%22edge+AI%22+OR+%22on-device+AI%22+OR+%22AI+agent%22+OR+MCP+OR+%22home+assistant%22%29+%28camera+OR+robot+OR+keyboard+OR+recorder+OR+microphone+OR+sensor+OR+%22edge+device%22+OR+%22AI+box%22+OR+gateway+OR+Jetson+OR+Hailo+OR+RK3588+OR+%22Ryzen+AI%22%29&sort=new&t=month&limit=50",
        "source_language": "en",
        "min_score": 1,
        "min_comments": 1,
        "candidate_category": "Agentic Edge Hardware",
        "category_eligible": False,
        "extraction_engine": "QUERY",
    },
    {
        "name": "Reddit Geek Productivity Hardware Search",
        "url": "https://www.reddit.com/search.json?q=%28%22stream+deck%22+OR+%22macro+pad%22+OR+macropad+OR+%22split+keyboard%22+OR+%22qmk%22+OR+%22zmk%22+OR+%22via%22+OR+%22loupedeck%22+OR+%22work+louder%22+OR+%22moonlander%22+OR+%22wooting%22+OR+%22glove80%22%29+%28workflow+OR+developer+OR+productivity+OR+coding+OR+AI+OR+setup%29&sort=new&t=month&limit=50",
        "source_language": "en",
        "min_score": 1,
        "min_comments": 1,
        "candidate_category": "Geek AI Productivity Hardware",
        "category_eligible": False,
        "extraction_engine": "QUERY",
        "required_keywords": GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS,
    },
]

GOOGLE_TRENDS_GEOS = [geo.strip().upper() for geo in os.getenv("GOOGLE_TRENDS_GEOS", "US").split(",") if geo.strip()]

REDDIT_MIN_SCORE = 50
REDDIT_MIN_COMMENTS = 10
GITHUB_MIN_STARS = 1000
GITHUB_TOOLCHAIN_MIN_STARS = int(os.getenv("GITHUB_TOOLCHAIN_MIN_STARS", "50"))
GITHUB_HARDWARE_BRIDGE_MIN_STARS = int(os.getenv("GITHUB_HARDWARE_BRIDGE_MIN_STARS", "10"))
GITHUB_AGENTIC_EDGE_MIN_STARS = int(os.getenv("GITHUB_AGENTIC_EDGE_MIN_STARS", "25"))
SOURCE_SCAN_LIMIT = int(os.getenv("SOURCE_SCAN_LIMIT", "120"))
SOURCE_SCAN_PER_SOURCE_LIMIT = int(os.getenv("SOURCE_SCAN_PER_SOURCE_LIMIT", "20"))
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")

TREND_TOPIC_PRIORITY = [
    "openclaw_hardware_bridge",
    "agentic_edge_hardware",
    "local_ai_box",
    "ai_camera_node",
    "ai_recorder",
    "geek_ai_productivity_hardware",
    "programmable_keyboard_ecosystem",
    "workflow_plugin_hardware",
    "ai_keyboard",
    "robot_agent_kit",
    "ai_devkit_peripheral",
    "hardware_intersections",
    "ai_coding_agent_ecosystem",
    "big_tech_peripherals",
    "ai_model_peripherals",
    "github_ai_projects",
]

HARDWARE_PATTERN = re.compile(
    r"(device|wearable|hardware|smart|ai|gadget|robot|camera|sensor|audio|tracker|monitor|"
    r"headphone|earbud|ring|glasses|keyboard|recorder|drone|speaker|charger|console|controller|macropad|"
    r"设备|硬件|智能|可穿戴|机器人|摄像头|相机|传感器|音频|耳机|戒指|眼镜|键盘|录音|"
    r"无人机|音箱|充电|门铃|门锁|显示器|监控|控制台|控制器|灯|净化器|冰箱|手表)",
    re.IGNORECASE,
)

NON_HARDWARE_PATTERN = re.compile(
    r"(book|documentary|software|platform|api|agent|agents|newsletter|movie|film|novel|"
    r"road trip|college radio|venture factory|secretary|religion|omnibus|lounge|"
    r"书|图书|纪录片|软件|平台|接口|代理|智能体|通讯|电影|影片|小说|电台|宗教|"
    r"晚报|早报|日报|融资|投资|立法|政策|法规|条例|大会|发布会|财报|股价|gdp)",
    re.IGNORECASE,
)

GENERIC_CATEGORIES = {
    "ai device",
    "ai gadget",
    "audio device",
    "camera",
    "device",
    "earbuds",
    "gadget",
    "hardware",
    "headphones",
    "humanoid robot",
    "robot",
    "robot mop",
    "sensor",
    "smart camera",
    "smart device",
    "smart gadget",
    "smart glasses",
    "ai glasses",
    "smart home device",
    "smart ring",
    "smart speaker",
    "smart watch",
    "smartphone",
    "smartwatch",
    "wearable",
    "wearable device",
    "ai设备",
    "ai硬件",
    "可穿戴",
    "可穿戴设备",
    "摄像头",
    "智能家居设备",
    "智能手表",
    "智能硬件",
    "智能设备",
    "智能眼镜",
    "机器人",
    "硬件",
    "设备",
    "音箱",
}

GENERIC_HEAD_NOUNS = {
    "camera",
    "console",
    "controller",
    "deadbolt",
    "deck",
    "device",
    "doorbell",
    "drone",
    "earbuds",
    "fan",
    "fridge",
    "gadget",
    "glasses",
    "headphones",
    "keyboard",
    "light",
    "lighting",
    "lock",
    "monitor",
    "pad",
    "macropad",
    "recorder",
    "ring",
    "robot",
    "sensor",
    "shade",
    "shades",
    "speaker",
    "tracker",
    "wearable",
}

QUALIFIER_WORDS = {
    "ai",
    "baby",
    "bike",
    "cycling",
    "creative",
    "desk",
    "developer",
    "dictation",
    "dog",
    "elder",
    "fitness",
    "gaming",
    "health",
    "hearing",
    "home",
    "kids",
    "local",
    "macro",
    "meeting",
    "modular",
    "outdoor",
    "pet",
    "posture",
    "programmable",
    "recording",
    "remote",
    "sleep",
    "smart",
    "translation",
    "vacuum",
    "video",
    "wireless",
    "workout",
    "workflow",
}

CHINESE_HEAD_NOUNS = {
    "摄像头",
    "相机",
    "监控",
    "门锁",
    "门铃",
    "锁",
    "录音笔",
    "录音设备",
    "记录仪",
    "传感器",
    "耳机",
    "音箱",
    "键盘",
    "控制台",
    "控制器",
    "显示器",
    "机器人",
    "手表",
    "戒指",
    "眼镜",
    "充电器",
    "净化器",
    "冰箱",
    "灯",
    "灯具",
    "窗帘",
    "风扇",
    "设备",
}

CHINESE_QUALIFIER_WORDS = {
    "ai",
    "智能",
    "户外",
    "室外",
    "本地",
    "无订阅",
    "会议",
    "语音",
    "听写",
    "宠物",
    "健康",
    "睡眠",
    "翻译",
    "游戏",
    "无线",
    "可编程",
    "分体",
    "人体工学",
    "开发者",
    "创作者",
    "家用",
    "家居",
    "安防",
    "儿童",
    "老人",
    "运动",
    "远程",
    "低功耗",
    "端侧",
    "边缘",
    "视觉",
}

BEHAVIOR_SOURCE_TYPES = {"crowdfunding", "product_launch", "product_reference", "community", "developer", "marketplace", "search"}
SOURCE_QUALITY = {
    "media": 1,
    "community": 2,
    "developer": 2,
    "product_reference": 2,
    "product_launch": 3,
    "crowdfunding": 4,
    "marketplace": 5,
    "search": 5,
}

CATEGORY_CLUSTER_RULES = [
    {
        "key": "smart_home_security",
        "name_en": "Smart Home Security Device",
        "name_zh": "智能家居安防设备",
        "keywords": [
            "doorbell",
            "deadbolt",
            "smart lock",
            "lock",
            "outdoor camera",
            "security camera",
            "local recording",
            "mechanical chime",
            "智能门锁",
            "门锁",
            "智能门铃",
            "门铃",
            "户外摄像头",
            "室外摄像头",
            "安防摄像头",
            "本地录像",
            "无订阅",
        ],
    },
    {
        "key": "ai_voice_capture",
        "name_en": "AI Voice Capture Device",
        "name_zh": "AI语音采集设备",
        "keywords": [
            "meeting recorder",
            "voice recorder",
            "dictation device",
            "ai recorder",
            "transcription device",
            "会议记录仪",
            "ai录音笔",
            "录音笔",
            "听写设备",
            "语音记录",
        ],
    },
]


def github_sources():
    cutoff = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
    return [
        {
            "name": "GitHub Edge AI Camera",
            "query": f'"edge ai" camera stars:>{GITHUB_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Edge AI Camera",
            "category_eligible": False,
        },
        {
            "name": "GitHub Robotics AI Hardware",
            "query": f"robotics ai hardware stars:>{GITHUB_MIN_STARS} pushed:>{cutoff}",
            "candidate_category": "AI Robotics Hardware",
            "category_eligible": False,
        },
        {
            "name": "GitHub Wearable AI",
            "query": f'"wearable ai" stars:>{GITHUB_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "AI Wearable",
            "category_eligible": False,
        },
        {
            "name": "GitHub Voice AI Device",
            "query": f'"voice assistant" device ai stars:>{GITHUB_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Voice AI Device",
            "category_eligible": False,
        },
        {
            "name": "GitHub On Device AI",
            "query": f'"on-device ai" camera OR sensor stars:>{GITHUB_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "On Device AI Project",
            "category_eligible": False,
        },
        {
            "name": "GitHub OpenClaw Ecosystem",
            "query": f'openclaw OR "open claw" stars:>{GITHUB_TOOLCHAIN_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "AI Coding Agent Ecosystem",
            "category_eligible": False,
            "min_stars": GITHUB_TOOLCHAIN_MIN_STARS,
        },
        {
            "name": "GitHub Claude Code Ecosystem",
            "query": f'"claude code" OR claude-code stars:>{GITHUB_TOOLCHAIN_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "AI Coding Agent Ecosystem",
            "category_eligible": False,
            "min_stars": GITHUB_TOOLCHAIN_MIN_STARS,
        },
        {
            "name": "GitHub Codex Ecosystem",
            "query": f'"openai codex" OR "codex cli" stars:>{GITHUB_TOOLCHAIN_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "AI Coding Agent Ecosystem",
            "category_eligible": False,
            "min_stars": GITHUB_TOOLCHAIN_MIN_STARS,
        },
        {
            "name": "GitHub Gemini Code Ecosystem",
            "query": f'"gemini cli" OR "gemini code" OR "gemini code assist" stars:>{GITHUB_TOOLCHAIN_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "AI Coding Agent Ecosystem",
            "category_eligible": False,
            "min_stars": GITHUB_TOOLCHAIN_MIN_STARS,
        },
        {
            "name": "GitHub OpenClaw Hardware Bridge",
            "query": f'openclaw camera OR robot OR hardware OR "edge device" OR keyboard OR recorder stars:>{GITHUB_HARDWARE_BRIDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "OpenClaw Hardware Bridge",
            "category_eligible": False,
            "min_stars": GITHUB_HARDWARE_BRIDGE_MIN_STARS,
        },
        {
            "name": "GitHub OpenClaw Camera Node",
            "query": f'openclaw camera stars:>{GITHUB_HARDWARE_BRIDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "OpenClaw Hardware Bridge",
            "category_eligible": False,
            "min_stars": GITHUB_HARDWARE_BRIDGE_MIN_STARS,
        },
        {
            "name": "GitHub Agentic Edge Hardware",
            "query": f'"local AI agent" OR "edge AI" OR "on-device AI" camera OR robot OR keyboard OR recorder OR sensor OR gateway OR Jetson OR Hailo stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Agentic Edge Hardware",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
        },
        {
            "name": "GitHub Local AI Box",
            "query": f'"local AI" box OR gateway OR hub OR Jetson OR Hailo OR RK3588 OR "Ryzen AI" stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Local AI Box",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
        },
        {
            "name": "GitHub AI Camera Node",
            "query": f'"edge AI" camera OR "local AI camera" OR "RTSP AI" OR "ONVIF AI" stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "AI Camera Node",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
        },
        {
            "name": "GitHub AI Recorder Device",
            "query": f'"AI recorder" OR "local transcription" OR "offline speech" OR "Whisper device" stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "AI Recorder Device",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
        },
        {
            "name": "GitHub Robot Agent Kit",
            "query": f'"robot agent" OR "embodied AI" OR "robot controller" OR "local robot agent" stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Robot Agent Kit",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
        },
        {
            "name": "GitHub Programmable Keyboard Firmware",
            "query": f'"qmk firmware" OR "zmk firmware" OR "via keyboard" OR "keyboard firmware" stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Geek AI Productivity Hardware",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
            "required_keywords": GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS,
        },
        {
            "name": "GitHub Stream Deck Plugin Ecosystem",
            "query": f'"stream deck" plugin OR streamdeck plugin OR "stream deck sdk" stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Geek AI Productivity Hardware",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
            "required_keywords": GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS,
        },
        {
            "name": "GitHub AI Workflow Controller",
            "query": f'"claude code" OR "cursor" OR "codex" OR "copilot" "stream deck" OR macropad OR "macro pad" stars:>{GITHUB_AGENTIC_EDGE_MIN_STARS} pushed:>{cutoff}',
            "candidate_category": "Geek AI Productivity Hardware",
            "category_eligible": False,
            "min_stars": GITHUB_AGENTIC_EDGE_MIN_STARS,
            "required_keywords": GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS,
        },
    ]


def google_trends_sources():
    return [
        {
            "name": f"Google Trends {geo} Daily",
            "url": f"https://trends.google.com/trending/rss?geo={geo}&hl=en-US",
            "source_type": "search",
            "source_language": "en",
            "geo": geo,
        }
        for geo in GOOGLE_TRENDS_GEOS
    ]


def product_reference_items(observed_at):
    items = []
    health_entries = []
    for source in PRODUCT_REFERENCE_SOURCES:
        item = {
            "title": source["title"],
            "link": source["url"],
            "source_name": source["name"],
            "source_type": "product_reference",
            "source_language": "en",
            "candidate_category": "Geek AI Productivity Hardware",
            "category_eligible": False,
            "extraction_engine": "SOURCE_REFERENCE",
            "metrics": {"reference_kind": "first_party_product_site"},
            "tags": ["first_party_product_reference"],
        }
        items.append(item)
        health_entries.append(
            source_health_entry(
                {"name": source["name"], "source_type": "product_reference", "source_language": "en"},
                source["url"],
                observed_at,
                "ok",
                item_count=1,
            )
        )
    return items, health_entries


def read_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        print(f"    [!] {path.name} is corrupted; using empty default.")
        return default


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def utc_parse(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def has_cjk(value):
    return bool(CJK_PATTERN.search(value or ""))


def normalize_text(value):
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", (value or "").lower()).strip()


def compact_text(value):
    return normalize_text(value).replace(" ", "")


def contains_any(value, keywords):
    compacted = compact_text(value)
    return any(compact_text(keyword) in compacted for keyword in keywords)


def contains_required_keyword(value, keywords):
    normalized = normalize_text(value)
    compacted = compact_text(value)
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if not normalized_keyword:
            continue
        if len(normalized_keyword) <= 3:
            if re.search(rf"(^|\s){re.escape(normalized_keyword)}($|\s)", normalized):
                return True
            continue
        if compact_text(keyword) in compacted:
            return True
    return False


def format_category(category):
    category = re.sub(r"\s+", " ", (category or "").strip(" \"'."))
    if has_cjk(category):
        return category
    acronyms = {"ai", "ar", "vr", "npu", "pcba", "usb"}
    return " ".join(word.upper() if word.lower() in acronyms else word.capitalize() for word in category.split())


def load_watch_topics():
    return read_json(WATCH_TOPICS_FILE, {"schema_version": "1.0", "topics": []}).get("topics", [])


def match_watch_topics(text, topics):
    matched = []
    for topic in topics:
        topic_id = topic.get("id")
        keywords = topic.get("keywords", [])
        if topic_id and contains_any(text, keywords):
            matched.append(topic_id)
    return matched


def signal_key(item):
    raw = item.get("link") or item.get("title", "")
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def source_health_entry(source, url, observed_at, status, http_status=None, error=None, rate_limit=None, item_count=0):
    return {
        "source_name": source.get("name", url),
        "source_type": source.get("source_type", "unknown"),
        "source_language": source.get("source_language", "unknown"),
        "auth_mode": source.get("auth_mode", "none"),
        "url": url,
        "query": source.get("query"),
        "status": status,
        "http_status": http_status,
        "error": str(error)[:300] if error else None,
        "rate_limit": rate_limit or {},
        "item_count": item_count,
        "checked_at": observed_at,
    }


def rate_limit_headers(response):
    return {
        key: response.headers.get(key)
        for key in ("x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset", "retry-after")
        if response.headers.get(key) is not None
    }


def github_auth_headers():
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        return {}
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def reddit_user_agent():
    return os.getenv("REDDIT_USER_AGENT", "smart-hardware-radar/1.0 by data-scout")


def reddit_oauth_url(url):
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse(
        ("https", "oauth.reddit.com", parsed.path, parsed.params, parsed.query, parsed.fragment)
    )


def reddit_access_token():
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None

    now = datetime.utcnow()
    cached_token = REDDIT_TOKEN_CACHE.get("access_token")
    cached_expiry = REDDIT_TOKEN_CACHE.get("expires_at") or datetime.min
    if cached_token and cached_expiry > now + timedelta(seconds=30):
        return cached_token

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    headers = {
        "Authorization": f"Basic {auth}",
        "User-Agent": reddit_user_agent(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, http.client.RemoteDisconnected, json.JSONDecodeError) as e:
        print(f"[!] Error fetching Reddit OAuth token: {e}")
        return None

    token = payload.get("access_token")
    expires_in = int(payload.get("expires_in") or 3600)
    if not token:
        return None
    REDDIT_TOKEN_CACHE["access_token"] = token
    REDDIT_TOKEN_CACHE["expires_at"] = now + timedelta(seconds=max(expires_in - 60, 60))
    return token


def update_source_health_doc(health_doc, entries):
    sources = health_doc.setdefault("sources", [])
    existing = {(source.get("source_name"), source.get("url"), source.get("query")): source for source in sources}
    current_keys = {(entry.get("source_name"), entry.get("url"), entry.get("query")) for entry in entries}
    current_names = {entry.get("source_name") for entry in entries}
    existing = {
        key: source
        for key, source in existing.items()
        if key in current_keys or source.get("source_name") not in current_names
    }

    for entry in entries:
        key = (entry.get("source_name"), entry.get("url"), entry.get("query"))
        previous = existing.get(key, {})
        if entry["status"] in {"ok", "fetch_ok_zero_items"}:
            entry["last_success_at"] = entry["checked_at"]
        else:
            entry["last_success_at"] = previous.get("last_success_at")
        existing[key] = {**previous, **entry}

    health_doc["sources"] = sorted(existing.values(), key=lambda source: source.get("source_name", ""))
    health_doc["methodology_version"] = METHODOLOGY_VERSION
    return health_doc


def fetch_rss(url, source=None, observed_at=None):
    source = source or {"name": url, "source_type": "unknown"}
    observed_at = observed_at or datetime.now().isoformat() + "Z"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read()
            health = source_health_entry(source, url, observed_at, "ok", getattr(response, "status", None), rate_limit=rate_limit_headers(response))
            return body, health
    except (urllib.error.URLError, TimeoutError, http.client.RemoteDisconnected) as e:
        print(f"[!] Error fetching {url}: {e}")
        http_status = getattr(e, "code", None)
        headers = getattr(e, "headers", None)
        rate_limit = {key: headers.get(key) for key in ("x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset", "retry-after") if headers and headers.get(key)}
        return None, source_health_entry(source, url, observed_at, "error", http_status, e, rate_limit)


def fetch_json(url, source=None, observed_at=None, extra_headers=None):
    source = source or {"name": url, "source_type": "unknown"}
    observed_at = observed_at or datetime.now().isoformat() + "Z"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; smart-hardware-radar/1.0; source-linked-signal-scout)",
            "Accept": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            health = source_health_entry(source, url, observed_at, "ok", getattr(response, "status", None), rate_limit=rate_limit_headers(response))
            return payload, health
    except (urllib.error.URLError, TimeoutError, http.client.RemoteDisconnected, json.JSONDecodeError) as e:
        print(f"[!] Error fetching JSON {url}: {e}")
        http_status = getattr(e, "code", None)
        headers = getattr(e, "headers", None)
        rate_limit = {key: headers.get(key) for key in ("x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset", "retry-after") if headers and headers.get(key)}
        return None, source_health_entry(source, url, observed_at, "error", http_status, e, rate_limit)


def fetch_github_search(source, observed_at):
    encoded = urllib.parse.quote(source["query"])
    url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page=10"
    auth_headers = github_auth_headers()
    auth_mode = "token" if auth_headers else "anonymous"
    github_source = {**source, "source_type": "developer", "auth_mode": auth_mode}
    return fetch_json(url, github_source, observed_at, auth_headers)


def fetch_reddit_json(source, observed_at):
    token = reddit_access_token()
    if token:
        reddit_source = {**source, "source_type": "community", "auth_mode": "reddit_oauth"}
        return fetch_json(
            reddit_oauth_url(source["url"]),
            reddit_source,
            observed_at,
            {"Authorization": f"Bearer {token}", "User-Agent": reddit_user_agent()},
        )

    reddit_source = {**source, "source_type": "community", "auth_mode": "public_json"}
    return fetch_json(source["url"], reddit_source, observed_at, {"User-Agent": reddit_user_agent()})


def parse_feed(xml_data, feed):
    items = []
    if not xml_data:
        return items, None
    try:
        root = ET.fromstring(xml_data)
        ns_atom = {"atom": "http://www.w3.org/2005/Atom"}

        entries = root.findall("atom:entry", ns_atom)
        if entries:
            for entry in entries:
                title_node = entry.find("atom:title", ns_atom)
                link_node = entry.find("atom:link", ns_atom)
                title = title_node.text if title_node is not None else ""
                link = link_node.attrib.get("href") if link_node is not None else ""
                append_hardware_item(items, title, link, feed)
        else:
            for item in root.findall(".//item"):
                title_node = item.find("title")
                link_node = item.find("link")
                title = title_node.text if title_node is not None else ""
                link = link_node.text if link_node is not None else ""
                append_hardware_item(items, title, link, feed)
    except ET.ParseError as e:
        print(f"    [!] Error parsing feed {feed['name']}: {e}")
        return items, e
    return items, None


def annotate_parse_health(health, items, parse_error=None):
    health["item_count"] = len(items)
    if health.get("status") != "ok":
        return health
    if parse_error:
        health["status"] = "fetch_ok_parse_failed"
        health["error"] = f"XML parse failed: {parse_error}"
    elif not items:
        health["status"] = "fetch_ok_zero_items"
        health["error"] = None
    return health


def parse_traffic_value(value):
    text = (value or "").lower().replace("+", "").replace(",", "").strip()
    if not text:
        return 0
    multiplier = 1
    if text.endswith("k"):
        multiplier = 1000
        text = text[:-1]
    elif text.endswith("m"):
        multiplier = 1000000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        digits = re.sub(r"[^0-9]", "", text)
        return int(digits) if digits else 0


def parse_google_trends_rss(xml_data, source):
    items = []
    if not xml_data:
        return items
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"    [!] Error parsing Google Trends {source['name']}: {e}")
        return items

    trends_namespaces = (
        "{https://trends.google.com/trending/rss}",
        "{https://trends.google.com/trends/trendingsearches/daily}",
    )
    for item in root.findall(".//item"):
        title_node = item.find("title")
        link_node = item.find("link")
        traffic_node = None
        picture_node = None
        news_titles = []
        news_urls = []
        for trends_ns in trends_namespaces:
            if traffic_node is None:
                traffic_node = item.find(f"{trends_ns}approx_traffic")
            if picture_node is None:
                picture_node = item.find(f"{trends_ns}picture")
            for news_item in item.findall(f"{trends_ns}news_item"):
                news_title_node = news_item.find(f"{trends_ns}news_item_title")
                news_url_node = news_item.find(f"{trends_ns}news_item_url")
                if news_title_node is not None and news_title_node.text:
                    news_titles.append(news_title_node.text.strip())
                if news_url_node is not None and news_url_node.text:
                    news_urls.append(news_url_node.text.strip())
            direct_news_title = item.find(f"{trends_ns}news_item_title")
            if direct_news_title is not None and direct_news_title.text:
                news_titles.append(direct_news_title.text.strip())

        query = title_node.text.strip() if title_node is not None and title_node.text else ""
        link = link_node.text.strip() if link_node is not None and link_node.text else ""
        news_title = next((title for title in news_titles if HARDWARE_PATTERN.search(title)), news_titles[0] if news_titles else "")
        combined = " ".join([query, " ".join(news_titles)])
        if not query or not HARDWARE_PATTERN.search(combined):
            continue

        signal_title = news_title if news_title and HARDWARE_PATTERN.search(news_title) else query
        items.append(
            {
                "title": signal_title,
                "link": news_urls[0] if news_urls else link or f"https://trends.google.com/trends/explore?geo={source['geo']}&q={urllib.parse.quote(query)}",
                "source_name": source["name"],
                "source_type": "search",
                "source_language": source.get("source_language", "en"),
                "metrics": {
                    "search_query": query,
                    "search_geo": source["geo"],
                    "google_trends_approx_traffic": traffic_node.text.strip() if traffic_node is not None and traffic_node.text else None,
                    "google_trends_traffic_value": parse_traffic_value(traffic_node.text if traffic_node is not None else None),
                    "google_trends_news_title": news_title,
                    "google_trends_news_titles": news_titles[:5],
                    "google_trends_picture": picture_node.text.strip() if picture_node is not None and picture_node.text else None,
                },
                "tags": ["google_trends_daily"],
            }
        )
    return items


def parse_github_repositories(payload, source):
    items = []
    if not payload:
        return items

    min_stars = int(source.get("min_stars") or GITHUB_MIN_STARS)
    for repo in payload.get("items", []):
        stars = int(repo.get("stargazers_count") or 0)
        if stars < min_stars:
            continue
        full_name = repo.get("full_name", "")
        description = repo.get("description") or ""
        html_url = repo.get("html_url") or ""
        if not full_name or not html_url:
            continue

        raw_text = f"{full_name} - {description}".strip(" -")
        if source.get("required_keywords") and not contains_required_keyword(raw_text, source["required_keywords"]):
            continue
        items.append(
            {
                "title": raw_text,
                "link": html_url,
                "source_name": source["name"],
                "source_type": "developer",
                "source_language": source.get("source_language", "en"),
                "candidate_category": source["candidate_category"],
                "category_eligible": source.get("category_eligible", False),
                "extraction_engine": "QUERY",
                "metrics": {
                    "github_stars": stars,
                    "github_forks": repo.get("forks_count"),
                    "github_open_issues": repo.get("open_issues_count"),
                    "github_language": repo.get("language"),
                    "github_pushed_at": repo.get("pushed_at"),
                    "github_topics": repo.get("topics", []),
                },
                "tags": ["github_repo"],
            }
        )
    return items


def parse_indiegogo_projects(payload, source):
    items = []
    if not payload:
        return items

    projects = payload if isinstance(payload, list) else payload.get("projects", [])
    for project in projects:
        if not isinstance(project, dict):
            continue
        title = (project.get("projectName") or "").strip()
        link = (project.get("projectHomeUrl") or "").strip()
        description = re.sub(r"\s+", " ", project.get("shortDescription") or "").strip()
        if not title or not link:
            continue

        raw_text = f"{title} - {description}".strip(" -")
        if not HARDWARE_PATTERN.search(raw_text) or NON_HARDWARE_PATTERN.search(raw_text):
            continue

        items.append(
            {
                "title": raw_text,
                "link": link,
                "source_name": source["name"],
                "source_type": "crowdfunding",
                "source_language": source.get("source_language", "en"),
                "metrics": {
                    "backers": int(project.get("backerCount") or 0),
                    "pledged_usd": float(project.get("fundsGathered") or 0),
                    "funding_goal": float(project.get("campaignGoal") or 0),
                    "currency": project.get("currencyShortName"),
                    "comments": int(project.get("commentCount") or 0),
                    "updates": int(project.get("updateCount") or 0),
                    "rewards": int(project.get("rewardCount") or 0),
                    "campaign_start": project.get("campaignStartDate"),
                    "campaign_end": project.get("campaignEndDate"),
                },
                "tags": ["indiegogo_project"],
            }
        )
    return items


def parse_reddit_listing(payload, source):
    items = []
    if not payload:
        return items

    min_score = int(source.get("min_score") if source.get("min_score") is not None else REDDIT_MIN_SCORE)
    min_comments = int(source.get("min_comments") if source.get("min_comments") is not None else REDDIT_MIN_COMMENTS)
    children = payload.get("data", {}).get("children", [])
    for child in children:
        post = child.get("data", {})
        title = post.get("title", "")
        score = int(post.get("score") or 0)
        comments = int(post.get("num_comments") or 0)
        if post.get("stickied") or post.get("over_18"):
            continue
        if score < min_score and comments < min_comments:
            continue
        if not title or not HARDWARE_PATTERN.search(title):
            continue
        if source.get("required_keywords") and not contains_required_keyword(title, source["required_keywords"]):
            continue

        permalink = post.get("permalink") or ""
        source_url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else post.get("url") or permalink
        item = {
            "title": title.strip(),
            "link": source_url,
            "source_name": source["name"],
            "source_type": "community",
            "source_language": source.get("source_language", "en"),
            "metrics": {
                "reddit_score": score,
                "reddit_comments": comments,
                "reddit_upvote_ratio": post.get("upvote_ratio"),
                "subreddit": post.get("subreddit"),
                "created_utc": post.get("created_utc"),
            },
            "tags": ["reddit_engagement"],
        }
        if source.get("candidate_category"):
            item["candidate_category"] = source["candidate_category"]
            item["category_eligible"] = source.get("category_eligible", False)
            item["extraction_engine"] = source.get("extraction_engine", "SOURCE_HINT")
        items.append(item)
    return items


def append_hardware_item(items, title, link, feed):
    if title and link and HARDWARE_PATTERN.search(title):
        if feed.get("required_keywords") and not contains_required_keyword(title, feed["required_keywords"]):
            return
        item = {
            "title": title.strip(),
            "link": link.strip(),
            "source_name": feed["name"],
            "source_type": feed["source_type"],
            "source_language": feed.get("source_language", "en"),
            "metrics": {},
            "tags": [],
        }
        if feed.get("candidate_category"):
            item["candidate_category"] = feed["candidate_category"]
            item["category_eligible"] = feed.get("category_eligible", False)
            item["extraction_engine"] = feed.get("extraction_engine", "SOURCE_HINT")
        items.append(item)


def parse_llm_json(content):
    text = (content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None

    decision = str(payload.get("decision", "")).lower().strip()
    confidence = payload.get("confidence", 0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0

    if decision == "reject":
        return {
            "decision": "reject",
            "category": None,
            "hardware_noun": None,
            "use_case": None,
            "confidence": max(0, min(1, confidence)),
            "reject_reason": str(payload.get("reject_reason", "rejected")).strip()[:160],
        }
    if decision != "accept":
        return None

    category = str(payload.get("category", "")).strip(" \"'.")
    words = normalize_text(category).split()
    if has_cjk(category):
        if len(compact_text(category)) < 2 or len(compact_text(category)) > 18:
            return None
    elif len(words) < 2 or len(words) > 5:
        return None

    return {
        "decision": "accept",
        "category": format_category(category),
        "hardware_noun": str(payload.get("hardware_noun", "")).strip().lower(),
        "use_case": str(payload.get("use_case", "")).strip(),
        "confidence": max(0, min(1, confidence)),
        "reject_reason": None,
    }


def llm_keyword_extraction(raw_title):
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
    if not base_url.endswith("/chat/completions"):
        base_url = base_url.rstrip("/") + "/chat/completions"

    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    prompt = f"""You are an expert hardware analyst.
Return ONLY strict JSON with these fields:
decision: "accept" or "reject"
category: a specific 2-to-5 word English or Chinese physical hardware category, or null
hardware_noun: the concrete device noun, or null
use_case: the concrete use case, user group, or functional qualifier, or null
confidence: number from 0 to 1
reject_reason: short reason when rejected, otherwise null

Reject broad mature categories such as Smartphone, Smartwatch, Smart Glasses, Robot, Camera, Wearable, or Device.
Reject software, APIs, newsletters, films, and generic AI projects.

Good category examples: "AI Meeting Recorder", "Pet Health Smart Collar", "Open Ear Sleep Headphones", "AI会议记录仪", "智能门锁"
Bad category examples: "Smart Glasses", "Smartphone", "Robot", "Wearable Device", "智能设备", "机器人"

Title: {json.dumps(raw_title)}
JSON:"""

    data = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 180}

    try:
        req = urllib.request.Request(base_url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return parse_llm_json(result["choices"][0]["message"]["content"])
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
        print(f"    [LLM API Error using {model_name} at {base_url}] {e}")
        return None


def heuristic_keyword_extraction(raw_title):
    parts = re.split(r"[:|\-\u2013\u2014]", raw_title)
    target_part = max(parts, key=len).strip()
    noise_words = [
        r"world'?s\s+first",
        r"ultimate",
        r"smartest",
        r"best",
        r"revolutionary",
        r"innovative",
        r"next[-\s]gen(eration)?",
        r"100%",
        r"kickstarter",
        r"indiegogo",
        r"introducing",
    ]
    for word in noise_words:
        target_part = re.sub(word, "", target_part, flags=re.IGNORECASE)
    target_part = re.sub(r"^[^\w\d]+|[^\w\d]+$", "", target_part).strip()
    if has_cjk(target_part):
        target_part = re.sub(r"\s+", "", target_part)
        if 2 <= len(target_part) <= 18:
            return target_part
        for noun in CHINESE_HEAD_NOUNS:
            index = target_part.find(noun)
            if index >= 0:
                start = max(0, index - 6)
                end = min(len(target_part), index + len(noun) + 4)
                return target_part[start:end]
        return target_part[:18]
    words = target_part.split()
    if len(words) > 6:
        hw_nouns = ["tracker", "monitor", "camera", "robot", "wearable", "headphones", "earbuds", "ring", "glasses", "device", "sensor", "recorder", "collar"]
        for i, word in enumerate(words):
            if word.lower() in hw_nouns:
                start = max(0, i - 3)
                return " ".join(words[start : i + 1]).title()
        return " ".join(words[:5]).title()
    if len(words) >= 2:
        return target_part.title()
    return None


def clean_title_hybrid(raw_title):
    extraction = llm_keyword_extraction(raw_title)
    if extraction:
        if extraction["decision"] == "reject":
            return None, "FILTERED", extraction
        return extraction["category"], "LLM", extraction
    kw = heuristic_keyword_extraction(raw_title)
    if kw:
        return kw, "NLP", None
    return None, None, None


def is_generic_category(category):
    normalized = normalize_text(category)
    words = normalized.split()
    compacted = compact_text(category)
    if normalized in GENERIC_CATEGORIES:
        return True
    if compacted in GENERIC_CATEGORIES:
        return True
    if has_cjk(category):
        if len(compacted) > 12:
            return True
        has_head = contains_any(category, CHINESE_HEAD_NOUNS)
        has_qualifier = contains_any(category, CHINESE_QUALIFIER_WORDS)
        if not has_head:
            return True
        if not has_qualifier and any(compacted == compact_text(noun) for noun in CHINESE_HEAD_NOUNS):
            return True
        return False
    if len(words) < 2 or len(words) > 5:
        return True
    if len(words) <= 2 and words[-1] in GENERIC_HEAD_NOUNS and not (set(words) & QUALIFIER_WORDS):
        return True
    return False


def is_specific_hardware_category(category):
    normalized = normalize_text(category)
    words = normalized.split()
    if is_generic_category(category):
        return False
    if "," in category:
        return False
    if NON_HARDWARE_PATTERN.search(category):
        return False
    if has_cjk(category):
        return contains_any(category, CHINESE_HEAD_NOUNS) and contains_any(category, CHINESE_QUALIFIER_WORDS)
    if not (set(words) & GENERIC_HEAD_NOUNS):
        return False
    if not (set(words) & QUALIFIER_WORDS):
        return False
    return True


def normalize_category_candidate(category):
    category = re.sub(r"^[A-Z][A-Za-z0-9]+[’'][sS]\s+", "", category or "").strip()
    category = re.sub(r"\s+", " ", category)
    category = re.sub(r"\b(with|without|that|works|like|for|and|or|the|a|an)\b", " ", category, flags=re.IGNORECASE)
    category = re.sub(r"\s+", " ", category).strip()
    if has_cjk(category):
        return re.sub(r"\s+", "", category)
    words = category.split()
    lower_words = [word.lower().strip(".,:;!?") for word in words]
    noun_index = None
    for index, word in enumerate(lower_words):
        if word in GENERIC_HEAD_NOUNS:
            noun_index = index
    if noun_index is not None:
        qualifier_indexes = [index for index, word in enumerate(lower_words) if word in QUALIFIER_WORDS]
        if qualifier_indexes:
            start = min(qualifier_indexes[0], noun_index)
            end = max(qualifier_indexes[-1], noun_index)
            return format_category(" ".join(words[start : end + 1]))
    return format_category(category)


def behavior_strength(source_type, metrics):
    if source_type == "community":
        comments = int(metrics.get("reddit_comments") or 0)
        score = int(metrics.get("reddit_score") or 0)
        if comments >= 50 or score >= 250:
            return 5
        if comments >= 20 or score >= 100:
            return 4
        if comments >= 10 or score >= 50:
            return 3
        return 1
    if source_type == "developer":
        stars = int(metrics.get("github_stars") or 0)
        if stars >= 10000:
            return 5
        if stars >= 3000:
            return 4
        if stars >= 1000:
            return 3
        return 1
    if source_type == "crowdfunding":
        backers = int(metrics.get("backers") or 0)
        pledged = float(metrics.get("pledged_usd") or 0)
        if backers >= 5000 or pledged >= 1000000:
            return 5
        if backers >= 1000 or pledged >= 250000:
            return 4
        if backers >= 100 or pledged >= 50000:
            return 3
        return 2
    if source_type == "search":
        traffic = int(metrics.get("google_trends_traffic_value") or 0)
        if traffic >= 100000:
            return 5
        if traffic >= 50000:
            return 4
        return 3
    if source_type == "product_reference":
        return 2
    if source_type in {"marketplace", "product_launch"}:
        return 3
    return 0


def specificity_score(category):
    if not is_specific_hardware_category(category):
        return 0
    if has_cjk(category):
        score = 1
        if contains_any(category, CHINESE_QUALIFIER_WORDS):
            score += 1
        if len(compact_text(category)) >= 4:
            score += 1
        return min(score, 3)
    words = normalize_text(category).split()
    score = 1
    if set(words) & QUALIFIER_WORDS:
        score += 1
    if len(words) >= 3:
        score += 1
    return min(score, 3)


def diffusion_stage_for_signal(source_type):
    if source_type in {"developer", "product_launch", "product_reference"}:
        return "innovator"
    if source_type == "community":
        return "early_adopter"
    if source_type == "media":
        return "opinion_leader"
    if source_type in {"marketplace", "search"}:
        return "early_majority"
    if source_type == "crowdfunding":
        return "early_adopter_paid"
    return "unknown"


def signal_strength_score(l0_scores):
    return round(
        l0_scores["source_quality"] * 0.25
        + l0_scores["behavior_strength"] * 0.35
        + l0_scores["specificity"] * 0.25
        + l0_scores["watch_relevance"] * 0.15,
        2,
    )


def l0_scores_for_signal(source_type, category, metrics, matched_watch_topics):
    scores = {
        "source_quality": SOURCE_QUALITY.get(source_type, 0),
        "behavior_strength": behavior_strength(source_type, metrics),
        "specificity": specificity_score(category),
        "watch_relevance": min(3, len(matched_watch_topics)),
        "diffusion_stage": diffusion_stage_for_signal(source_type),
    }
    scores["signal_strength"] = signal_strength_score(scores)
    return scores


def signal_from_item(item, category, engine, observed_at, watch_topics, extraction=None):
    tags = ["hardware_keyword_match"]
    for tag in item.get("tags", []):
        if tag not in tags:
            tags.append(tag)
    matched_watch_topics = match_watch_topics(
        " ".join(
            [
                item.get("title", ""),
                category,
                " ".join(str(topic) for topic in item.get("metrics", {}).get("github_topics", [])),
            ]
        ),
        watch_topics,
    )
    for topic in matched_watch_topics:
        tag = f"watch:{topic}"
        if tag not in tags:
            tags.append(tag)
    metrics = item.get("metrics", {})
    l0_scores = l0_scores_for_signal(item["source_type"], category, metrics, matched_watch_topics)
    return {
        "id": None,
        "source_type": item["source_type"],
        "source_language": item.get("source_language", "unknown"),
        "source_name": item["source_name"],
        "source_url": item["link"],
        "source_title": item["title"],
        "raw_text": item["title"],
        "observed_at": observed_at,
        "first_seen_at": observed_at,
        "last_seen_at": observed_at,
        "seen_count": 1,
        "candidate_category": category,
        "candidate_key": normalize_text(category),
        "category_eligible": item.get("category_eligible", True),
        "extraction_engine": engine,
        "extraction": extraction,
        "metrics": metrics,
        "tags": tags,
        "matched_watch_topics": matched_watch_topics,
        "l0_scores": l0_scores,
        "dedupe_key": signal_key(item),
    }


def next_signal_id(signals):
    max_id = 0
    for signal in signals:
        value = signal.get("id", "")
        if value.startswith("S") and value[1:].isdigit():
            max_id = max(max_id, int(value[1:]))
    return max_id + 1


def append_new_signals(signals_doc, candidates):
    signals = signals_doc.setdefault("signals", [])
    existing_by_key = {signal.get("dedupe_key"): signal for signal in signals}
    next_id = next_signal_id(signals)
    new_count = 0
    refreshed_count = 0

    for signal in candidates:
        existing = existing_by_key.get(signal["dedupe_key"])
        if existing:
            existing["last_seen_at"] = signal["last_seen_at"]
            existing["seen_count"] = int(existing.get("seen_count") or 1) + 1
            existing["metrics"] = signal.get("metrics", {})
            existing["source_title"] = signal.get("source_title", existing.get("source_title"))
            existing["raw_text"] = signal.get("raw_text", existing.get("raw_text"))
            existing["candidate_category"] = signal.get("candidate_category", existing.get("candidate_category"))
            existing["candidate_key"] = signal.get("candidate_key", existing.get("candidate_key"))
            existing["matched_watch_topics"] = signal.get("matched_watch_topics", [])
            existing["l0_scores"] = signal.get("l0_scores", {})
            existing["extraction"] = signal.get("extraction")
            existing["tags"] = sorted(set(existing.get("tags", [])) | set(signal.get("tags", [])))
            refreshed_count += 1
            continue
        signal["id"] = f"S{next_id:03d}"
        signals.append(signal)
        existing_by_key[signal["dedupe_key"]] = signal
        next_id += 1
        new_count += 1

    return new_count, refreshed_count


def normalize_signal_schema(signals_doc):
    for signal in signals_doc.setdefault("signals", []):
        observed_at = signal.get("observed_at")
        signal.setdefault("first_seen_at", observed_at)
        signal.setdefault("last_seen_at", observed_at)
        signal["seen_count"] = int(signal.get("seen_count") or 1)
        signal.setdefault("matched_watch_topics", [])
        signal.setdefault("tags", [])
        signal.setdefault("source_language", "unknown")
        signal.setdefault("gate_status", "watch_only" if signal.get("category_eligible") is False else "held")
        signal.setdefault("gate_reason", "watch_only_source" if signal.get("category_eligible") is False else "not_evaluated")


def prune_invalid_signals(signals_doc):
    signals = signals_doc.setdefault("signals", [])
    kept = []
    removed = 0
    for signal in signals:
        if (
            signal.get("category_eligible") is False
            and signal.get("candidate_category") == "Geek AI Productivity Hardware"
            and signal.get("source_type") != "product_reference"
            and not contains_required_keyword(signal.get("source_title", ""), GEEK_PRODUCTIVITY_REQUIRED_KEYWORDS)
        ):
            removed += 1
            continue
        if signal.get("category_eligible") is False:
            kept.append(signal)
            continue
        category = signal.get("candidate_category", "")
        if category and is_specific_hardware_category(category):
            kept.append(signal)
        else:
            removed += 1
    signals_doc["signals"] = kept
    return removed


def confidence_for(signals):
    source_types = {signal["source_type"] for signal in signals}
    behavior = any(signal["source_type"] in BEHAVIOR_SOURCE_TYPES for signal in signals)
    avg_strength = sum(signal.get("l0_scores", {}).get("signal_strength", 0) for signal in signals) / max(len(signals), 1)
    score = 0.4 + min(0.25, len(signals) * 0.08) + min(0.15, len(source_types) * 0.05) + min(0.15, avg_strength / 5 * 0.15)
    if behavior:
        score += 0.05
    return round(min(score, 0.95), 2)


def diffusion_stage_for_category(source_types):
    source_types = set(source_types)
    if {"media", "community"} <= source_types:
        return "two_step_confirmed"
    if ({"community", "search"} <= source_types) or ({"community", "marketplace"} <= source_types):
        return "demand_confirmed"
    if ({"developer", "media"} <= source_types) or ({"developer", "community"} <= source_types):
        return "innovator_to_early_adopter"
    if len(source_types) >= 3:
        return "cross_network_diffusion"
    if len(source_types) == 1:
        return "single_network_hold"
    return "multi_source_unclassified"


def l0_evidence_for_category(signals):
    source_types = sorted({signal["source_type"] for signal in signals})
    watch_topics = sorted({topic for signal in signals for topic in signal.get("matched_watch_topics", [])})
    candidate_keys = sorted({signal.get("candidate_key") for signal in signals if signal.get("candidate_key")})
    avg_strength = round(
        sum(signal.get("l0_scores", {}).get("signal_strength", 0) for signal in signals) / max(len(signals), 1),
        2,
    )
    return {
        "source_types": source_types,
        "cross_source_count": len(source_types),
        "has_behavior_source": any(signal["source_type"] in BEHAVIOR_SOURCE_TYPES for signal in signals),
        "diffusion_stage": diffusion_stage_for_category(source_types),
        "avg_signal_strength": avg_strength,
        "matched_watch_topics": watch_topics,
        "candidate_keys": candidate_keys,
        "l0_confidence": confidence_for(signals),
    }


def category_gate(signals):
    source_types = {signal["source_type"] for signal in signals}
    has_behavior = any(signal["source_type"] in BEHAVIOR_SOURCE_TYPES for signal in signals)
    if len(source_types) < 2:
        return False, "needs_two_independent_source_types"
    if not has_behavior:
        return False, "needs_behavior_source"
    return True, "passed"


def cluster_rule_for_signal(signal):
    text = normalize_text(
        " ".join(
            [
                signal.get("candidate_category", ""),
                signal.get("source_title", ""),
                str(signal.get("metrics", {}).get("subreddit", "")),
            ]
        )
    )
    for rule in CATEGORY_CLUSTER_RULES:
        if any(normalize_text(keyword) in text for keyword in rule["keywords"]):
            return rule
    return None


def cluster_key_for_signal(signal):
    rule = cluster_rule_for_signal(signal)
    if rule:
        return f"cluster:{rule['key']}"
    return signal.get("candidate_key")


def cluster_name_for_signals(cluster_key, signals):
    if cluster_key.startswith("cluster:"):
        rule_key = cluster_key.split(":", 1)[1]
        for rule in CATEGORY_CLUSTER_RULES:
            if rule["key"] == rule_key:
                return rule["name_en"]
    return max(
        signals,
        key=lambda signal: signal.get("l0_scores", {}).get("signal_strength", 0),
    )["candidate_category"]


def cluster_name_zh_for_key(cluster_key):
    if cluster_key.startswith("cluster:"):
        rule_key = cluster_key.split(":", 1)[1]
        for rule in CATEGORY_CLUSTER_RULES:
            if rule["key"] == rule_key:
                return rule.get("name_zh")
    return None


def build_categories_from_signals(cats_doc, signals_doc):
    signals_by_key = {}
    for signal in signals_doc.get("signals", []):
        signal["gate_status"] = "watch_only" if signal.get("category_eligible") is False else "held"
        signal["gate_reason"] = "watch_only_source" if signal.get("category_eligible") is False else "not_evaluated"
        signal["cluster_key"] = cluster_key_for_signal(signal) if signal.get("category_eligible") is not False else None
        signal["cluster_name"] = None
        if signal.get("category_eligible") is False:
            continue
        key = signal.get("cluster_key")
        if key:
            signal["cluster_name"] = cluster_name_for_signals(key, [signal])
            signals_by_key.setdefault(key, []).append(signal)

    existing_keys = {c.get("cluster_key") or normalize_text(c.get("name_en", "")) for c in cats_doc.get("categories", [])}
    next_id = len(cats_doc.get("categories", [])) + 1
    added = 0
    rejected = 0

    for key, signals in sorted(signals_by_key.items()):
        category_name = cluster_name_for_signals(key, signals)
        category_name_zh = cluster_name_zh_for_key(key)
        for signal in signals:
            signal["cluster_name"] = category_name
            if category_name_zh:
                signal["cluster_name_zh"] = category_name_zh
        if key in existing_keys:
            for signal in signals:
                signal["gate_status"] = "promoted"
                signal["gate_reason"] = "existing_category"
            continue
        if is_generic_category(category_name):
            rejected += 1
            for signal in signals:
                signal["gate_status"] = "rejected"
                signal["gate_reason"] = "generic_category"
            print(f"  [gate] rejected generic category: {category_name}")
            continue
        passed, reason = category_gate(signals)
        if not passed:
            rejected += 1
            for signal in signals:
                signal["gate_status"] = "held"
                signal["gate_reason"] = reason
            print(f"  [gate] waiting for more evidence: {category_name} ({reason})")
            continue

        source = signals[0]
        new_id = f"A{next_id:03d}"
        cats_doc.setdefault("categories", []).append(
            {
                "id": new_id,
                "name": f"【证据聚类】{category_name}",
                "name_en": category_name,
                "name_zh": category_name_zh,
                "cluster_key": key,
                "cluster_members": sorted({signal["candidate_category"] for signal in signals}),
                "source_title": source["source_title"],
                "source_url": source["source_url"],
                "evidence_signal_ids": [signal["id"] for signal in signals],
                "confidence": confidence_for(signals),
                "l0_evidence": l0_evidence_for_category(signals),
                "status": "scouted",
                "tags": ["Auto-Discovered", "Evidence-Gated"],
            }
        )
        for signal in signals:
            signal["gate_status"] = "promoted"
            signal["gate_reason"] = "passed"
        existing_keys.add(key)
        next_id += 1
        added += 1

    return added, rejected


def select_items_for_scan(items):
    groups = {}
    for item in items:
        key = item.get("source_name") or item.get("source_type") or "unknown"
        groups.setdefault(key, []).append(item)

    queues = [group[:SOURCE_SCAN_PER_SOURCE_LIMIT] for group in groups.values()]
    selected = []
    while len(selected) < SOURCE_SCAN_LIMIT and any(queues):
        for queue in queues:
            if queue and len(selected) < SOURCE_SCAN_LIMIT:
                selected.append(queue.pop(0))
    return selected


def trend_key_for_signal(signal):
    return l0_trend_engine.trend_key_for_signal(signal, TREND_TOPIC_PRIORITY, cluster_key_for_signal)


def trend_name_for_signals(trend_key, signals):
    return l0_trend_engine.trend_name_for_signals(trend_key, signals, cluster_name_for_signals)


def trend_status_for_cluster(cluster, previous_runs):
    return l0_trend_engine.trend_status_for_cluster(cluster, previous_runs, BEHAVIOR_SOURCE_TYPES)


def build_trend_clusters(signals_doc, trend_runs_doc, observed_at):
    return l0_trend_engine.build_trend_clusters(
        signals_doc,
        trend_runs_doc,
        observed_at,
        METHODOLOGY_VERSION,
        TREND_TOPIC_PRIORITY,
        BEHAVIOR_SOURCE_TYPES,
        cluster_key_for_signal,
        cluster_name_for_signals,
        cluster_name_zh_for_key,
    )


def main():
    observed_at = datetime.now().isoformat() + "Z"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] L0 Signal Scout Activated...")
    if os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"):
        print(f"  -> LLM cleaner connected ({os.getenv('LLM_MODEL', 'gpt-4o-mini')})")
    else:
        print("  -> No LLM_API_KEY found. Running in heuristic fallback mode.")

    raw_items = []
    source_health_entries = []
    reference_items, reference_health = product_reference_items(observed_at)
    raw_items.extend(reference_items)
    source_health_entries.extend(reference_health)
    for feed in FEEDS:
        xml, health = fetch_rss(feed["url"], feed, observed_at)
        items, parse_error = parse_feed(xml, feed)
        health = annotate_parse_health(health, items, parse_error)
        source_health_entries.append(health)
        raw_items.extend(items)
    for feed in CHINESE_FEEDS:
        xml, health = fetch_rss(feed["url"], feed, observed_at)
        items, parse_error = parse_feed(xml, feed)
        health = annotate_parse_health(health, items, parse_error)
        source_health_entries.append(health)
        raw_items.extend(items)
    for source in JSON_SOURCES:
        payload, health = fetch_json(source["url"], source, observed_at)
        items = parse_indiegogo_projects(payload, source)
        health["item_count"] = len(items)
        source_health_entries.append(health)
        raw_items.extend(items)
    for source in REDDIT_SOURCES:
        payload, health = fetch_reddit_json(source, observed_at)
        items = parse_reddit_listing(payload, source)
        health["item_count"] = len(items)
        source_health_entries.append(health)
        raw_items.extend(items)
    for source in REDDIT_SEARCH_SOURCES:
        payload, health = fetch_reddit_json(source, observed_at)
        items = parse_reddit_listing(payload, source)
        health["item_count"] = len(items)
        source_health_entries.append(health)
        raw_items.extend(items)
    for source in google_trends_sources():
        xml, health = fetch_rss(source["url"], source, observed_at)
        items = parse_google_trends_rss(xml, source)
        health["item_count"] = len(items)
        source_health_entries.append(health)
        raw_items.extend(items)
    for source in github_sources():
        payload, health = fetch_github_search(source, observed_at)
        items = parse_github_repositories(payload, source)
        health["item_count"] = len(items)
        source_health_entries.append(health)
        raw_items.extend(items)

    seen_keys = set()
    unique_items = []
    for item in raw_items:
        key = item.get("link") or item["title"]
        if key not in seen_keys:
            seen_keys.add(key)
            unique_items.append(item)

    items_for_scan = select_items_for_scan(unique_items)
    print(f"\nTotal source-linked hardware signals found today: {len(unique_items)}")
    print(f"Items selected for extraction after per-source quota: {len(items_for_scan)}")

    watch_topics = load_watch_topics()
    signal_candidates = []
    print("Running extraction and evidence gate...")
    for item in items_for_scan:
        title = item["title"]
        extraction = None
        if item.get("candidate_category"):
            category, engine = item["candidate_category"], item.get("extraction_engine", "SOURCE_HINT")
        else:
            category, engine, extraction = clean_title_hybrid(title)
        if engine == "FILTERED":
            print(f"  [filtered] '{title[:50]}...' -> not specific hardware")
            continue
        if not category:
            continue
        category_eligible = item.get("category_eligible", True)
        if category_eligible:
            category = normalize_category_candidate(category)
        else:
            category = re.sub(r"\s+", " ", category).strip()
        if category_eligible and not is_specific_hardware_category(category):
            print(f"  [low-quality] '{title[:50]}...' -> {category}")
            continue
        signal = signal_from_item(item, category, engine, observed_at, watch_topics, extraction)
        if not category_eligible and not signal["matched_watch_topics"]:
            print(f"  [low-quality] '{title[:50]}...' -> {category}")
            continue
        mode = "watch-only" if not category_eligible else engine
        print(f"  [{mode}] '{title[:50]}...' -> {category}")
        signal_candidates.append(signal)

    signals_doc = read_json(
        SIGNAL_FILE,
        {"schema_version": "1.0", "methodology_version": METHODOLOGY_VERSION, "signals": []},
    )
    signals_doc["methodology_version"] = METHODOLOGY_VERSION
    normalize_signal_schema(signals_doc)
    pruned_signals = prune_invalid_signals(signals_doc)
    new_signals, refreshed_signals = append_new_signals(signals_doc, signal_candidates)

    cats_doc = read_json(
        CAT_FILE,
        {"schema_version": "2.1", "methodology_version": METHODOLOGY_VERSION, "categories": []},
    )
    cats_doc["methodology_version"] = METHODOLOGY_VERSION
    added_categories, rejected_categories = build_categories_from_signals(cats_doc, signals_doc)
    trend_runs_doc = read_json(
        TREND_RUN_FILE,
        {"schema_version": "1.0", "methodology_version": METHODOLOGY_VERSION, "runs": []},
    )
    trend_clusters_doc, trend_runs_doc = build_trend_clusters(signals_doc, trend_runs_doc, observed_at)
    market_theses_doc = market_thesis_engine.build_market_theses(
        trend_clusters_doc,
        signals_doc,
        observed_at,
        METHODOLOGY_VERSION,
    )
    write_json(SIGNAL_FILE, signals_doc)
    write_json(CAT_FILE, cats_doc)
    write_json(TREND_CLUSTER_FILE, trend_clusters_doc)
    write_json(TREND_RUN_FILE, trend_runs_doc)
    write_json(MARKET_THESIS_FILE, market_theses_doc)

    health_doc = read_json(
        SOURCE_HEALTH_FILE,
        {"schema_version": "1.0", "methodology_version": METHODOLOGY_VERSION, "sources": []},
    )
    write_json(SOURCE_HEALTH_FILE, update_source_health_doc(health_doc, source_health_entries))

    print(f"\nSignals added: {new_signals}")
    print(f"Signals refreshed: {refreshed_signals}")
    print(f"Signals pruned: {pruned_signals}")
    print(f"Categories added: {added_categories}")
    print(f"Candidates held back by gate: {rejected_categories}")
    print(f"Trend clusters updated: {len(trend_clusters_doc.get('clusters', []))}")
    print(f"Market theses updated: {len(market_theses_doc.get('theses', []))}")


if __name__ == "__main__":
    main()
