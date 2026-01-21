export function validateEmail(email: string): string | null {
  if (!email) return '이메일을 입력해주세요.'
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) return '올바른 이메일 형식이 아닙니다.'
  return null
}

export function validatePassword(password: string): string | null {
  if (!password) return '비밀번호를 입력해주세요.'
  if (password.length < 8) return '비밀번호는 8자 이상이어야 합니다.'
  if (!/[A-Za-z]/.test(password)) return '비밀번호에 영문자가 포함되어야 합니다.'
  if (!/\d/.test(password)) return '비밀번호에 숫자가 포함되어야 합니다.'
  return null
}

export function validatePasswordConfirm(
  password: string,
  confirm: string
): string | null {
  if (!confirm) return '비밀번호 확인을 입력해주세요.'
  if (password !== confirm) return '비밀번호가 일치하지 않습니다.'
  return null
}

export function validateNickname(nickname: string): string | null {
  if (!nickname) return '닉네임을 입력해주세요.'
  if (nickname.length < 2) return '닉네임은 2자 이상이어야 합니다.'
  if (nickname.length > 20) return '닉네임은 20자 이하여야 합니다.'
  return null
}
