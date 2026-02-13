import { useEffect } from 'react'
import type { PropsWithChildren } from 'react'
import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/auth'
import { getMe } from '../features/auth/authApi'

const navItems = [
  { to: '/', label: '대시보드' },
  { to: '/users', label: '유저' },
  { to: '/credits', label: '크레딧' },
  { to: '/episodes', label: '에피소드' },
  { to: '/jobs', label: '잡' },
  { to: '/config', label: '설정' },
]

export default function AdminLayout({ children }: PropsWithChildren) {
  const navigate = useNavigate()
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)
  const logout = useAuthStore((s) => s.logout)

  useEffect(() => {
    const boot = async () => {
      if (!token) {
        navigate('/login', { replace: true })
        return
      }
      if (user) return
      try {
        const me = await getMe()
        setUser(me)
      } catch {
        logout()
        navigate('/login', { replace: true })
      }
    }
    void boot()
  }, [token, user, setUser, logout, navigate])

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f7f7f9' }}>
      <AppBar position="static" elevation={0} color="default">
        <Toolbar sx={{ gap: 2 }}>
          <Typography component={Link} to="/" variant="h6" sx={{ textDecoration: 'none', color: 'inherit', fontWeight: 800 }}>
            EasyShorts Admin
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flex: 1 }}>
            {navItems.map((n) => (
              <Button
                key={n.to}
                component={NavLink}
                to={n.to}
                sx={{
                  textTransform: 'none',
                  '&.active': { fontWeight: 800 },
                }}
              >
                {n.label}
              </Button>
            ))}
          </Box>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            {user ? `${user.username} (${user.email})` : '...'}
          </Typography>
          <Button onClick={() => { logout(); navigate('/login') }} color="inherit">
            로그아웃
          </Button>
        </Toolbar>
      </AppBar>

      <Container sx={{ py: 3 }}>
        {children}
      </Container>
    </Box>
  )
}
