import { useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

type CreditUserSummary = {
  user_id: string
  email: string
  username: string
  credits_balance: number
  updated_at: string
}

type CreditLedgerEntry = {
  id: string
  user_id: string
  delta: number
  reason: string
  created_at: string
  actor?: string | null
}

type CreditUserDetail = {
  user_id: string
  email: string
  username: string
  credits_balance: number
  updated_at: string
  ledger: CreditLedgerEntry[]
}

export default function CreditsPage() {
  const [q, setQ] = useState('')
  const [selectedUserId, setSelectedUserId] = useState<string>('1')

  const usersQuery = useQuery({
    queryKey: ['creditUsers', q],
    queryFn: async () => {
      const { data } = await api.get<CreditUserSummary[]>('/api/admin/credits/users', {
        params: q ? { q } : undefined,
      })
      return data
    },
  })

  const userDetailQuery = useQuery({
    queryKey: ['creditUser', selectedUserId],
    queryFn: async () => {
      const { data } = await api.get<CreditUserDetail>(`/api/admin/credits/users/${selectedUserId}`)
      return data
    },
    enabled: Boolean(selectedUserId),
  })

  const [delta, setDelta] = useState<number>(10)
  const [reason, setReason] = useState<string>('관리자 조정')

  const adjustMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post<{ status: 'ok'; user: CreditUserDetail }>(
        `/api/admin/credits/users/${selectedUserId}/adjust`,
        { delta, reason },
      )
      return data
    },
    onSuccess: async () => {
      await Promise.all([
        usersQuery.refetch(),
        userDetailQuery.refetch(),
      ])
    },
  })

  const selected = userDetailQuery.data

  const selectedLabel = useMemo(() => {
    if (!selected) return ''
    return `${selected.username} (${selected.email})`
  }, [selected])

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>유저 크레딧</Typography>

      <Alert severity="info">
        현재는 DB 연동 전이라 백엔드가 in-memory(임시)로 동작할 수 있어.
        <br />실서비스용은 반드시 DB(예: Postgres) + 감사로그/권한체크로 교체해야 함.
      </Alert>

      <Card>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
            <TextField
              label="유저 검색 (id/email/username)"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              fullWidth
            />
            <Button variant="outlined" onClick={() => usersQuery.refetch()} disabled={usersQuery.isFetching}>
              검색
            </Button>
          </Stack>

          <Divider sx={{ my: 2 }} />

          <Stack spacing={1}>
            <Typography variant="subtitle2" color="text.secondary">유저 목록</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {(usersQuery.data ?? []).map((u) => (
                <Button
                  key={u.user_id}
                  size="small"
                  variant={u.user_id === selectedUserId ? 'contained' : 'outlined'}
                  onClick={() => setSelectedUserId(u.user_id)}
                >
                  {u.username} · {u.credits_balance}
                </Button>
              ))}
            </Stack>
            {usersQuery.isError && (
              <Alert severity="error">유저 목록을 불러오지 못했어.</Alert>
            )}
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={800}>선택 유저</Typography>
          <Typography variant="body2" color="text.secondary">{selectedLabel || '...'} </Typography>

          <Box sx={{ mt: 2 }}>
            <Typography variant="h4" fontWeight={900}>
              {selected ? selected.credits_balance : '—'}
              <Typography component="span" sx={{ ml: 1 }} color="text.secondary" variant="body1">
                credits
              </Typography>
            </Typography>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
            <TextField
              label="증감(delta)"
              type="number"
              value={delta}
              onChange={(e) => setDelta(Number(e.target.value))}
              sx={{ width: 180 }}
            />
            <TextField
              label="사유(reason)"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              fullWidth
            />
            <Button
              variant="contained"
              onClick={() => adjustMutation.mutate()}
              disabled={adjustMutation.isPending || !selectedUserId}
            >
              크레딧 조정
            </Button>
          </Stack>

          {adjustMutation.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              크레딧 조정 실패
            </Alert>
          )}

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" color="text.secondary">변경 이력(최근 50)</Typography>
          <Stack spacing={1} sx={{ mt: 1 }}>
            {(selected?.ledger ?? []).length === 0 && (
              <Typography variant="body2" color="text.secondary">이력 없음</Typography>
            )}
            {(selected?.ledger ?? []).map((e) => (
              <Box key={e.id} sx={{ p: 1.2, bgcolor: 'white', borderRadius: 1, border: '1px solid #eee' }}>
                <Typography fontWeight={800}>
                  {e.delta > 0 ? `+${e.delta}` : e.delta}
                  <Typography component="span" sx={{ ml: 1 }} color="text.secondary" fontWeight={400}>
                    {e.reason}
                  </Typography>
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {e.created_at} · actor: {e.actor ?? '—'}
                </Typography>
              </Box>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  )
}
