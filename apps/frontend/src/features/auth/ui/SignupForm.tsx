import { useCallback, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signup } from '../../../shared/api/authApi'
import type { ApiError } from '../../../shared/types/api'
import type { SignupFormData } from '../types'
import {
  validateEmail,
  validateNickname,
  validatePassword,
  validatePasswordConfirm,
} from '../lib/validation'

export function SignupForm() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
    password: '',
    passwordConfirm: '',
    nickname: '',
  })
  const [errors, setErrors] = useState<Partial<Record<keyof SignupFormData, string>>>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setErrors((prev) => ({ ...prev, [name]: undefined }))
    setServerError(null)
  }, [])

  const validateForm = useCallback((): boolean => {
    const newErrors: Partial<Record<keyof SignupFormData, string>> = {}

    const emailError = validateEmail(formData.email)
    if (emailError) newErrors.email = emailError

    const passwordError = validatePassword(formData.password)
    if (passwordError) newErrors.password = passwordError

    const confirmError = validatePasswordConfirm(
      formData.password,
      formData.passwordConfirm
    )
    if (confirmError) newErrors.passwordConfirm = confirmError

    const nicknameError = validateNickname(formData.nickname)
    if (nicknameError) newErrors.nickname = nicknameError

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [formData])

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      if (!validateForm()) return

      setIsLoading(true)
      setServerError(null)

      try {
        await signup({
          email: formData.email,
          password: formData.password,
          nickname: formData.nickname,
        })
        navigate('/login', {
          state: { message: '회원가입이 완료되었습니다. 로그인해주세요.' },
        })
      } catch (err) {
        const apiError = err as ApiError
        if (apiError.code === 'EMAIL_ALREADY_EXISTS') {
          setErrors({ email: apiError.message })
        } else {
          setServerError(apiError.message || '회원가입에 실패했습니다.')
        }
      } finally {
        setIsLoading(false)
      }
    },
    [formData, navigate, validateForm]
  )

  return (
    <form onSubmit={handleSubmit} className="signup-form">
      <h2>회원가입</h2>

      {serverError && (
        <div className="signup-form__error" role="alert">
          {serverError}
        </div>
      )}

      <div className="signup-form__group">
        <label htmlFor="email">이메일</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          disabled={isLoading}
          autoComplete="email"
          aria-invalid={!!errors.email}
          aria-errormessage={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <span id="email-error" className="signup-form__field-error">
            {errors.email}
          </span>
        )}
      </div>

      <div className="signup-form__group">
        <label htmlFor="password">비밀번호</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          disabled={isLoading}
          autoComplete="new-password"
          aria-invalid={!!errors.password}
          aria-errormessage={errors.password ? 'password-error' : undefined}
        />
        {errors.password && (
          <span id="password-error" className="signup-form__field-error">
            {errors.password}
          </span>
        )}
      </div>

      <div className="signup-form__group">
        <label htmlFor="passwordConfirm">비밀번호 확인</label>
        <input
          type="password"
          id="passwordConfirm"
          name="passwordConfirm"
          value={formData.passwordConfirm}
          onChange={handleChange}
          disabled={isLoading}
          autoComplete="new-password"
          aria-invalid={!!errors.passwordConfirm}
          aria-errormessage={
            errors.passwordConfirm ? 'passwordConfirm-error' : undefined
          }
        />
        {errors.passwordConfirm && (
          <span id="passwordConfirm-error" className="signup-form__field-error">
            {errors.passwordConfirm}
          </span>
        )}
      </div>

      <div className="signup-form__group">
        <label htmlFor="nickname">닉네임</label>
        <input
          type="text"
          id="nickname"
          name="nickname"
          value={formData.nickname}
          onChange={handleChange}
          disabled={isLoading}
          autoComplete="nickname"
          aria-invalid={!!errors.nickname}
          aria-errormessage={errors.nickname ? 'nickname-error' : undefined}
        />
        {errors.nickname && (
          <span id="nickname-error" className="signup-form__field-error">
            {errors.nickname}
          </span>
        )}
      </div>

      <button type="submit" disabled={isLoading} className="signup-form__submit">
        {isLoading ? '가입 중...' : '회원가입'}
      </button>

      <p className="signup-form__footer">
        이미 계정이 있으신가요? <Link to="/login">로그인</Link>
      </p>
    </form>
  )
}
