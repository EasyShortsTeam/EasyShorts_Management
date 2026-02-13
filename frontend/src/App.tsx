import { CssBaseline } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import AdminLayout from './layouts/AdminLayout'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import UsersPage from './pages/UsersPage'
import EpisodesPage from './pages/EpisodesPage'
import JobsPage from './pages/JobsPage'
import ConfigPage from './pages/ConfigPage'
import CreditsPage from './pages/CreditsPage'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <AdminLayout>
                <DashboardPage />
              </AdminLayout>
            }
          />
          <Route
            path="/users"
            element={
              <AdminLayout>
                <UsersPage />
              </AdminLayout>
            }
          />
          <Route
            path="/episodes"
            element={
              <AdminLayout>
                <EpisodesPage />
              </AdminLayout>
            }
          />
          <Route
            path="/jobs"
            element={
              <AdminLayout>
                <JobsPage />
              </AdminLayout>
            }
          />
          <Route
            path="/config"
            element={
              <AdminLayout>
                <ConfigPage />
              </AdminLayout>
            }
          />
          <Route
            path="/credits"
            element={
              <AdminLayout>
                <CreditsPage />
              </AdminLayout>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
