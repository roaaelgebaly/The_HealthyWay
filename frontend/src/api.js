async function postJson(path, values) {
  let res
  try {
    res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values),
    })
  } catch {
    throw new Error("Can't reach the server. Make sure the API is running on port 8000.")
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const detail = typeof body.detail === 'string'
      ? body.detail
      : 'Some values are out of range or invalid. Please check your answers.'
    throw new Error(detail)
  }
  return res.json()
}

export function analyzeProfile(values) {
  return postJson('/api/analyze', values)
}

export function generateMealPlan(values) {
  return postJson('/api/meal-plan', values)
}

export function generateFitnessPlan(values) {
  return postJson('/api/fitness-plan', values)
}
