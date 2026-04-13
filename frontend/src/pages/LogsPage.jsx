import { useEffect, useState } from 'react'
import api from '../api/client'

function LogsPage() {
  const [logs, setLogs] = useState([])

  useEffect(() => {
    api.post('/detect/analyze', {}).then((res) => {
      setLogs(res.data.results || [])
    })
  }, [])

  return (
    <div className="container">
      <h2 className="mb-3">Detection Results</h2>
      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Log ID</th>
              <th>Suspicious</th>
              <th>Threat</th>
              <th>Score</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((item) => (
              <tr key={item.log_id}>
                <td>{item.log_id}</td>
                <td>{item.is_suspicious ? 'Yes' : 'No'}</td>
                <td>{item.threat_level}</td>
                <td>{Number(item.anomaly_score).toFixed(2)}</td>
                <td>{item.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default LogsPage
