import type { User } from '@/api/dbTypes'
import * as v from 'valibot'

export const EditProfileSchema = v.object({
  username: v.pipe(
    v.string(),
    v.minLength(3, 'Username must be at least 3 characters.'),
    v.regex(/^[A-Za-z0-9@.+_-]+$/, 'Use letters, numbers, and @ . + - _ only.'),
  ),
  full_name: v.pipe(v.string(), v.minLength(1, 'Fullname cannot be empty')),
  phone: v.pipe(
    v.string(),
    v.trim(),
    v.regex(/^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/, 'Invalid phone number'),
  ),
  city: v.pipe(v.string(), v.minLength(2, 'City must be at least 2 characters.')),
})

export const ChangePasswordSchema = v.object({
  current_password: v.pipe(v.string(), v.minLength(8, 'Min 8 characters')),
  new_password: v.pipe(v.string(), v.minLength(8, 'Min 8 characters')),
  confirm_password: v.pipe(v.string(), v.minLength(8, 'Min 8 characters')),
})
