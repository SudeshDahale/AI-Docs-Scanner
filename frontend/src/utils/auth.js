const TOKEN_KEY = 'documind_token'

export const saveToken = (token) => localStorage.setItem(TOKEN_KEY, token)
export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const removeToken = () => localStorage.removeItem(TOKEN_KEY)
export const isLoggedIn = () => !!getToken()

export const authHeaders = () => ({
  Authorization: `Bearer ${getToken()}`,
})

export const apiFetch = async (url, options = {}) => {
  const res = await fetch(url, {
    ...options,
    headers: {
      ...authHeaders(),
      ...(options.headers || {}),
    },
  })

  if (res.status === 401) {
    removeToken()
    window.location.reload()
  }

  return res
}