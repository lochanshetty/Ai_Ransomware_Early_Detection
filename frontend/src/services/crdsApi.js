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
    return await getJson('/detect/threats')
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

export async function getMonitorLogs() {
  try {
    const payload = await getJson('/monitor/logs')
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
