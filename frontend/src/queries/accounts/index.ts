import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type { AxiosError } from 'axios'
import $api from '@/api'
import { accountKeys } from '../keys'
import { computed, toValue, type MaybeRef } from 'vue'
import type {
  ChangePasswordArgs,
  CreateRoleCodesArgs,
  CreateRoleCodesResponse,
  ForgotPasswordArgs,
  ForgotPasswordResponse,
  GetProfileResponse,
  GetRoleCodesArgs,
  GetRoleCodesResponse,
  GetUsersResponse,
  GoogleLoginArgs,
  LoginArgs,
  LoginResponse,
  RegisterArgs,
  RegisterResponse,
  ResetPasswordArgs,
  ResetPasswordResponse,
  UpdateProfileArgs,
  ValidatePasswordArgs,
  ValidatePasswordResponse,
} from '@/api/accounts/types'

export const useProfile = () => {
  return useQuery<GetProfileResponse, AxiosError>({
    queryKey: accountKeys.profile(),
    queryFn: $api.accounts.getProfile,
    retry(failureCount, error) {
      if (error.response?.status === 401) {
        return false
      }
      return true
    },
  })
}

export const useUsers = () => {
  return useQuery<GetUsersResponse, AxiosError>({
    queryKey: accountKeys.users(),
    queryFn: $api.accounts.getUsers,
  })
}

export const useUpdateProfile = () => {
  return useMutation<unknown, AxiosError, UpdateProfileArgs>({
    mutationFn: $api.accounts.updateProfile,
  })
}

export const useDeleteAccount = () => {
  return useMutation<unknown, AxiosError>({
    mutationFn: $api.accounts.deleteAccount,
  })
}

export const useChangePassword = () => {
  return useMutation<unknown, AxiosError, ChangePasswordArgs>({
    mutationFn: $api.accounts.changePassword,
  })
}

export const useLogin = () => {
  return useMutation<LoginResponse, AxiosError, LoginArgs>({
    mutationFn: $api.accounts.login,
  })
}

export const useGoogleLogin = () => {
  return useMutation<unknown, AxiosError, GoogleLoginArgs>({
    mutationFn: $api.accounts.googleLogin,
  })
}

export const useRegister = () => {
  return useMutation<RegisterResponse, AxiosError, RegisterArgs>({
    mutationFn: $api.accounts.register,
  })
}

export const useForgotPassword = () => {
  return useMutation<ForgotPasswordResponse, AxiosError, ForgotPasswordArgs>({
    mutationFn: $api.accounts.forgotPassword,
  })
}

export const useResetPassword = () => {
  return useMutation<ResetPasswordResponse, AxiosError, ResetPasswordArgs>({
    mutationFn: $api.accounts.resetPassword,
  })
}

export const useValidatePassword = (params: ValidatePasswordArgs) => {
  return useMutation<
    ValidatePasswordResponse,
    AxiosError<{ message: string }>,
    ValidatePasswordArgs
  >({
    mutationFn: () => $api.accounts.validatePassword({ uid: params.uid, token: params.token }),
  })
}

export const useRoleCodes = (args: { filter: MaybeRef<GetRoleCodesArgs['filter']> }) => {
  return useQuery<GetRoleCodesResponse, AxiosError>({
    queryKey: computed(() => accountKeys.roleCodes(toValue(args.filter))),
    queryFn: () => $api.accounts.getRoleCodes({ filter: toValue(args.filter) }),
  })
}

export const useGenerateCodes = () => {
  const queryClient = useQueryClient()
  return useMutation<CreateRoleCodesResponse, AxiosError, CreateRoleCodesArgs>({
    mutationFn: $api.accounts.generateCodes,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accountKeys.roleCodes() })
    },
  })
}
