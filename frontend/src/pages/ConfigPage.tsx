import { useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { listAssets, uploadAsset, type AssetItem } from '../features/admin/adminApi'

type AssetKind = 'fonts' | 'soundeffects' | 'userassets'

function fmtBytes(n?: number | null) {
  if (n == null) return '-'
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  if (n < 1024 * 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} MB`
  return `${(n / 1024 / 1024 / 1024).toFixed(1)} GB`
}

export default function ConfigPage() {
  const qc = useQueryClient()

  const [kind, setKind] = useState<AssetKind>('fonts')
  const [prefix, setPrefix] = useState('')
  const [uploadKey, setUploadKey] = useState('')
  const [uploadFile, setUploadFile] = useState<File | null>(null)

  const queryKey = useMemo(() => ['admin.assets', kind, prefix], [kind, prefix])
  const assets = useQuery({
    queryKey,
    queryFn: () => listAssets(kind, { prefix: prefix.trim() || undefined }),
  })

  const uploadMut = useMutation({
    mutationFn: (vars: { kind: AssetKind; key: string; file: File }) => uploadAsset(vars.kind, vars.key, vars.file),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['admin.assets'] })
      setUploadKey('')
      setUploadFile(null)
    },
  })

  const items: AssetItem[] = assets.data ?? []

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>설정 / 리소스</Typography>

      <Alert severity="info">
        여기서 S3/정적 리소스(폰트/효과음/유저 업로드) 관리해.
        <br />백엔드 버킷 env가 없으면 /static 아래 로컬 파일로 대체 동작.
      </Alert>

      <Card>
        <CardContent>
          <Tabs value={kind} onChange={(_, v) => setKind(v)}>
            <Tab value="fonts" label="Fonts" />
            <Tab value="soundeffects" label="Sound Effects" />
            <Tab value="userassets" label="User Uploads" />
          </Tabs>
          <Divider sx={{ my: 2 }} />

          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1} alignItems={{ md: 'center' }}>
            <TextField
              size="small"
              label="prefix"
              placeholder="optional"
              value={prefix}
              onChange={(e) => setPrefix(e.target.value)}
              sx={{ width: { xs: '100%', md: 360 } }}
            />
            <Box sx={{ flex: 1 }} />
            <Button size="small" variant="outlined" onClick={() => assets.refetch()} disabled={assets.isFetching}>
              {assets.isFetching ? '갱신 중...' : '새로고침'}
            </Button>
          </Stack>

          <Table size="small" sx={{ mt: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>key</TableCell>
                <TableCell align="right">size</TableCell>
                <TableCell>last_modified</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((a) => (
                <TableRow key={a.key} hover>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{a.key}</TableCell>
                  <TableCell align="right">{fmtBytes(a.size)}</TableCell>
                  <TableCell>{a.last_modified ?? '-'}</TableCell>
                </TableRow>
              ))}
              {!assets.isLoading && items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3}>
                    <Typography variant="body2" color="text.secondary">리소스 없음</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          <Divider sx={{ my: 2 }} />

          <Typography fontWeight={700}>업로드</Typography>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1} alignItems={{ md: 'center' }} sx={{ mt: 1 }}>
            <TextField
              size="small"
              label="key"
              placeholder={kind === 'fonts' ? 'ex) NotoSansKR-Regular.ttf' : kind === 'soundeffects' ? 'ex) click.wav' : 'ex) user_123/avatar.png'}
              value={uploadKey}
              onChange={(e) => setUploadKey(e.target.value)}
              sx={{ width: { xs: '100%', md: 420 } }}
            />
            <Button component="label" variant="outlined" size="small">
              파일 선택
              <input type="file" hidden onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)} />
            </Button>
            <Typography variant="body2" color="text.secondary" sx={{ flex: 1 }}>
              {uploadFile ? uploadFile.name : '선택된 파일 없음'}
            </Typography>
            <Button
              variant="contained"
              size="small"
              disabled={!uploadFile || !uploadKey.trim() || uploadMut.isPending}
              onClick={() => {
                if (!uploadFile) return
                uploadMut.mutate({ kind, key: uploadKey.trim(), file: uploadFile })
              }}
            >
              {uploadMut.isPending ? '업로드 중...' : '업로드'}
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {assets.error && <Alert severity="error">리소스 조회 실패</Alert>}
      {uploadMut.error && <Alert severity="error">업로드 실패</Alert>}

      <Alert severity="warning">
        삭제/이동 같은 관리 기능도 필요하면 /api/admin/assets/* 에 DELETE 엔드포인트 추가해서 붙이면 돼.
      </Alert>
    </Stack>
  )
}
