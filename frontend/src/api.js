export async function api(path, options = {}) {
  const token = sessionStorage.getItem('eco-token');
  const response = await fetch(`/api${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    if (response.status === 401 && !path.startsWith('/auth/')) window.dispatchEvent(new Event('session-expired'));
    throw new Error(Array.isArray(body.detail) ? body.detail.map(x => `${x.loc.slice(1).join(' ')}: ${x.msg}`).join('; ') : body.detail || 'Unable to connect. Check that the backend is running.');
  }
  return response.status === 204 ? null : response.json();
}
export const send = (method, body) => ({ method, body: JSON.stringify(body) });
