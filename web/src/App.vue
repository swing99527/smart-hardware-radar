<template>
  <div class="shell py-4 md:py-6 space-y-4">
    <header class="panel px-4 py-3 md:px-5 md:py-4">
      <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full" :class="stats.sourceErrors ? 'bg-red' : 'bg-green'"></span>
            <h1 class="text-xl md:text-2xl font-semibold text-white">Smart Hardware Radar</h1>
            <span class="chip mono">V1.2</span>
            <span class="status-badge" :class="stats.sourceErrors ? 'status-error' : 'status-ok'">
              {{ stats.sourceErrors ? 'SOURCE DEGRADED' : 'SOURCES OK' }}
            </span>
          </div>
          <div class="mt-1 text-sm text-muted">智能硬件趋势监控 · 证据分层 · 源健康审计</div>
        </div>
        <div class="grid grid-cols-2 gap-2 text-right sm:flex sm:items-center sm:gap-2">
          <div class="panel-soft px-3 py-2">
            <div class="text-[11px] text-muted">最近同步</div>
            <div class="mono text-xs text-gray-200">{{ lastUpdated }}</div>
          </div>
          <div class="panel-soft px-3 py-2">
            <div class="text-[11px] text-muted">行为源异常</div>
            <div class="mono text-xs" :class="criticalHealthRows.length ? 'text-red' : 'text-green'">{{ criticalHealthRows.length }}</div>
          </div>
        </div>
      </div>
    </header>

    <section class="grid grid-cols-2 gap-3 lg:grid-cols-6">
      <div class="panel metric p-3">
        <div class="text-xs text-muted">Hot</div>
        <div class="mt-2 text-3xl font-semibold text-green">{{ stats.hot }}</div>
        <div class="mt-1 text-xs text-muted">多源强信号</div>
      </div>
      <div class="panel metric p-3">
        <div class="text-xs text-muted">Warming</div>
        <div class="mt-2 text-3xl font-semibold text-amber">{{ stats.warming }}</div>
        <div class="mt-1 text-xs text-muted">行为信号升温</div>
      </div>
      <div class="panel metric p-3">
        <div class="text-xs text-muted">Watch</div>
        <div class="mt-2 text-3xl font-semibold text-blue">{{ stats.watch }}</div>
        <div class="mt-1 text-xs text-muted">单源观察</div>
      </div>
      <div class="panel metric p-3">
        <div class="text-xs text-muted">Noise</div>
        <div class="mt-2 text-3xl font-semibold text-red">{{ stats.noise }}</div>
        <div class="mt-1 text-xs text-muted">媒体或弱证据</div>
      </div>
      <div class="panel metric p-3">
        <div class="text-xs text-muted">Signals</div>
        <div class="mt-2 text-3xl font-semibold text-white">{{ stats.signalTotal }}</div>
        <div class="mt-1 text-xs text-muted">{{ stats.marketThesisTotal }} market theses</div>
      </div>
      <div class="panel metric p-3">
        <div class="text-xs text-muted">Sources</div>
        <div class="mt-2 text-3xl font-semibold" :class="stats.sourceErrors ? 'text-red' : 'text-green'">{{ sourceHealth.length }}</div>
        <div class="mt-1 text-xs text-muted">{{ stats.sourceErrors }} 异常</div>
      </div>
    </section>

    <section class="panel overflow-hidden">
      <div class="flex flex-col gap-2 border-b border-line px-4 py-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-base font-semibold text-white">细分市场假设</h2>
          <div class="text-xs text-muted">{{ sortedMarketTheses.length }} theses · {{ stats.validatedTheses }} validated</div>
        </div>
      </div>
      <div class="table-scroll">
        <table class="w-full border-collapse text-left text-sm market-table">
          <thead>
            <tr class="border-b border-line bg-black/20 text-[11px] uppercase text-muted">
              <th class="px-4 py-3 font-semibold">市场假设</th>
              <th class="px-4 py-3 text-right font-semibold">证据</th>
              <th class="px-4 py-3 font-semibold">Job / 形态</th>
              <th class="px-4 py-3 font-semibold">来源组合</th>
              <th class="px-4 py-3 font-semibold">缺口</th>
              <th class="px-4 py-3 font-semibold">下一步验证</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-line/80">
            <tr v-for="thesis in sortedMarketTheses" :key="thesis.id" class="row-hover align-top">
              <td class="px-4 py-3 min-w-[250px]">
                <div class="flex items-center gap-2">
                  <span class="mono text-xs text-muted">{{ thesis.id }}</span>
                  <span class="font-medium text-gray-100">{{ thesis.name_zh || thesis.name }}</span>
                </div>
                <div class="mono mt-1 text-[11px] text-muted">{{ thesis.thesis_key }}</div>
                <div class="mt-2 text-xs text-muted truncate-2">{{ thesis.substitution_risk }}</div>
              </td>
              <td class="px-4 py-3 min-w-[140px] text-right">
                <span class="status-badge" :class="marketStatusClass(thesis.evidence_status)">{{ marketStatusText(thesis.evidence_status) }}</span>
                <div class="mono mt-2 text-lg font-semibold" :class="getSignalColor(thesis.evidence_score / 25)">{{ thesis.evidence_score }}</div>
                <div class="text-xs text-muted">{{ thesis.signal_count }} signals</div>
              </td>
              <td class="px-4 py-3 min-w-[320px]">
                <div class="truncate-2 text-gray-200">{{ thesis.job_to_be_done }}</div>
                <div class="mt-2 flex flex-wrap gap-1">
                  <span v-for="form in (thesis.hardware_form_factors || []).slice(0, 4)" :key="form" class="chip">{{ form }}</span>
                </div>
              </td>
              <td class="px-4 py-3 min-w-[170px]">
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="type in sourceMixTypes(thesis)" :key="type" class="chip gap-1.5">
                    <span class="source-dot" :class="sourceDotClass(type)"></span>{{ sourceTypeText(type) }}
                  </span>
                </div>
              </td>
              <td class="px-4 py-3 min-w-[210px]">
                <div class="flex flex-wrap gap-1">
                  <span v-for="item in (thesis.missing_evidence || []).slice(0, 4)" :key="item" class="chip">{{ missingEvidenceText(item) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 min-w-[250px]">
                <div class="flex flex-wrap gap-1">
                  <span v-for="action in (thesis.next_validation || []).slice(0, 4)" :key="action" class="chip mono">{{ validationText(action) }}</span>
                </div>
              </td>
            </tr>
            <tr v-if="sortedMarketTheses.length === 0">
              <td colspan="6" class="px-4 py-10 text-center text-muted">还没有市场假设。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <main class="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.55fr)_minmax(360px,.65fr)]">
      <section class="panel overflow-hidden">
        <div class="flex flex-col gap-3 border-b border-line px-4 py-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 class="text-base font-semibold text-white">趋势雷达</h2>
            <div class="text-xs text-muted">{{ filteredTrendClusters.length }} / {{ trendClusters.length }} clusters</div>
          </div>
          <div class="panel-soft inline-flex w-fit flex-wrap gap-1 p-1">
            <button
              v-for="option in trendFilterOptions"
              :key="option.value"
              class="seg-button"
              :class="{ active: trendFilter === option.value }"
              @click="trendFilter = option.value"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
        <div class="table-scroll">
          <table class="w-full border-collapse text-left text-sm">
            <thead>
              <tr class="border-b border-line bg-black/20 text-[11px] uppercase text-muted">
                <th class="px-4 py-3 font-semibold">趋势</th>
                <th class="px-4 py-3 font-semibold">证据</th>
                <th class="px-4 py-3 font-semibold">来源</th>
                <th class="px-4 py-3 text-right font-semibold">强度</th>
                <th class="px-4 py-3 text-right font-semibold">速度</th>
                <th class="px-4 py-3 text-right font-semibold">状态</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-line/80">
              <tr v-for="trend in filteredTrendClusters" :key="trend.trend_key" class="row-hover align-top">
                <td class="px-4 py-3 min-w-[260px]">
                  <div class="font-medium text-gray-100">{{ trend.name_zh || trend.name }}</div>
                  <div class="mono mt-1 text-[11px] text-muted">{{ trend.trend_key }}</div>
                  <div class="mt-2 flex flex-wrap gap-1">
                    <span v-for="topic in trend.matched_watch_topics.slice(0, 3)" :key="topic" class="chip mono">{{ topic }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 min-w-[320px]">
                  <div class="mono text-xs text-gray-300">{{ trend.signal_count }} signals · {{ trend.seen_count_total }} seen</div>
                  <a
                    v-if="topSignalUrl(trend)"
                    :href="topSignalUrl(trend)"
                    target="_blank"
                    class="mt-1 block max-w-[430px] text-xs text-muted hover:text-blue"
                    :title="topSignalTitle(trend)"
                  >
                    <span class="truncate-2">{{ topSignalTitle(trend) }}</span>
                  </a>
                  <div v-else class="mt-1 max-w-[430px] text-xs text-muted truncate-2">{{ topSignalTitle(trend) }}</div>
                </td>
                <td class="px-4 py-3 min-w-[150px]">
                  <div class="flex flex-wrap gap-1.5">
                    <span v-for="type in trend.source_types" :key="type" class="chip gap-1.5">
                      <span class="source-dot" :class="sourceDotClass(type)"></span>{{ sourceTypeText(type) }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3 text-right mono font-semibold" :class="getSignalColor(trend.avg_signal_strength)">{{ trend.avg_signal_strength }}</td>
                <td class="px-4 py-3 text-right mono text-gray-300">{{ trend.velocity_7run_delta > 0 ? '+' : '' }}{{ trend.velocity_7run_delta || 0 }}</td>
                <td class="px-4 py-3 text-right">
                  <span class="status-badge" :class="getTrendClass(trend.trend_status)">{{ trendStatusText(trend.trend_status) }}</span>
                  <div class="mt-1 text-xs text-muted">{{ trendReasonText(trend.trend_reason) }}</div>
                </td>
              </tr>
              <tr v-if="filteredTrendClusters.length === 0">
                <td colspan="6" class="px-4 py-10 text-center text-muted">没有匹配的趋势。</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="space-y-4">
        <section class="panel overflow-hidden">
          <div class="border-b border-line px-4 py-3">
            <h2 class="text-base font-semibold text-white">源健康异常</h2>
            <div class="text-xs text-muted">GitHub / Reddit / API 认证与限流</div>
          </div>
          <div class="divide-y divide-line/80">
            <div v-for="source in criticalHealthRows.slice(0, 8)" :key="source.source_name + source.url" class="px-4 py-3">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="truncate text-sm font-medium text-gray-100" :title="source.source_name">{{ source.source_name }}</div>
                  <div class="mt-1 flex flex-wrap gap-1">
                    <span class="chip">{{ authModeText(source.auth_mode) }}</span>
                    <span class="chip mono">{{ rateLimitText(source.rate_limit) }}</span>
                  </div>
                </div>
                <span class="status-badge" :class="getSourceHealthClass(source.status)">{{ sourceHealthText(source.status) }}</span>
              </div>
              <div v-if="source.error" class="mt-2 truncate text-xs text-muted" :title="source.error">{{ source.error }}</div>
            </div>
            <div v-if="criticalHealthRows.length === 0" class="px-4 py-8 text-center text-sm text-muted">暂无关键源异常。</div>
          </div>
        </section>

        <section class="panel overflow-hidden">
          <div class="border-b border-line px-4 py-3">
            <h2 class="text-base font-semibold text-white">证据队列</h2>
            <div class="text-xs text-muted">待补证据、观察源、已晋级</div>
          </div>
          <div class="grid grid-cols-3 divide-x divide-line/80 text-center">
            <div class="p-3">
              <div class="text-2xl font-semibold text-amber">{{ stats.held }}</div>
              <div class="text-xs text-muted">待补</div>
            </div>
            <div class="p-3">
              <div class="text-2xl font-semibold text-blue">{{ stats.watchOnly }}</div>
              <div class="text-xs text-muted">观察</div>
            </div>
            <div class="p-3">
              <div class="text-2xl font-semibold text-green">{{ stats.promoted }}</div>
              <div class="text-xs text-muted">晋级</div>
            </div>
          </div>
        </section>
      </aside>
    </main>

    <section class="panel overflow-hidden">
      <div class="flex flex-col gap-3 border-b border-line px-4 py-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-base font-semibold text-white">信号收件箱</h2>
          <div class="text-xs text-muted">Top {{ filteredSignals.length }} visible signals</div>
        </div>
        <div class="panel-soft inline-flex w-fit flex-wrap gap-1 p-1">
          <button
            v-for="option in signalFilterOptions"
            :key="option.value"
            class="seg-button"
            :class="{ active: signalFilter === option.value }"
            @click="signalFilter = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
      <div class="table-scroll">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-line bg-black/20 text-[11px] uppercase text-muted">
              <th class="px-4 py-3 font-semibold">信号</th>
              <th class="px-4 py-3 font-semibold">候选 / 聚类</th>
              <th class="px-4 py-3 font-semibold">来源</th>
              <th class="px-4 py-3 text-right font-semibold">强度</th>
              <th class="px-4 py-3 text-right font-semibold">命中</th>
              <th class="px-4 py-3 text-right font-semibold">证据门</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-line/80">
            <tr v-for="signal in filteredSignals" :key="signal.id" class="row-hover align-top">
              <td class="px-4 py-3 min-w-[320px]">
                <div class="flex items-center gap-2">
                  <span class="mono text-xs text-muted">{{ signal.id }}</span>
                  <a v-if="signal.source_url" :href="signal.source_url" target="_blank" class="text-xs text-blue hover:text-white">source</a>
                </div>
                <div class="mt-1 max-w-[460px] truncate-2 text-gray-200" :title="signal.source_title">{{ signal.source_title }}</div>
              </td>
              <td class="px-4 py-3 min-w-[220px]">
                <div class="font-medium text-gray-100">{{ signal.candidate_category }}</div>
                <div class="mono mt-1 text-[11px] text-muted">{{ signal.cluster_name_zh || signal.cluster_name || signal.candidate_key }}</div>
              </td>
              <td class="px-4 py-3 min-w-[180px]">
                <div class="text-gray-200">{{ signal.source_name }}</div>
                <div class="mt-1 flex gap-1">
                  <span class="chip gap-1.5"><span class="source-dot" :class="sourceDotClass(signal.source_type)"></span>{{ sourceTypeText(signal.source_type) }}</span>
                  <span class="chip">{{ languageText(signal.source_language) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-right mono font-semibold" :class="getSignalColor(signal.l0_scores && signal.l0_scores.signal_strength)">{{ signal.l0_scores ? signal.l0_scores.signal_strength : '--' }}</td>
              <td class="px-4 py-3 text-right mono text-gray-300">{{ signal.seen_count || 1 }}x</td>
              <td class="px-4 py-3 text-right">
                <span class="status-badge" :class="getGateClass(signal.gate_status)">{{ gateStatusText(signal.gate_status) }}</span>
                <div class="mt-1 text-xs text-muted">{{ gateReasonText(signal.gate_reason) }}</div>
              </td>
            </tr>
            <tr v-if="filteredSignals.length === 0">
              <td colspan="6" class="px-4 py-10 text-center text-muted">没有匹配的信号。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel overflow-hidden">
      <div class="flex flex-col gap-2 border-b border-line px-4 py-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-base font-semibold text-white">采集源健康度</h2>
          <div class="text-xs text-muted">{{ sourceHealth.length }} sources · {{ stats.sourceErrors }} degraded</div>
        </div>
      </div>
      <div class="table-scroll">
        <table class="w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-line bg-black/20 text-[11px] uppercase text-muted">
              <th class="px-4 py-3 font-semibold">采集源</th>
              <th class="px-4 py-3 font-semibold">类型</th>
              <th class="px-4 py-3 font-semibold">认证</th>
              <th class="px-4 py-3 text-right font-semibold">命中</th>
              <th class="px-4 py-3 font-semibold">限流</th>
              <th class="px-4 py-3 font-semibold">最近成功</th>
              <th class="px-4 py-3 text-right font-semibold">状态</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-line/80">
            <tr v-for="source in healthRows" :key="source.source_name + source.url" class="row-hover align-top">
              <td class="px-4 py-3 min-w-[260px]">
                <div class="font-medium text-gray-100">{{ source.source_name }}</div>
                <div v-if="source.error" class="mt-1 max-w-[420px] truncate text-xs text-muted" :title="source.error">{{ source.error }}</div>
              </td>
              <td class="px-4 py-3 text-muted">{{ sourceTypeText(source.source_type) }} · {{ languageText(source.source_language) }}</td>
              <td class="px-4 py-3"><span class="chip">{{ authModeText(source.auth_mode) }}</span></td>
              <td class="px-4 py-3 text-right mono text-gray-300">{{ source.item_count || 0 }}</td>
              <td class="px-4 py-3 mono text-muted">{{ rateLimitText(source.rate_limit) }}</td>
              <td class="px-4 py-3 mono text-muted">{{ source.last_success_at || '--' }}</td>
              <td class="px-4 py-3 text-right"><span class="status-badge" :class="getSourceHealthClass(source.status)">{{ sourceHealthText(source.status) }}</span></td>
            </tr>
            <tr v-if="sourceHealth.length === 0">
              <td colspan="7" class="px-4 py-10 text-center text-muted">还没有采集源状态。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const categories = ref([])
const signals = ref([])
const sourceHealth = ref([])
const trendClusters = ref([])
const marketTheses = ref([])
const lastUpdated = ref('加载中...')
const trendFilter = ref('all')
const signalFilter = ref('all')

const trendFilterOptions = [
  { value: 'all', label: '全部' },
  { value: 'Hot', label: 'Hot' },
  { value: 'Warming', label: 'Warming' },
  { value: 'Watch', label: 'Watch' },
  { value: 'Noise', label: 'Noise' }
]

const signalFilterOptions = [
  { value: 'all', label: '全部' },
  { value: 'held', label: '待补' },
  { value: 'watch_only', label: '观察' },
  { value: 'promoted', label: '晋级' }
]

const loadData = async () => {
  try {
    const response = await fetch(`./data.json?t=${Date.now()}`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    categories.value = data.categories || []
    signals.value = data.signals || []
    sourceHealth.value = data.source_health || []
    trendClusters.value = data.trend_clusters || []
    marketTheses.value = data.market_theses || []
    lastUpdated.value = data.last_updated || '未知'
  } catch (error) {
    console.error('Failed to load data.json', error)
    lastUpdated.value = '数据同步失败'
  }
}

const sortedTrendClusters = computed(() => {
  const rank = { Hot: 4, Warming: 3, Watch: 2, Noise: 1 }
  return [...trendClusters.value].sort((a, b) => {
    const statusA = rank[a.trend_status] || 0
    const statusB = rank[b.trend_status] || 0
    if (statusA !== statusB) return statusB - statusA
    const strengthA = a.avg_signal_strength || 0
    const strengthB = b.avg_signal_strength || 0
    if (strengthA !== strengthB) return strengthB - strengthA
    return (b.signal_count || 0) - (a.signal_count || 0)
  })
})

const filteredTrendClusters = computed(() => {
  if (trendFilter.value === 'all') return sortedTrendClusters.value
  return sortedTrendClusters.value.filter((trend) => trend.trend_status === trendFilter.value)
})

const sortedMarketTheses = computed(() => {
  const rank = { 'Ready for Selection': 5, Validated: 4, Warming: 3, Watch: 2, Noise: 1 }
  return [...marketTheses.value].sort((a, b) => {
    const statusA = rank[a.evidence_status] || 0
    const statusB = rank[b.evidence_status] || 0
    if (statusA !== statusB) return statusB - statusA
    const scoreA = a.evidence_score || 0
    const scoreB = b.evidence_score || 0
    if (scoreA !== scoreB) return scoreB - scoreA
    return (b.signal_count || 0) - (a.signal_count || 0)
  })
})

const sortedSignals = computed(() => {
  return [...signals.value].sort((a, b) => {
    const scoreA = a.l0_scores ? a.l0_scores.signal_strength || 0 : 0
    const scoreB = b.l0_scores ? b.l0_scores.signal_strength || 0 : 0
    if (scoreA !== scoreB) return scoreB - scoreA
    return (b.last_seen_at || b.observed_at || '').localeCompare(a.last_seen_at || a.observed_at || '')
  })
})

const filteredSignals = computed(() => {
  const rows = signalFilter.value === 'all'
    ? sortedSignals.value
    : sortedSignals.value.filter((signal) => (signal.gate_status || 'held') === signalFilter.value)
  return rows.slice(0, 60)
})

const healthRows = computed(() => {
  const rank = { error: 0, fetch_ok_parse_failed: 1, fetch_ok_zero_items: 2, ok: 3 }
  return [...sourceHealth.value].sort((a, b) => {
    if (a.status !== b.status) return (rank[a.status] ?? 1) - (rank[b.status] ?? 1)
    return (a.source_name || '').localeCompare(b.source_name || '')
  })
})

const criticalHealthRows = computed(() => {
  return healthRows.value.filter((source) => {
    const name = source.source_name || ''
    const critical = name.startsWith('GitHub') || name.startsWith('Reddit')
    return critical && !['ok', 'fetch_ok_zero_items'].includes(source.status)
  })
})

const stats = computed(() => {
  const hot = trendClusters.value.filter((trend) => trend.trend_status === 'Hot').length
  const warming = trendClusters.value.filter((trend) => trend.trend_status === 'Warming').length
  const watch = trendClusters.value.filter((trend) => trend.trend_status === 'Watch').length
  const noise = trendClusters.value.filter((trend) => trend.trend_status === 'Noise').length
  const held = signals.value.filter((signal) => signal.gate_status === 'held').length
  const watchOnly = signals.value.filter((signal) => signal.gate_status === 'watch_only').length
  const promoted = signals.value.filter((signal) => signal.gate_status === 'promoted').length
  const sourceErrors = sourceHealth.value.filter((source) => !['ok', 'fetch_ok_zero_items'].includes(source.status)).length
  const marketThesisTotal = marketTheses.value.length
  const validatedTheses = marketTheses.value.filter((thesis) => ['Validated', 'Ready for Selection'].includes(thesis.evidence_status)).length
  return { trendTotal: trendClusters.value.length, categoryTotal: categories.value.length, hot, warming, watch, noise, signalTotal: signals.value.length, held, watchOnly, promoted, sourceErrors, marketThesisTotal, validatedTheses }
})

const getTrendClass = (status) => {
  if (status === 'Hot') return 'status-hot'
  if (status === 'Warming') return 'status-warming'
  if (status === 'Noise') return 'status-noise'
  return 'status-watch'
}

const trendStatusText = (status) => {
  const labels = { Hot: '热门', Warming: '升温', Watch: '观察', Noise: '噪声' }
  return labels[status] || status || '未知'
}

const trendReasonText = (reason) => {
  const labels = {
    multi_source_behavior_with_strength: '多源强行为',
    behavior_signal_needs_more_confirmation: '行为待确认',
    single_network_or_low_velocity: '低速观察',
    media_only_awareness: '媒体认知'
  }
  return labels[reason] || reason || '待解释'
}

const marketStatusClass = (status) => {
  if (status === 'Ready for Selection' || status === 'Validated') return 'status-hot'
  if (status === 'Warming') return 'status-warming'
  if (status === 'Noise') return 'status-noise'
  return 'status-watch'
}

const marketStatusText = (status) => {
  const labels = {
    'Ready for Selection': '可选品',
    Validated: '已验证',
    Warming: '升温',
    Watch: '观察',
    Noise: '噪声'
  }
  return labels[status] || status || '未知'
}

const sourceMixTypes = (thesis) => Object.keys(thesis.source_mix || {}).sort()

const missingEvidenceText = (item) => {
  const labels = {
    demand_behavior: '需求行为',
    market_validation: '市场验证',
    supply_chain: '供应链',
    productization: '产品化',
    source_diversity: '多源'
  }
  return labels[item] || item || '未知'
}

const validationText = (action) => {
  const labels = {
    reddit_pain_scan: 'Reddit pain',
    google_trends_keyword_scan: 'Trends',
    youtube_review_query: 'YouTube',
    amazon_keyword_scan: 'Amazon keyword',
    amazon_competition_snapshot: 'Amazon CR',
    kickstarter_indiegogo_deep_scan: 'Crowdfunding',
    '1688_alibaba_supplier_scan': '1688/Alibaba',
    fcc_bluetooth_bom_check: 'FCC/BOM',
    reference_design_scan: 'Reference design',
    product_launch_scan: 'Launch',
    crowdfunding_live_project_scan: 'Live funding',
    add_independent_behavior_source: 'Add source'
  }
  return labels[action] || action || 'next'
}

const topSignal = (trend) => trend.top_signals && trend.top_signals[0]
const topSignalTitle = (trend) => {
  const top = topSignal(trend)
  return top ? `${top.source_name}: ${top.source_title}` : '--'
}
const topSignalUrl = (trend) => {
  const top = topSignal(trend)
  return top && top.source_url
}

const getSignalColor = (score) => {
  if (score === undefined || score === null) return 'text-muted'
  if (score >= 3) return 'text-green'
  if (score >= 2) return 'text-amber'
  return 'text-muted'
}

const getGateClass = (status) => {
  if (status === 'promoted') return 'status-promoted'
  if (status === 'watch_only') return 'status-watch-only'
  if (status === 'rejected') return 'status-rejected'
  return 'status-held'
}

const sourceTypeText = (type) => {
  const labels = {
    media: '媒体',
    community: '社区',
    developer: '开发者',
    product_launch: '发布',
    crowdfunding: '众筹',
    marketplace: '电商',
    search: '搜索',
    unknown: '未知'
  }
  return labels[type] || type || '未知'
}

const sourceDotClass = (type) => `dot-${type || 'unknown'}`

const gateStatusText = (status) => {
  const labels = {
    promoted: '已晋级',
    held: '待补证据',
    watch_only: '观察源',
    rejected: '已拒绝'
  }
  return labels[status || 'held'] || status || '待补证据'
}

const gateReasonText = (reason) => {
  const labels = {
    needs_two_independent_source_types: '需要双源',
    needs_behavior_source: '需要行为源',
    watch_only_source: '观察不晋级',
    generic_category: '泛词拦截',
    existing_category: '已有类目',
    passed: '已通过',
    not_evaluated: '未评估'
  }
  return labels[reason || 'not_evaluated'] || reason || '未评估'
}

const languageText = (language) => {
  const labels = { zh: '中文', en: '英文', unknown: '未知' }
  return labels[language || 'unknown'] || language || '未知'
}

const authModeText = (mode) => {
  const labels = {
    token: 'Token',
    anonymous: '匿名',
    reddit_oauth: 'OAuth',
    public_json: '公共 JSON',
    none: '无'
  }
  return labels[mode || 'none'] || mode || '无'
}

const rateLimitText = (rateLimit) => {
  if (!rateLimit) return '--'
  const remaining = rateLimit['x-ratelimit-remaining']
  const limit = rateLimit['x-ratelimit-limit']
  const retryAfter = rateLimit['retry-after']
  if (remaining !== undefined && limit !== undefined) return `${remaining}/${limit}`
  if (retryAfter !== undefined) return `retry ${retryAfter}s`
  return '--'
}

const getSourceHealthClass = (status) => {
  if (status === 'ok') return 'status-ok'
  if (status === 'fetch_ok_zero_items') return 'status-zero'
  return 'status-error'
}

const sourceHealthText = (status) => {
  const labels = {
    ok: '正常',
    fetch_ok_zero_items: '无命中',
    fetch_ok_parse_failed: '解析失败',
    error: '抓取失败'
  }
  return labels[status] || status || '未知'
}

onMounted(loadData)
</script>
