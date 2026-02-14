import { useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  LinearProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { getJob, listJobs, type AdminJob } from '../features/admin/adminApi'

function fmtDate(s?: string) {
  if (!s) return '-'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return s
  return d.toLocaleString()
}

function pickProgress(job: AdminJob): number | null {
  const r: any = job.result
  const candidates = [r?.progress, r?.percent, r?.pct, r?.step_progress]
  for (const c of candidates) {
    if (typeof c === 'number' && Number.isFinite(c)) {
      if (c <= 1) return Math.max(0, Math.min(1, c)) * 100
      return Math.max(0, Math.min(100, c))
    }
  }
  return null
}

export default function JobsPage() {
  const [status, setStatus] = useState('pending,started,failed')
  const [offset, setOffset] = useState(0)
  const limit = 50

  const queryKey = useMemo(() => ['admin.jobs', { status, limit, offset }], [status, limit, offset])
  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey,
    queryFn: () => listJobs({ status: status.trim() || undefined, limit, offset }),
    refetchInterval: 2000,
  })

  const [detailJobId, setDetailJobId] = useState<string | null>(null)
  const detail = useQuery({
    queryKey: ['admin.job', detailJobId],
    queryFn: () => getJob(detailJobId as string),
    enabled: !!detailJobId,
    refetchInterval: detailJobId ? 1500 : false,
  })

  const items = data?.items ?? []
  const total = data?.total ?? 0

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>잡 모니터링</Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1} alignItems={{ md: 'center' }}>
            <TextField
              size="small"
              label="status"
              helperText="comma-separated"
              value={status}
              onChange={(e) => { setOffset(0); setStatus(e.target.value) }}
              sx={{ width: { xs: '100%', md: 420 } }}
            />
            <Box sx={{ flex: 1 }} />
            <Button size="small" variant="outlined" onClick={() => refetch()} disabled={isFetching}>
              {isFetching ? '갱신 중...' : '새로고침'}
            </Button>
            <Typography variant="body2" color="text.secondary">
              {isLoading ? '로딩...' : `총 ${total}개`}
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
                <TableCell>job_id</TableCell>
                <TableCell>type</TableCell>
                <TableCell>status</TableCell>
                <TableCell>updated</TableCell>
                <TableCell>progress</TableCell>
                <TableCell>error</TableCell>
                <TableCell align="right">상세</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((j) => {
                const p = pickProgress(j)
                return (
                  <TableRow key={j.job_id} hover>
                    <TableCell sx={{ fontFamily: 'monospace' }}>{j.job_id}</TableCell>
                    <TableCell>{j.job_type}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={j.status}
                        color={j.status === 'failed' ? 'error' : j.status === 'started' ? 'info' : j.status === 'succeeded' ? 'success' : 'default'}
                        variant={j.status === 'pending' ? 'outlined' : 'filled'}
                      />
                    </TableCell>
                    <TableCell>{fmtDate(j.updated_at || j.created_at)}</TableCell>
                    <TableCell sx={{ minWidth: 160 }}>
                      {p == null ? (
                        <Typography variant="body2" color="text.secondary">-</Typography>
                      ) : (
                        <Stack spacing={0.5}>
                          <LinearProgress variant="determinate" value={p} />
                          <Typography variant="caption" color="text.secondary">{p.toFixed(0)}%</Typography>
                        </Stack>
                      )}
                    </TableCell>
                    <TableCell>
                      {j.error ? (
                        <Typography variant="body2" color="error" sx={{ maxWidth: 300, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {j.error}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">-</Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Button size="small" variant="outlined" onClick={() => setDetailJobId(j.job_id)}>
                        보기
                      </Button>
                    </TableCell>
                  </TableRow>
                )
              })}

              {!isLoading && items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7}>
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

      <Alert severity="info">
        이 페이지는 2초 폴링으로 최신 상태를 끌어와.
        <br />progress 값은 job.result 안에 progress/percent/pct 같은 필드가 있으면 자동으로 막대 그려.
      </Alert>

      <Dialog open={!!detailJobId} onClose={() => setDetailJobId(null)} maxWidth="md" fullWidth>
        <DialogTitle>Job 상세</DialogTitle>
        <DialogContent>
          {detail.isLoading ? (
            <Typography>로딩...</Typography>
          ) : detail.error ? (
            <Alert severity="error">상세 조회 실패</Alert>
          ) : (
            <Stack spacing={1}>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{detail.data?.job_id}</Typography>
              <Stack direction="row" spacing={1}>
                <Chip size="small" label={detail.data?.job_type} />
                <Chip size="small" label={detail.data?.status} />
                <Chip size="small" label={`updated: ${fmtDate(detail.data?.updated_at)}`} variant="outlined" />
              </Stack>
              <Typography variant="subtitle2">result</Typography>
              <Box component="pre" sx={{ m: 0, p: 1.5, bgcolor: '#111', color: '#eee', borderRadius: 1, overflow: 'auto', maxHeight: 420 }}>
                {JSON.stringify(detail.data?.result ?? null, null, 2)}
              </Box>
              {detail.data?.error && (
                <>
                  <Typography variant="subtitle2" color="error">error</Typography>
                  <Box component="pre" sx={{ m: 0, p: 1.5, bgcolor: '#2b0d0d', color: '#ffd7d7', borderRadius: 1, overflow: 'auto' }}>
                    {detail.data.error}
                  </Box>
                </>
              )}
            </Stack>
          )}
        </DialogContent>
      </Dialog>
    </Stack>
  )
}
