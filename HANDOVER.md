# Smart Hardware Radar - Session Handover Document

## 1. Project Context & Business Goal
**Repository**: `/Users/chenshangwei/code/smart-hardware-radar/`
**Goal**: Build an objective, data-driven market intelligence radar for high-ticket Smart Hardware (AI Wearables, Productivity Tools, Smart Lifestyle) on Amazon US / Crowdfunding platforms.
**Lineage**: This is a direct evolution of the `toy-shopify` project. It inherits the "Process-Data Separation" architecture and the strict **3-Layer Decision Framework**:
1. **Macro Screening (Sorftime / Crowdfunding)**: Category-level lifecycle & CR3 monopoly checks.
2. **Micro Teardown (Jungle Scout MCP)**: ASIN-level revenue & keyword PPC bids.
3. **Feasibility Audit**: Shenzhen PCBA costs, FCC/CE/BQB certifications, and App/SaaS development barriers.

## 2. The L1-L4 Scoring Algorithm (Hardware Adapted)
Unlike toys, smart hardware scoring heavily penalizes Tech Giant Monopoly (Apple/Samsung) and requires hardware+software supply chain readiness.
- **L1 (Geek/Social)**: Kickstarter/Indiegogo funding trends & YouTube tech reviews (Max 25).
- **L2 (Search)**: Amazon niche/scenario keyword search volume (Max 25).
- **L3 (Market)**: Market vacuum & Anti-Monopoly Index. CR3 > 50% is a severe penalty (Max 25).
- **L4 (Supply)**: PCBA/Tooling maturity + Certification barriers + App/SaaS recurring costs (Max 25).

**Algorithmic Decisions**:
- `Now Score` = L3*0.5 + L4*0.3 + L2*0.2
- `Trend Score` = L1*0.4 + L3*0.4 + L4*0.2
- 🟢 **Core (核心推荐)**: `Now >= 21.0`
- 🟡 **Trend (潜力黑马)**: `Trend >= 18.0`
- ❌ **Skip (暂缓入场)**: `Now < 15.0 & Trend < 15.0` (or manual veto due to extreme monopoly)

## 3. Current State & Seed Categories
The database (`data/categories.json`) is initialized with 3 test categories to validate the logic:
1. `H03` **Open Ear Headphones (OWS)**: 🟢 Core (High search, mature Shenzhen supply, low monopoly compared to TWS).
2. `H01` **AI Voice Recorder**: 🟡 Trend (High geek interest, SaaS recurring revenue, moderate supply barrier).
3. `H02` **Smart Ring**: ❌ Skip (Extreme monopoly by Oura/Samsung, high flexible-PCB/battery barrier).

## 4. Architecture & Immediate Next Steps for the New Agent
This repo is currently a **scaffold**. The next Agent should immediately begin the **Micro Teardown (Step 2 of the framework)** using Jungle Scout MCP.

**Your First Task:**
1. Navigate to `/Users/chenshangwei/code/smart-hardware-radar/`.
2. Use `accio-mcp-cli` to call `js_product_database_query` and `js_keywords_by_keyword`.
3. Target the `🟢 Core` and `🟡 Trend` categories (H03 Open Ear Headphones, H01 AI Voice Recorder).
4. Extract the Top 10 ASINs, their exact monthly revenue, reviews, and the exact PPC bids for their core keywords.
5. Save these results into the `v2/input/l2/` and `v2/input/l3/` directories (you will need to create them following the `toy-shopify` V2 offline schema).

*Remember: You are the Principal Data Analyst. Maintain absolute data objectivity. Do not hallucinate Amazon metrics; fetch them via tools.*
