import { Box, Card, CardContent, Chip, LinearProgress, Stack, Typography } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { listJobs, type AdminJob } from '../features/admin/adminApi'
import { useAuthStore } from '../stores/auth'

function fmtDate(s?: string) {
  if (!s) return '-'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return s
  return d.toLocaleString()
}

function pickProgress(job: AdminJob): number | null {
  const r: any = job.result
  const candidates = [r?.progress, r?.percent, r?.pct]
  for (const c of candidates) {
    if (typeof c === 'number' && Number.isFinite(c)) {
      if (c <= 1) return Math.max(0, Math.min(1, c)) * 100
      return Math.max(0, Math.min(100, c))
    }
  }
  return null
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  const recentJobs = useQuery({
    queryKey: ['admin.jobs.recent'],
    queryFn: () => listJobs({ limit: 8, offset: 0 }),
    refetchInterval: 3000,
  })

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>대시보드</Typography>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' },
          gap: 2,
        }}
      >
        <Card>
          <CardContent>
            <Typography variant="overline" color="text.secondary">로그인 사용자</Typography>
            <Typography fontWeight={700}>{user?.username ?? '-'}</Typography>
            <Typography variant="body2" color="text.secondary">{user?.email ?? '-'}</Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Chip size="small" label={user?.plan ?? '-'} />
              <Chip size="small" label={`credit: ${user?.credit ?? 0}`} variant="outlined" />
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="overline" color="text.secondary">최근 잡</Typography>

            {recentJobs.isLoading ? (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>로딩...</Typography>
            ) : recentJobs.error ? (
              <Typography variant="body2" color="error" sx={{ mt: 1 }}>잡 조회 실패</Typography>
            ) : (
              <Stack spacing={1} sx={{ mt: 1 }}>
                {(recentJobs.data?.items ?? []).map((j) => {
                  const p = pickProgress(j)
                  return (
                    <Stack key={j.job_id} direction={{ xs: 'column', md: 'row' }} spacing={1} alignItems={{ md: 'center' }}>
                      <Typography sx={{ fontFamily: 'monospace', minWidth: 180 }} variant="body2">{j.job_id}</Typography>
                      <Chip size="small" label={j.status} />
                      <Typography variant="body2" color="text.secondary" sx={{ flex: 1 }}>
                        {j.job_type} · {fmtDate(j.updated_at || j.created_at)}
                      </Typography>
                      {p != null && (
                        <Stack sx={{ width: { xs: '100%', md: 160 } }} spacing={0.5}>
                          <LinearProgress variant="determinate" value={p} />
                          <Typography variant="caption" color="text.secondary">{p.toFixed(0)}%</Typography>
                        </Stack>
                      )}
                    </Stack>
                  )
                })}

                {(recentJobs.data?.items?.length ?? 0) === 0 && (
                  <Typography variant="body2" color="text.secondary">잡이 아직 없어.</Typography>
                )}
              </Stack>
            )}
          </CardContent>
        </Card>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="overline" color="text.secondary">바로가기</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            유저/에피소드/잡 페이지는 이제 실제 /api/admin/* 엔드포인트를 붙여놨어.
            <br />설정 탭은 S3/정적 리소스(폰트/효과음/유저 업로드) 관리 UI로 확장하면 돼.
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  )
}
