import { Alert, Card, CardContent, Stack, Typography } from '@mui/material'

export default function UsersPage() {
  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>유저</Typography>
      <Alert severity="warning">
        백엔드에 관리자용 "전체 유저 목록" API가 아직 없어 보여.
        
        다음 중 하나로 확장해야 함:
        
        - (권장) /api/admin/users (role=admin만)
        - 또는 DB 직접 접근/리포트
      </Alert>
      <Card>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            구현 아이디어:
            <br />- 유저 검색(email/username)
            <br />- 플랜/크레딧 수정
            <br />- 계정 비활성화
            <br />- 결제/주문(orders) 조회
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  )
}
