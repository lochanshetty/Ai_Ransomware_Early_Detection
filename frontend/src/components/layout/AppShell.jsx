import { Outlet } from 'react-router-dom'
import DashboardLayout from './DashboardLayout'

function AppShell() {
  return (
    <DashboardLayout>
      <Outlet />
    </DashboardLayout>
  )
}

export default AppShell
