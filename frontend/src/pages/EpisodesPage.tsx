import { Alert, Card, CardContent, Stack, Typography } from '@mui/material'

export default function EpisodesPage() {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>에피소드</Typography>
      <Alert severity="warning">
        현재 /api/episodes 는 "내 에피소드" 위주(로그인 사용자 소유)로 보임.
        관리자 페이지에서는 전체 에피소드 조회/필터/삭제(결과 S3 포함) 같은 기능이 필요해.
      </Alert>
      <Card>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            구현 아이디어:
            <br />- 전체 에피소드 목록(기간/레이아웃/상태/에러)
            <br />- 특정 episode 강제 재시도(retry)
            <br />- 결과물 URL(S3) 확인/삭제
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  )
}
