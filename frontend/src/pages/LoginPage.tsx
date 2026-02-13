import { useState } from 'react'
import { Container, Paper, Stack, TextField, Typography, Button, Alert } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/auth'
import { getMe } from '../features/auth/authApi'

export default function LoginPage() {
  const navigate = useNavigate()
  const setToken = useAuthStore((s) => s.setToken)
  const setUser = useAuthStore((s) => s.setUser)

  const [tokenInput, setTokenInput] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const onSubmit = async () => {
    setError(null)
    setLoading(true)
    try {
      const token = tokenInput.trim()
      if (!token) throw new Error('토큰을 입력해')
      setToken(token)
      const me = await getMe()
      setUser(me)
      navigate('/')
    } catch (e: any) {
      setToken(null)
      setUser(null)
      setError(e?.response?.data?.detail || e?.message || '로그인 실패')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Paper sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h5" fontWeight={700}>EasyShorts 관리자</Typography>
          <Alert severity="info">
            현재 백엔드는 관리자 전용 로그인 엔드포인트가 없어서, 우선 <b>Access Token(JWT)</b>을 붙여 넣는 방식으로 시작해.
            
            다음 단계로 관리자 계정/권한(Role) 기반 로그인으로 확장 가능.
          </Alert>
          <TextField
            label="Access Token"
            value={tokenInput}
            onChange={(e) => setTokenInput(e.target.value)}
            placeholder="Bearer 없이 JWT만"
            multiline
            minRows={4}
          />
          {error && <Alert severity="error">{error}</Alert>}
          <Button variant="contained" onClick={onSubmit} disabled={loading}>
            {loading ? '확인 중...' : '로그인'}
          </Button>
        </Stack>
      </Paper>
    </Container>
  )
}
