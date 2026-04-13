import { useEffect, useState } from 'react'
import api from '../api/client'

function OverviewPage() {
  const [status, setStatus] = useState(null)
  const [threats, setThreats] = useState([])
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    const load = async () => {
      const [statusRes, threatsRes, alertsRes] = await Promise.all([
        api.get('/monitor/status'),
        api.get('/detect/threats'),
        api.get('/alerts/'),
      ])
      setStatus(statusRes.data)
      setThreats(threatsRes.data || [])
      setAlerts(alertsRes.data || [])
    }
    load()
  }, [])

  return (
    <div className="container">
      <h2 className="mb-3">CRDS Operations Overview</h2>
      <div className="mb-4">
        <span className={`badge ${status?.is_running ? 'text-bg-success' : 'text-bg-secondary'}`}>
          {status?.is_running ? 'Monitoring Running' : 'Monitoring Stopped'}
        </span>
      </div>
      <div className="row g-3">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h5>Detected Threats</h5>
              <p className="display-6 mb-0">{Array.isArray(threats) ? threats.length : 0}</p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h5>Open Alerts</h5>
              <p className="display-6 mb-0">{Array.isArray(alerts) ? alerts.length : 0}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OverviewPage
