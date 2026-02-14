import { useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { listUsers, patchUserActive, patchUserCredit, type AdminUser } from '../features/admin/adminApi'

function fmtDate(s?: string) {
  if (!s) return '-'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return s
  return d.toLocaleString()
}

export default function UsersPage() {
  const qc = useQueryClient()

  const [q, setQ] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 50

  const queryKey = useMemo(() => ['admin.users', { q, limit, offset }], [q, limit, offset])
  const { data, isLoading, error } = useQuery({
    queryKey,
    queryFn: () => listUsers({ q: q.trim() || undefined, limit, offset }),
  })

  const [creditDialogOpen, setCreditDialogOpen] = useState(false)
  const [creditTarget, setCreditTarget] = useState<AdminUser | null>(null)
  const [creditMode, setCreditMode] = useState<'set' | 'add'>('add')
  const [creditAmount, setCreditAmount] = useState<number>(0)

  const creditMut = useMutation({
    mutationFn: (vars: { user_id: string; mode: 'set' | 'add'; amount: number }) =>
      patchUserCredit(vars.user_id, { mode: vars.mode, amount: vars.amount }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['admin.users'] })
      setCreditDialogOpen(false)
    },
  })

  const activeMut = useMutation({
    mutationFn: (vars: { user_id: string; is_active: number }) => patchUserActive(vars.user_id, vars.is_active),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['admin.users'] })
    },
  })

  const openCredit = (u: AdminUser) => {
    setCreditTarget(u)
    setCreditMode('add')
    setCreditAmount(0)
    setCreditDialogOpen(true)
  }

  const items = data?.items ?? []
  const total = data?.total ?? 0

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>유저</Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1} alignItems={{ md: 'center' }}>
            <TextField
              size="small"
              label="검색"
              placeholder="email/username/user_id"
              value={q}
              onChange={(e) => { setOffset(0); setQ(e.target.value) }}
              sx={{ width: { xs: '100%', md: 420 } }}
            />
            <Box sx={{ flex: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {isLoading ? '로딩...' : `총 ${total}명`}
            </Typography>
          </Stack>
        </CardContent>
      </Card>

      {error && <Alert severity="error">{(error as any)?.message ?? '조회 실패'}</Alert>}

      <Card>
        <CardContent>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>user_id</TableCell>
                <TableCell>email</TableCell>
                <TableCell>username</TableCell>
                <TableCell>plan</TableCell>
                <TableCell align="right">credit</TableCell>
                <TableCell>active</TableCell>
                <TableCell>created</TableCell>
                <TableCell align="right">액션</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((u) => (
                <TableRow key={u.user_id} hover>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{u.user_id}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>{u.username}</TableCell>
                  <TableCell>
                    <Chip size="small" label={u.plan ?? '-'} />
                  </TableCell>
                  <TableCell align="right" sx={{ fontVariantNumeric: 'tabular-nums' }}>{u.credit ?? 0}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      color={u.is_active ? 'success' : 'default'}
                      label={u.is_active ? 'active' : 'inactive'}
                      variant={u.is_active ? 'filled' : 'outlined'}
                    />
                  </TableCell>
                  <TableCell>{fmtDate(u.created_at)}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} justifyContent="flex-end">
                      <Button size="small" variant="outlined" onClick={() => openCredit(u)}>크레딧</Button>
                      <Button
                        size="small"
                        color={u.is_active ? 'warning' : 'success'}
                        variant="outlined"
                        onClick={() => activeMut.mutate({ user_id: u.user_id, is_active: u.is_active ? 0 : 1 })}
                        disabled={activeMut.isPending}
                      >
                        {u.is_active ? '비활성' : '활성'}
                      </Button>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}

              {!isLoading && items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8}>
                    <Typography variant="body2" color="text.secondary">결과 없음</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          <Stack direction="row" spacing={1} justifyContent="flex-end" sx={{ mt: 2 }}>
            <Button size="small" variant="outlined" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}>
              이전
            </Button>
            <Button
              size="small"
              variant="outlined"
              disabled={offset + limit >= total}
              onClick={() => setOffset(offset + limit)}
            >
              다음
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Dialog open={creditDialogOpen} onClose={() => setCreditDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>크레딧 조정</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Alert severity="info">
              대상: <b>{creditTarget?.username}</b> ({creditTarget?.email})
              <br />현재: <b>{creditTarget?.credit ?? 0}</b>
            </Alert>
            <TextField
              select
              label="모드"
              SelectProps={{ native: true }}
              value={creditMode}
              onChange={(e) => setCreditMode(e.target.value as any)}
            >
              <option value="add">add (증감)</option>
              <option value="set">set (절대값)</option>
            </TextField>
            <TextField
              label="amount"
              type="number"
              value={creditAmount}
              onChange={(e) => setCreditAmount(Number(e.target.value))}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreditDialogOpen(false)}>취소</Button>
          <Button
            variant="contained"
            disabled={!creditTarget || creditMut.isPending}
            onClick={() => {
              if (!creditTarget) return
              creditMut.mutate({ user_id: creditTarget.user_id, mode: creditMode, amount: creditAmount })
            }}
          >
            {creditMut.isPending ? '적용 중...' : '적용'}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
