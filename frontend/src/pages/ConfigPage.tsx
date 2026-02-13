import { Alert, Card, CardContent, Stack, Typography } from '@mui/material'

export default function ConfigPage() {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>설정</Typography>
      <Alert severity="info">
        백엔드에 공개 설정 조회(/api/config)가 있음.
        
        관리자 페이지에서는 운영 설정(예: 크레딧 단가, feature flag 등)을 관리하려면 별도 Admin API가 필요.
      </Alert>
      <Card>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            구현 아이디어:
            <br />- /api/admin/config GET/PUT
            <br />- S3 base url, OAuth 설정 여부, 워커 상태(/api/health/worker)
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  )
}
