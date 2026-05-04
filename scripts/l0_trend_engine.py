WATCH_LABELS = {
    "openclaw_hardware_bridge": "OpenClaw Hardware Bridge",
    "agentic_edge_hardware": "Agentic Edge Hardware",
    "local_ai_box": "Local AI Box",
    "ai_camera_node": "AI Camera Node",
    "ai_recorder": "AI Recorder Device",
    "geek_ai_productivity_hardware": "Geek AI Productivity Hardware",
    "programmable_keyboard_ecosystem": "Programmable Keyboard Ecosystem",
    "workflow_plugin_hardware": "Workflow Plugin Hardware",
    "ai_keyboard": "AI Keyboard / Command Deck",
    "robot_agent_kit": "Robot Agent Kit",
    "ai_devkit_peripheral": "AI Dev Kit Peripheral",
    "github_ai_projects": "Hot GitHub AI Projects",
    "ai_model_peripherals": "AI Model Peripherals",
    "big_tech_peripherals": "Big Tech Peripherals",
    "hardware_intersections": "AI Hardware Intersections",
    "ai_coding_agent_ecosystem": "AI Coding Agent Ecosystem",
}


def trend_key_for_signal(signal, topic_priority, cluster_key_fn):
    if signal.get("category_eligible") is False and signal.get("matched_watch_topics"):
        for topic in topic_priority:
            if topic in signal["matched_watch_topics"]:
                return f"watch:{topic}"
        return f"watch:{signal['matched_watch_topics'][0]}"
    return signal.get("cluster_key") or cluster_key_fn(signal) or signal.get("candidate_key")


def trend_name_for_signals(trend_key, signals, cluster_name_fn):
    if trend_key.startswith("watch:"):
        topic = trend_key.split(":", 1)[1]
        return WATCH_LABELS.get(topic, topic.replace("_", " ").title())
    return cluster_name_fn(trend_key, signals)


def trend_status_for_cluster(cluster, previous_runs, behavior_source_types):
    source_types = set(cluster["source_types"])
    has_behavior = cluster["has_behavior_source"]
    signal_count = cluster["signal_count"]
    avg_strength = cluster["avg_signal_strength"]
    recent_counts = [
        run_cluster.get("signal_count", 0)
        for run in previous_runs[-7:]
        for run_cluster in run.get("clusters", [])
        if run_cluster.get("trend_key") == cluster["trend_key"]
    ]
    previous_avg = sum(recent_counts) / len(recent_counts) if recent_counts else 0
    velocity = round(signal_count - previous_avg, 2)
    cluster["velocity_7run_delta"] = velocity

    if not has_behavior and source_types <= {"media"}:
        return "Noise", "media_only_awareness"
    if len(source_types) >= 2 and has_behavior and avg_strength >= 2.6 and (signal_count >= 3 or velocity > 0):
        return "Hot", "multi_source_behavior_with_strength"
    if has_behavior and (len(source_types) >= 2 or velocity > 0 or signal_count >= 2):
        return "Warming", "behavior_signal_needs_more_confirmation"
    return "Watch", "single_network_or_low_velocity"


def build_trend_clusters(
    signals_doc,
    trend_runs_doc,
    observed_at,
    methodology_version,
    topic_priority,
    behavior_source_types,
    cluster_key_fn,
    cluster_name_fn,
    cluster_name_zh_fn,
):
    grouped = {}
    for signal in signals_doc.get("signals", []):
        key = trend_key_for_signal(signal, topic_priority, cluster_key_fn)
        if not key:
            continue
        signal["trend_key"] = key
        grouped.setdefault(key, []).append(signal)

    previous_runs = trend_runs_doc.get("runs", [])
    clusters = []
    run_clusters = []
    for key, signals in sorted(grouped.items()):
        strengths = [signal.get("l0_scores", {}).get("signal_strength", 0) for signal in signals]
        source_types = sorted({signal.get("source_type", "unknown") for signal in signals})
        matched_watch_topics = sorted({topic for signal in signals for topic in signal.get("matched_watch_topics", [])})
        last_seen = max((signal.get("last_seen_at") or signal.get("observed_at") or "" for signal in signals), default="")
        first_seen = min((signal.get("first_seen_at") or signal.get("observed_at") or "" for signal in signals), default="")
        cluster = {
            "trend_key": key,
            "name": trend_name_for_signals(key, signals, cluster_name_fn),
            "name_zh": cluster_name_zh_fn(key),
            "signal_count": len(signals),
            "source_types": source_types,
            "source_names": sorted({signal.get("source_name", "unknown") for signal in signals}),
            "has_behavior_source": any(signal.get("source_type") in behavior_source_types for signal in signals),
            "avg_signal_strength": round(sum(strengths) / max(len(strengths), 1), 2),
            "max_signal_strength": round(max(strengths) if strengths else 0, 2),
            "seen_count_total": sum(int(signal.get("seen_count") or 1) for signal in signals),
            "matched_watch_topics": matched_watch_topics,
            "first_seen_at": first_seen,
            "last_seen_at": last_seen,
            "evidence_signal_ids": [signal.get("id") for signal in signals if signal.get("id")],
            "top_signals": sorted(
                [
                    {
                        "id": signal.get("id"),
                        "source_name": signal.get("source_name"),
                        "source_type": signal.get("source_type"),
                        "source_title": signal.get("source_title"),
                        "source_url": signal.get("source_url"),
                        "signal_strength": signal.get("l0_scores", {}).get("signal_strength", 0),
                    }
                    for signal in signals
                ],
                key=lambda value: value.get("signal_strength", 0),
                reverse=True,
            )[:5],
        }
        status, reason = trend_status_for_cluster(cluster, previous_runs, behavior_source_types)
        cluster["trend_status"] = status
        cluster["trend_reason"] = reason
        clusters.append(cluster)
        run_clusters.append(
            {
                "trend_key": key,
                "signal_count": cluster["signal_count"],
                "source_types": source_types,
                "avg_signal_strength": cluster["avg_signal_strength"],
                "has_behavior_source": cluster["has_behavior_source"],
            }
        )

    run_record = {
        "run_at": observed_at,
        "signal_count": len(signals_doc.get("signals", [])),
        "cluster_count": len(clusters),
        "clusters": run_clusters,
    }
    trend_runs_doc["schema_version"] = "1.0"
    trend_runs_doc["methodology_version"] = methodology_version
    trend_runs_doc["runs"] = (previous_runs + [run_record])[-60:]

    trend_clusters_doc = {
        "schema_version": "1.0",
        "methodology_version": methodology_version,
        "generated_at": observed_at,
        "clusters": sorted(
            clusters,
            key=lambda cluster: (
                {"Hot": 3, "Warming": 2, "Watch": 1, "Noise": 0}.get(cluster["trend_status"], 0),
                cluster["avg_signal_strength"],
                cluster["signal_count"],
            ),
            reverse=True,
        ),
    }
    return trend_clusters_doc, trend_runs_doc
