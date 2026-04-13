import { useEffect, useState } from 'react'
import api from '../api/client'

function ThreatsPage() {
  const [threats, setThreats] = useState([])

  useEffect(() => {
    api.get('/detect/threats').then((res) => {
      setThreats(res.data || [])
    })
  }, [])

  return (
    <div className="container">
      <h2 className="mb-3">Detected Threats</h2>
      <div className="row g-3">
        {threats.map((threat) => (
          <div className="col-md-6" key={threat.id}>
            <div className="card h-100 border-start border-4 border-danger">
              <div className="card-body">
                <h5 className="card-title">{threat.threat_level} Threat</h5>
                <p className="card-text mb-1"><strong>Log:</strong> {threat.security_log}</p>
                <p className="card-text mb-1"><strong>Score:</strong> {Number(threat.confidence_score).toFixed(2)}</p>
                <p className="card-text mb-0"><strong>Reason:</strong> {threat.reason}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ThreatsPage
