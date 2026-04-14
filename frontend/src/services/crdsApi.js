const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

async function postJson(path, body = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

export async function getMonitorStatus() {
  try {
    return await getJson('/monitor/status')
  } catch {
    return { is_running: false, run_id: null, started_at: null }
  }
}

export async function getHealth() {
  try {
    return await getJson('/healthz')
  } catch {
    return { status: 'down', service: 'CRDS backend', counts: { logs: 0, threats: 0, alerts: 0 } }
  }
}

export async function getThreats() {
  try {
    const payload = await getJson('/detect/threats')
    if (Array.isArray(payload)) {
      return payload
    }
    return payload?.results || []
  } catch {
    return []
  }
}

export async function getAlerts() {
  try {
    return await getJson('/alerts/')
  } catch {
    return []
  }
}

export async function getMonitorLogs(filter = 'all') {
  try {
    const payload = await getJson(`/monitor/logs?status=${encodeURIComponent(filter)}`)
    return payload.results || []
  } catch {
    return []
  }
}

export async function startMonitoring() {
  return postJson('/monitor/start')
}

export async function runDemoAttack() {
  return postJson('/demo/run')
}

export async function getSystemStatus() {
  try {
    return await getJson('/system/status')
  } catch {
    return { monitoring: 'stopped', attack: 'stopped' }
  }
}

export async function systemStartMonitoring() {
  return postJson('/system/start-monitoring')
}

export async function systemStopMonitoring() {
  return postJson('/system/stop-monitoring')
}

export async function systemRunAttack() {
  return postJson('/system/run-attack')
}

export async function systemStopAttack() {
  return postJson('/system/stop-attack')
}

export async function openFilePath(path) {
  const payload = await getJson(`/file/open?path=${encodeURIComponent(path)}`)
  return payload.preview_url
}

export async function getSystemMetrics() {
  try {
    return await getJson('/system/metrics')
  } catch {
    return {
      status: 'down',
      system: { monitoring: 'stopped', attack: 'stopped' },
      metrics: { cpu_percent: 0, memory_percent: 0, disk_percent: 0, network_bytes_sent: 0, network_bytes_recv: 0 },
      components: [],
    }
  }
}

export async function getHoneypotStatus() {
  try {
    return await getJson('/honeypot/status')
  } catch {
    return { total_files: 0, triggered_files: 0, safe_files: 0 }
  }
}

export async function getHoneypotTriggered() {
  try {
    const payload = await getJson('/honeypot/triggered')
    return payload.triggered || []
  } catch {
    return []
  }
}

export async function generateHoneypots() {
  return postJson('/honeypot/generate')
}

export async function refreshHoneypots() {
  return postJson('/honeypot/refresh')
}
