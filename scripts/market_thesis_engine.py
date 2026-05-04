import json
from datetime import datetime
from pathlib import Path


SCHEMA_VERSION = "1.0"
ROOT = Path(__file__).resolve().parent.parent
SIGNAL_FILE = ROOT / "data" / "signals.json"
TREND_CLUSTER_FILE = ROOT / "data" / "trend_clusters.json"
MARKET_THESIS_FILE = ROOT / "data" / "market_theses.json"

BEHAVIOR_DEMAND_TYPES = {"community", "search"}
MARKET_TYPES = {"marketplace", "crowdfunding", "product_launch", "product_reference"}
PRODUCTIZATION_TYPES = {"marketplace", "crowdfunding", "product_launch", "product_reference"}
SUPPLY_TYPES = {"supply_chain"}
SOURCE_WEIGHTS = {
    "community": 25,
    "developer": 20,
    "product_reference": 15,
    "crowdfunding": 20,
    "product_launch": 15,
    "search": 20,
    "marketplace": 25,
    "media": 5,
}

STATUS_RANK = {
    "Ready for Selection": 5,
    "Validated": 4,
    "Warming": 3,
    "Watch": 2,
    "Noise": 1,
}

THESIS_RULES = [
    {
        "key": "local_first_smart_home_security",
        "name": "Local-first smart home security",
        "name_zh": "本地优先智能家居安防",
        "keywords": ["smart_home_security", "doorbell", "deadbolt", "smart lock", "outdoor camera", "security camera", "home security", "local recording", "门锁", "门铃", "户外摄像头", "安防摄像头", "安防"],
        "job_to_be_done": "Homeowners want visible security and access control without subscription lock-in or cloud-only failure modes.",
        "hardware_form_factors": ["outdoor camera", "video doorbell", "smart lock", "home security hub"],
        "buyer_segments": ["homeowners", "apartment renters", "smart-home installers"],
        "substitution_risk": "High from Ring, Eufy, Aqara, Reolink and existing smart-home platforms.",
    },
    {
        "key": "ai_voice_capture_workflow",
        "name": "AI voice capture workflow devices",
        "name_zh": "AI语音采集工作流设备",
        "keywords": ["ai_voice_capture", "ai recorder", "voice recorder", "meeting recorder", "dictation", "recorder", "录音", "语音", "听写"],
        "job_to_be_done": "Knowledge workers want frictionless capture of meetings, field notes and ideas with local or private transcription paths.",
        "hardware_form_factors": ["AI recorder", "clip-on microphone", "desk dictation device", "offline transcription dock"],
        "buyer_segments": ["operators", "journalists", "students", "field sales teams"],
        "substitution_risk": "Medium from smartphone apps, meeting bots and bundled OS transcription.",
    },
    {
        "key": "agentic_edge_io_nodes",
        "name": "Agentic edge I/O nodes",
        "name_zh": "智能体边缘 I/O 节点",
        "keywords": ["agentic_edge_hardware", "local_ai_box", "ai_camera_node", "openclaw_hardware_bridge", "edge ai", "on-device ai", "local ai", "camera", "sensor", "gateway", "robot", "jetson", "hailo", "rk3588", "端侧", "边缘"],
        "job_to_be_done": "Builders need local devices that let software agents see, hear and act in the physical environment without shipping every event to the cloud.",
        "hardware_form_factors": ["edge AI box", "AI camera node", "sensor gateway", "robot agent kit"],
        "buyer_segments": ["AI builders", "smart-home power users", "robotics teams", "industrial pilots"],
        "substitution_risk": "Medium-high from Raspberry Pi, Jetson kits, cameras with built-in AI, and cloud automation stacks.",
    },
    {
        "key": "geek_ai_productivity_hardware",
        "name": "Geek AI productivity hardware",
        "name_zh": "极客 AI 生产力硬件",
        "keywords": [
            "geek_ai_productivity_hardware",
            "programmable_keyboard_ecosystem",
            "workflow_plugin_hardware",
            "stream deck",
            "moonlander",
            "keychron",
            "wooting",
            "loupedeck",
            "work louder",
            "charachorder",
            "glove80",
            "naya keyboard",
            "qmk",
            "zmk",
            "via keyboard",
            "split keyboard",
            "macro pad",
            "macropad",
            "creative console",
            "programmable keyboard",
            "ai workflow controller",
        ],
        "job_to_be_done": "Developers and creators want high-leverage physical controls for coding, AI agents and repeated workflow actions.",
        "hardware_form_factors": ["programmable keyboard", "macro pad", "workflow control console", "split ergonomic keyboard"],
        "buyer_segments": ["software engineers", "AI-heavy operators", "creators", "desk setup enthusiasts"],
        "substitution_risk": "High from Stream Deck, Loupedeck, QMK/ZMK keyboards, Raycast/Alfred and purely software shortcuts.",
    },
    {
        "key": "ai_command_input_peripherals",
        "name": "AI command input peripherals",
        "name_zh": "AI 指令输入外设",
        "keywords": ["ai_keyboard", "keyboard", "command deck", "macro pad", "coding agent", "ai_coding_agent_ecosystem", "键盘", "指令"],
        "job_to_be_done": "Power users want physical controls that shorten repeated AI, coding and creative workflows.",
        "hardware_form_factors": ["AI keyboard", "command deck", "macro pad", "programmable desktop controller"],
        "buyer_segments": ["developers", "creators", "AI-heavy operators"],
        "substitution_risk": "High from software launchers, Stream Deck, programmable keyboards and OS shortcuts.",
    },
    {
        "key": "ai_model_peripheral_devices",
        "name": "AI model peripheral devices",
        "name_zh": "AI 模型周边设备",
        "keywords": ["ai_model_peripherals", "ai dev kit", "model peripheral", "devkit", "peripheral"],
        "job_to_be_done": "AI early adopters need physical extensions around fast-moving models, but demand is still mostly developer-led.",
        "hardware_form_factors": ["AI dev kit", "desktop AI accessory", "local inference peripheral"],
        "buyer_segments": ["AI hobbyists", "developers", "prototype teams"],
        "substitution_risk": "High from generic dev boards, laptops and purely software workflows.",
    },
    {
        "key": "outdoor_smart_devices",
        "name": "Outdoor smart devices",
        "name_zh": "户外智能设备",
        "keywords": ["outdoor", "bike", "cycling", "drone", "tracker", "户外", "骑行", "无人机"],
        "job_to_be_done": "Outdoor users want connected devices that survive weather, motion and intermittent connectivity.",
        "hardware_form_factors": ["outdoor sensor", "bike device", "tracker", "rugged smart accessory"],
        "buyer_segments": ["outdoor enthusiasts", "cyclists", "fleet operators"],
        "substitution_risk": "Medium from phones, sports watches and action cameras.",
    },
    {
        "key": "smart_audio_devices",
        "name": "Smart audio devices",
        "name_zh": "智能音频设备",
        "keywords": ["speaker", "audio", "earbud", "headphone", "microphone", "音箱", "耳机", "音频"],
        "job_to_be_done": "Users want better listening and voice interaction hardware across home, desk and mobile contexts.",
        "hardware_form_factors": ["wireless speaker", "smart microphone", "earbuds", "desktop audio device"],
        "buyer_segments": ["home users", "remote workers", "audio enthusiasts"],
        "substitution_risk": "High from Apple, Sonos, Bose, JBL and commodity Bluetooth audio.",
    },
    {
        "key": "gaming_productivity_peripherals",
        "name": "Gaming productivity peripherals",
        "name_zh": "游戏与效率外设",
        "keywords": ["gaming", "monitor", "keyboard", "mouse", "display", "显示器", "游戏"],
        "job_to_be_done": "Desk users want hardware that improves focus, control and visual performance in gaming or productivity setups.",
        "hardware_form_factors": ["gaming monitor", "gaming keyboard", "desktop controller"],
        "buyer_segments": ["gamers", "developers", "desk setup buyers"],
        "substitution_risk": "High from mature peripheral brands and heavy price competition.",
    },
]

MISSING_LABELS = {
    "demand_behavior": "Demand behavior",
    "market_validation": "Market validation",
    "supply_chain": "Supply chain",
    "productization": "Productization",
    "source_diversity": "Independent source diversity",
}

VALIDATION_ACTIONS = {
    "demand_behavior": ["reddit_pain_scan", "google_trends_keyword_scan", "youtube_review_query"],
    "market_validation": ["amazon_keyword_scan", "amazon_competition_snapshot", "kickstarter_indiegogo_deep_scan"],
    "supply_chain": ["1688_alibaba_supplier_scan", "fcc_bluetooth_bom_check", "reference_design_scan"],
    "productization": ["product_launch_scan", "crowdfunding_live_project_scan"],
    "source_diversity": ["add_independent_behavior_source"],
}


def normalize(value):
    return " ".join(str(value or "").lower().replace("_", " ").replace(":", " ").split())


def combined_text(cluster):
    pieces = [
        cluster.get("trend_key"),
        cluster.get("name"),
        cluster.get("name_zh"),
        " ".join(cluster.get("matched_watch_topics", [])),
    ]
    for signal in cluster.get("top_signals", []):
        pieces.extend([signal.get("source_title"), signal.get("source_name")])
    return normalize(" ".join(piece for piece in pieces if piece))


def rule_for_cluster(cluster):
    text = combined_text(cluster)
    for rule in THESIS_RULES:
        if any(normalize(keyword) in text for keyword in rule["keywords"]):
            return rule
    name = cluster.get("name") or cluster.get("trend_key") or "Unknown hardware direction"
    key = normalize(name).replace(" ", "_")[:80] or "unknown_hardware_direction"
    return {
        "key": f"emerging_{key}",
        "name": name,
        "name_zh": cluster.get("name_zh") or name,
        "keywords": [],
        "job_to_be_done": "A specific hardware use case may be forming, but current evidence is too thin to name the buyer pain precisely.",
        "hardware_form_factors": [name],
        "buyer_segments": ["early adopters"],
        "substitution_risk": "Unknown until marketplace and buyer evidence are collected.",
    }


def source_mix_for_cluster(cluster):
    source_types = set(cluster.get("source_types", []))
    return {source_type: 1 for source_type in sorted(source_types)}


def missing_evidence_for_cluster(cluster):
    source_types = set(cluster.get("source_types", []))
    missing = []
    if not source_types & BEHAVIOR_DEMAND_TYPES:
        missing.append("demand_behavior")
    if not source_types & MARKET_TYPES:
        missing.append("market_validation")
    if not source_types & SUPPLY_TYPES:
        missing.append("supply_chain")
    if not source_types & PRODUCTIZATION_TYPES:
        missing.append("productization")
    if len(source_types) < 2:
        missing.append("source_diversity")
    return missing


def evidence_score_for_cluster(cluster, missing):
    source_types = set(cluster.get("source_types", []))
    source_score = sum(SOURCE_WEIGHTS.get(source_type, 0) for source_type in source_types)
    count_score = min(int(cluster.get("signal_count") or 0) * 4, 18)
    strength_score = min(float(cluster.get("avg_signal_strength") or 0) * 6, 18)
    seen_score = min(int(cluster.get("seen_count_total") or 0) * 1.5, 12)
    score = round(source_score + count_score + strength_score + seen_score)

    if source_types <= {"media"}:
        score = min(score, 30)
    if "demand_behavior" in missing:
        score = min(score, 65)
    if "market_validation" in missing:
        score = min(score, 70)
    if "supply_chain" in missing:
        score = min(score, 80)
    return max(0, min(int(score), 95))


def evidence_status_for_cluster(cluster, score, missing):
    trend_status = cluster.get("trend_status")
    source_types = set(cluster.get("source_types", []))
    has_demand = bool(source_types & BEHAVIOR_DEMAND_TYPES)
    has_market = bool(source_types & MARKET_TYPES)
    has_supply = bool(source_types & SUPPLY_TYPES)

    if trend_status == "Noise" or source_types <= {"media"}:
        return "Noise"
    if score >= 85 and has_demand and has_market and has_supply and len(source_types) >= 3:
        return "Ready for Selection"
    if score >= 70 and has_demand and has_market and len(source_types) >= 3:
        return "Validated"
    if score >= 55 and (has_demand or has_market) and len(source_types) >= 2:
        return "Warming"
    return "Watch"


def next_validation_for_missing(missing):
    actions = []
    for key in missing:
        actions.extend(VALIDATION_ACTIONS.get(key, []))
    deduped = []
    for action in actions:
        if action not in deduped:
            deduped.append(action)
    return deduped[:5]


def confidence_reason(cluster, status, score, missing):
    source_types = ", ".join(cluster.get("source_types", [])) or "no sources"
    if status in {"Ready for Selection", "Validated"}:
        return f"{status} because evidence score is {score} with source mix {source_types}."
    if status == "Warming":
        return f"Warming because behavior or market evidence exists, but {', '.join(MISSING_LABELS[item] for item in missing[:2])} is still missing."
    if status == "Noise":
        return "Noise because current evidence is weak, media-only, or not yet behavior-backed."
    return f"Watch because the thesis needs {', '.join(MISSING_LABELS[item] for item in missing[:2]) or 'more confirmation'}."


def top_signals(cluster):
    return [
        {
            "id": signal.get("id"),
            "source_name": signal.get("source_name"),
            "source_type": signal.get("source_type"),
            "source_title": signal.get("source_title"),
            "source_url": signal.get("source_url"),
            "signal_strength": signal.get("signal_strength", 0),
        }
        for signal in cluster.get("top_signals", [])[:3]
    ]


def thesis_for_cluster(index, cluster):
    rule = rule_for_cluster(cluster)
    missing = missing_evidence_for_cluster(cluster)
    score = evidence_score_for_cluster(cluster, missing)
    status = evidence_status_for_cluster(cluster, score, missing)
    return {
        "id": f"M{index:03d}",
        "thesis_key": rule["key"],
        "name": rule["name"],
        "name_zh": rule["name_zh"],
        "job_to_be_done": rule["job_to_be_done"],
        "hardware_form_factors": rule["hardware_form_factors"],
        "buyer_segments": rule["buyer_segments"],
        "evidence_status": status,
        "evidence_score": score,
        "source_mix": source_mix_for_cluster(cluster),
        "source_names": cluster.get("source_names", []),
        "signal_count": cluster.get("signal_count", 0),
        "trend_key": cluster.get("trend_key"),
        "trend_status": cluster.get("trend_status"),
        "trend_reason": cluster.get("trend_reason"),
        "_avg_signal_strength": cluster.get("avg_signal_strength", 0),
        "evidence_signal_ids": cluster.get("evidence_signal_ids", []),
        "top_signals": top_signals(cluster),
        "missing_evidence": missing,
        "substitution_risk": rule["substitution_risk"],
        "next_validation": next_validation_for_missing(missing),
        "confidence_reason": confidence_reason(cluster, status, score, missing),
    }


def merge_duplicate_theses(theses):
    merged = {}
    for thesis in theses:
        key = thesis["thesis_key"]
        current = merged.get(key)
        if not current:
            merged[key] = thesis
            continue
        current["signal_count"] += thesis.get("signal_count", 0)
        current["source_names"] = sorted(set(current.get("source_names", [])) | set(thesis.get("source_names", [])))
        current["evidence_signal_ids"] = sorted(set(current.get("evidence_signal_ids", [])) | set(thesis.get("evidence_signal_ids", [])))
        current["top_signals"] = (current.get("top_signals", []) + thesis.get("top_signals", []))[:5]
        current["_avg_signal_strength"] = max(current.get("_avg_signal_strength", 0), thesis.get("_avg_signal_strength", 0))
        for source_type, count in thesis.get("source_mix", {}).items():
            current["source_mix"][source_type] = current["source_mix"].get(source_type, 0) + count
        if thesis.get("evidence_score", 0) > current.get("evidence_score", 0):
            for field in ("evidence_score", "evidence_status", "trend_key", "trend_status", "trend_reason", "missing_evidence", "next_validation", "confidence_reason"):
                current[field] = thesis[field]
    refreshed = []
    for thesis in merged.values():
        source_types = sorted(thesis.get("source_mix", {}).keys())
        synthetic_cluster = {
            "source_types": source_types,
            "signal_count": thesis.get("signal_count", 0),
            "avg_signal_strength": thesis.get("_avg_signal_strength", 0),
            "seen_count_total": thesis.get("signal_count", 0),
            "trend_status": thesis.get("trend_status"),
        }
        missing = missing_evidence_for_cluster(synthetic_cluster)
        score = evidence_score_for_cluster(synthetic_cluster, missing)
        status = evidence_status_for_cluster(synthetic_cluster, score, missing)
        thesis["missing_evidence"] = missing
        thesis["evidence_score"] = score
        thesis["evidence_status"] = status
        thesis["next_validation"] = next_validation_for_missing(missing)
        thesis["confidence_reason"] = confidence_reason(synthetic_cluster, status, score, missing)
        thesis.pop("_avg_signal_strength", None)
        refreshed.append(thesis)
    return refreshed


def build_market_theses(trend_clusters_doc, signals_doc=None, observed_at=None, methodology_version="1.0"):
    observed_at = observed_at or datetime.now().isoformat() + "Z"
    raw_theses = [
        thesis_for_cluster(index, cluster)
        for index, cluster in enumerate(trend_clusters_doc.get("clusters", []), 1)
    ]
    theses = merge_duplicate_theses(raw_theses)
    theses = sorted(
        theses,
        key=lambda thesis: (
            STATUS_RANK.get(thesis.get("evidence_status"), 0),
            thesis.get("evidence_score", 0),
            thesis.get("signal_count", 0),
        ),
        reverse=True,
    )
    for index, thesis in enumerate(theses, 1):
        thesis["id"] = f"M{index:03d}"
    return {
        "schema_version": SCHEMA_VERSION,
        "methodology_version": methodology_version,
        "generated_at": observed_at,
        "theses": theses,
    }


def read_json(path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    trend_clusters_doc = read_json(TREND_CLUSTER_FILE, {"clusters": []})
    signals_doc = read_json(SIGNAL_FILE, {"signals": []})
    observed_at = datetime.now().isoformat() + "Z"
    methodology_version = trend_clusters_doc.get("methodology_version") or signals_doc.get("methodology_version") or "1.0"
    market_theses_doc = build_market_theses(trend_clusters_doc, signals_doc, observed_at, methodology_version)
    write_json(MARKET_THESIS_FILE, market_theses_doc)
    print(f"Market theses updated: {len(market_theses_doc.get('theses', []))}")


if __name__ == "__main__":
    main()
