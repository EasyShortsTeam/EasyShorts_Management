import { Alert, Card, CardContent, Stack, Typography } from '@mui/material'

export default function JobsPage() {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>잡 모니터링</Typography>
      <Alert severity="info">
        백엔드에 /api/jobs/{'{job_id}'} 조회가 있음.
        
        관리자 페이지에서는 "최근 잡 목록"(pending/started/failed) 조회 API를 추가하면 바로 모니터링 가능.
      </Alert>
      <Card>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            구현 아이디어:
            <br />- /api/admin/jobs?status=pending,started (최근 100개)
            <br />- job 상세: progress/result/error
            <br />- cancel 버튼: /api/jobs/{'{job_id}'}/cancel
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  )
}
