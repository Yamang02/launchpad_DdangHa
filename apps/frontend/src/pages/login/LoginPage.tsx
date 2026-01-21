import { useLocation } from 'react-router-dom'

export function LoginPage() {
  const { state } = useLocation() as { state?: { message?: string } }

  return (
    <main className="login-page">
      <h1>로그인</h1>
      {state?.message && <p className="login-page__message">{state.message}</p>}
      <p>로그인 폼은 002-login 스펙에서 구현 예정입니다.</p>
    </main>
  )
}
