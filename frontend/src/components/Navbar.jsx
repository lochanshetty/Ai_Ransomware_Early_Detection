import { Link, NavLink } from 'react-router-dom'

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div className="container">
        <Link className="navbar-brand" to="/">CRDS Frontend</Link>
        <div className="navbar-nav">
          <NavLink className="nav-link" to="/">Overview</NavLink>
          <NavLink className="nav-link" to="/logs">Logs</NavLink>
          <NavLink className="nav-link" to="/threats">Threats</NavLink>
          <NavLink className="nav-link" to="/honeypot">Honeypot</NavLink>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
