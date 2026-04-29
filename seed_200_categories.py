import json
from pathlib import Path

ROOT = Path("/Users/chenshangwei/code/smart-hardware-radar")
CAT_FILE = ROOT / "data/categories.json"

# 严格按照 Amazon/Kickstarter 硬件叶子节点提取的 200 个实体智能硬件赛道
seed_list = [
    # --- 1. Smart Wearables (智能穿戴 & 柔性电子) ---
    "Smart Ring", "Smart Glasses", "Audio Sunglasses", "Smart Helmet", "Smart Insoles",
    "Heated Jacket", "Cooling Vest", "Smart Posture Corrector", "Smart Belt", "Heated Gloves",
    "Smart Socks", "Heated Knee Brace", "Smart Sleep Mask", "Smart Earplugs", "VR Headset",
    "AR Glasses", "Smart Contact Lenses", "Wearable Air Purifier", "Smart Jewelry", "Smart Backpack",
    "Wearable Camera", "Smart Motorcycle Helmet", "Smart Ski Helmet", "Heated Insoles", "Smart Cap",

    # --- 2. Smart Audio & Hearables (智能音频 & 辅听) ---
    "Open Ear Headphones", "Bone Conduction Headphones", "Sleep Earbuds", "OTC Hearing Aid",
    "Language Translator Earbuds", "AI Voice Recorder", "Podcast Microphone", "Conference Speakerphone",
    "Swim Headphones", "Gaming Earbuds", "ANC Earbuds", "Neckband Speaker", "Smart Metronome",
    "Baby Monitor Audio", "Smart Guitar Amp", "Smart Piano Amp", "Bone Conduction Pillow Speaker",
    "White Noise Machine", "Directional Speaker", "Voice Amplifier",

    # --- 3. Health & Bio-tracking (数字健康 & 康复理疗) ---
    "Radar Sleep Monitor", "Smart Anti-Snoring Device", "Smart CPAP Machine", "Smart Body Composition Scale",
    "Smart Blood Pressure Monitor", "Portable ECG Monitor", "Continuous Glucose Monitor", "Smart Pill Dispenser",
    "EMS Muscle Stimulator", "TENS Unit", "Smart Cupping Therapy", "Massage Gun", "Eye Massager",
    "Neck Massager", "Hand Massager", "Knee Massager", "Foot Massager", "Smart Heating Pad",
    "Smart Thermometer", "Smart Inhaler", "Posture Training Device", "Smart Hearing Protector",
    "Vaginal Rejuvenation Device", "Pelvic Floor Muscle Trainer", "Smart Kegel Exerciser",

    # --- 4. Pet Tech (宠物智能硬件) ---
    "Automatic Pet Feeder", "Smart Pet Water Fountain", "Self-Cleaning Litter Box", "GPS Pet Tracker",
    "Pet Camera with Treat Dispenser", "Interactive Pet Toy", "Automatic Ball Launcher", "Smart Dog Collar",
    "Bark Control Collar", "Pet Hair Dryer Box", "Smart Pet Door", "Pet Activity Tracker",
    "Microchip Pet Feeder", "Automatic Fish Feeder", "Smart Aquarium", "Reptile Smart Terrarium",
    "Dog Paw Cleaner", "Smart Pet Bed", "Pet Grooming Vacuum", "Smart Bird Feeder",

    # --- 5. Productivity & Desk (桌面办公 & 生产力) ---
    "eInk Calendar", "Smart Pomodoro Timer", "Smart Pen", "Translator Pen", "Smart Notebook",
    "Desktop Air Purifier", "Monitor Light Bar", "Ergonomic Split Keyboard", "Smart Standing Desk",
    "Under Desk Elliptical", "Under Desk Bike", "Smart Mug", "Temperature Control Coaster",
    "Wireless Charging Mouse Pad", "Desk Humidifier", "Smart Label Printer", "Portable Document Scanner",
    "Mini PC", "Docking Station with Screen", "Smart Whiteboard", "Time Tracker Cube",

    # --- 6. Beauty & Personal Care Tech (科技美护) ---
    "Laser Hair Removal Device", "RF Skin Tightening Device", "LED Therapy Mask", "Smart Mirror",
    "Sonic Facial Brush", "Heated Eyelash Curler", "Water Flosser", "Smart Electric Toothbrush",
    "Ionic Hair Dryer", "Automatic Hair Curler", "Blackhead Remover Vacuum", "Ultrasonic Skin Scrubber",
    "Smart Epilator", "Microcurrent Facial Device", "Laser Cap for Hair Growth", "Smart Nail Clipper",
    "Teeth Whitening Kit LED", "Smart Razor", "Facial Steamer", "Smart Makeup Brush Cleaner",

    # --- 7. Outdoor, Micro-mobility & Sports (户外、短途出行 & 运动) ---
    "Electric Scooter", "Electric Skateboard", "Hoverboard", "Smart Jump Rope", "Smart Dumbbell",
    "Kettlebell with Sensor", "Smart Punching Bag", "Golf Swing Analyzer", "Tennis Sensor",
    "Swim Tracker", "Smart Water Bottle", "Bike Tail Light Radar", "Smart Bike Lock",
    "Portable Power Station", "Solar Generator", "Smart Cooler", "Portable Car Jump Starter",
    "Tire Inflator Air Compressor", "Smart Fishing Lure", "Underwater Drone", "Smart Swim Goggles",
    "Smart Helmet Camera", "E-Bike Conversion Kit", "Smart Boxing Gloves", "Smart Hula Hoop",

    # --- 8. Home, Kitchen & Ambient Intelligence (全屋智能 & 厨电) ---
    "Sous Vide Precision Cooker", "Smart Meat Thermometer", "Smart Kitchen Scale", "Automatic Pan Stirrer",
    "Smart Coffee Maker", "Smart Toaster Oven", "Smart Air Fryer", "Smart Indoor Garden",
    "Smart Diffuser", "Smart Humidifier", "Smart Dehumidifier", "Robot Vacuum",
    "Window Cleaning Robot", "Pool Cleaning Robot", "Lawn Mower Robot", "Smart Blinds",
    "Smart Curtain Motor", "Smart Garage Door Opener", "Smart Lock", "Video Doorbell",
    "Smart Safe Box", "Smart Mailbox", "Smart Thermostat", "Smart AC Controller",
    "Smart Smoke Detector", "Smart Water Leak Sensor", "Smart Sprinkler Controller",
    "Weather Station", "Smart Trash Can", "Automatic Soap Dispenser",

    # --- 9. Niche & Emerging (极客长尾 & 新兴边缘) ---
    "Smart Meditation Device", "AI Plant Care Tracker", "Smart Fidget Toy", "Smart Cube",
    "Crypto Hardware Wallet", "Smart Metronome", "Smart Tape Measure", "Laser Distance Meter",
    "Smart Level", "Thermal Imaging Camera", "Stud Finder Wall Scanner", "Digital Caliper",
    "Smart Jump Starter", "OBD2 Scanner", "Dash Cam", "Smart Rearview Mirror",
    "HUD Head Up Display", "Smart Baby Formula Dispenser", "Smart Baby Rocker", "Smart Breast Pump"
]

# Ensure uniqueness and limit to exact 200 for seed phase
unique_seeds = list(dict.fromkeys(seed_list))[:200]

categories = []
for i, kw in enumerate(unique_seeds, 1):
    categories.append({
        "id": f"S{i:03d}",  # S for Seed
        "name": f"【种子】{kw}",
        "name_en": kw,
        "status": "seed_pool", # 标记为种子，等待机器雷达 L2/L3 的检验
        "tags": ["Initial Seed"]
    })

data = {
    "schema_version": "2.1",
    "last_updated": "2026-04-29",
    "methodology": "research/00-methodology-hardware.md",
    "categories": categories
}

CAT_FILE.parent.mkdir(parents=True, exist_ok=True)
CAT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"Successfully injected {len(categories)} objective seed categories into categories.json.")
