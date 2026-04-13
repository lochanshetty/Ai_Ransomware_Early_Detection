import { useState } from 'react'
import api from '../api/client'

function HoneypotPage() {
  const [status, setStatus] = useState(null)
  const [triggered, setTriggered] = useState([])

  const createHoneypots = async () => {
    await api.post('/honeypot/create', {
      monitored_directories: ['C:/ransomware_detection/honeypots'],
      count: 5,
    })
    loadStatus()
  }

  const loadStatus = async () => {
    const [statusRes, triggeredRes] = await Promise.all([
      api.get('/honeypot/status'),
      api.get('/honeypot/triggered'),
    ])
    setStatus(statusRes.data)
    setTriggered(triggeredRes.data.triggered || [])
  }

  return (
    <div className="container">
      <h2 className="mb-3">Honeypot Control</h2>
      <div className="d-flex gap-2 mb-3">
        <button type="button" className="btn btn-primary" onClick={createHoneypots}>Create Honeypots</button>
        <button type="button" className="btn btn-outline-secondary" onClick={loadStatus}>Refresh Status</button>
      </div>
      {status && (
        <div className="alert alert-info">
          Total: {status.total_files} | Triggered: {status.triggered_files} | Safe: {status.safe_files}
        </div>
      )}
      <ul className="list-group">
        {triggered.map((item) => (
          <li key={item.id} className="list-group-item">
            {item.file_path}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default HoneypotPage
