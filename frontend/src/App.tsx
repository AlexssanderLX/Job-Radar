import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Search from './pages/Search'
import Jobs from './pages/Jobs'
import { CatalogPage, HistoryPage, ProfilesPage, SourcesPage, StacksPage } from './pages/Management'
import AccessedLinks from './pages/AccessedLinks'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/search" element={<Search />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/profiles" element={<ProfilesPage />} />
        <Route path="/roles" element={<CatalogPage kind="roles" />} />
        <Route path="/skills" element={<CatalogPage kind="skills" />} />
        <Route path="/stacks" element={<StacksPage />} />
        <Route path="/sources" element={<SourcesPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/accessed-links" element={<AccessedLinks />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
