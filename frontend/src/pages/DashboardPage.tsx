import { Card, CardContent, Grid, Stack, Typography } from '@mui/material'
import { useAuthStore } from '../stores/auth'

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={800}>대시보드</Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="overline" color="text.secondary">로그인 사용자</Typography>
              <Typography fontWeight={700}>{user?.username ?? '-'}</Typography>
              <Typography variant="body2" color="text.secondary">{user?.email ?? '-'}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="overline" color="text.secondary">다음 작업(추천)</Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                1) 관리자 전용 백엔드 엔드포인트 추가(유저/에피소드 전체 조회, 크레딧 조정 등)
                <br />
                2) 여기 화면에서 실시간 잡 모니터링(Job progress) 붙이기
                <br />
                3) S3/정적 리소스 관리(폰트/효과음/유저 업로드)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  )
}
