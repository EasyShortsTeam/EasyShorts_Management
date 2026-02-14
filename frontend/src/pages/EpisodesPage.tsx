import { useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
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
import { deleteEpisode, listEpisodes } from '../features/admin/adminApi'

function fmtDate(s?: string) {
  if (!s) return '-'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return s
  return d.toLocaleString()
}

export default function EpisodesPage() {
  const [q, setQ] = useState('')
  const [userId, setUserId] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 50

  const qc = useQueryClient()
  const del = useMutation({
    mutationFn: (episode_id: string) => deleteEpisode(episode_id, { delete_objects: true }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['admin.episodes'] })
    },
  })

  const queryKey = useMemo(() => ['admin.episodes', { q, userId, limit, offset }], [q, userId, limit, offset])
  const { data, isLoading, error } = useQuery({
    queryKey,
    queryFn: () => listEpisodes({
      q: q.trim() || undefined,
      user_id: userId.trim() || undefined,
      limit,
      offset,
    }),
  })

  const items = data?.items ?? []
  const total = data?.total ?? 0

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>에피소드</Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1} alignItems={{ md: 'center' }}>
            <TextField
              size="small"
              label="검색"
              placeholder="episode_id/title/user_id"
              value={q}
              onChange={(e) => { setOffset(0); setQ(e.target.value) }}
              sx={{ width: { xs: '100%', md: 420 } }}
            />
            <TextField
              size="small"
              label="user_id 필터"
              value={userId}
              onChange={(e) => { setOffset(0); setUserId(e.target.value) }}
              sx={{ width: { xs: '100%', md: 320 } }}
            />
            <Box sx={{ flex: 1 }} />
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
                <TableCell>episode_id</TableCell>
                <TableCell>user_id</TableCell>
                <TableCell>title</TableCell>
                <TableCell>layout</TableCell>
                <TableCell>created</TableCell>
                <TableCell>outputs</TableCell>
                <TableCell>error</TableCell>
                <TableCell align="right">actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((e) => (
                <TableRow key={e.episode_id} hover>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{e.episode_id}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{e.user_id ?? '-'}</TableCell>
                  <TableCell>{e.title ?? '-'}</TableCell>
                  <TableCell>{e.series_layout ? <Chip size="small" label={e.series_layout} /> : '-'}</TableCell>
                  <TableCell>{fmtDate(e.created_at)}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      {e.preview_video_url && (
                        <Button size="small" component="a" href={e.preview_video_url} target="_blank" rel="noreferrer">
                          preview
                        </Button>
                      )}
                      {e.video_url && (
                        <Button size="small" component="a" href={e.video_url} target="_blank" rel="noreferrer">
                          video
                        </Button>
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    {e.error ? (
                      <Typography variant="body2" color="error" sx={{ maxWidth: 360, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {e.error}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="text.secondary">-</Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      color="error"
                      variant="outlined"
                      disabled={del.isPending}
                      onClick={() => {
                        const ok = window.confirm(`에피소드 삭제할까?\n\n${e.episode_id}\n\n(DB + S3 결과물 URL까지 삭제 시도)`)
                        if (!ok) return
                        del.mutate(e.episode_id)
                      }}
                    >
                      삭제
                    </Button>
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

      <Alert severity="info">
        에피소드 삭제 버튼은 DB 레코드 + video_url/preview_video_url에 있는 S3 오브젝트까지 삭제를 시도해.
        (S3 권한 없으면 오브젝트 삭제만 실패로 남고 DB는 삭제됨)
      </Alert>
    </Stack>
  )
}
