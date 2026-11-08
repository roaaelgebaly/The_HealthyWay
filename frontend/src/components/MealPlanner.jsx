import { useState } from 'react'
import { generateMealPlan } from '../api'
import { PLAN_DISCLAIMER, Principles, Sources } from './PlanParts'

const GOALS = [
  'Lose Weight',
  'Gain Weight',
  'Maintain Weight',
  'Eat Healthier',
  'Build Healthy Habits'
]
const DIETS = [
  'Regular Diet',
  'Vegetarian',
  'Vegan',
  'Pescatarian',
  'Halal Diet',
  'No Specific Diet'
]

export default function MealPlanner({ profile, label }) {
  const [form, setForm] = useState({
    goal: GOALS[0], diet: DIETS[0], meals_per_day: 3, allergies: '', dislikes: '', cuisine: '',
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    setLoading(true); setError(null); setResult(null)
    try { setResult(await generateMealPlan({ profile, label, ...form, meals_per_day: Number(form.meals_per_day) })) }
    catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <section>
      <form className="card form" onSubmit={submit}>
        <div className="grid">
          <label className="field"><span>Goal</span>
            <select value={form.goal} onChange={(e) => set('goal', e.target.value)}>
              {GOALS.map((g) => <option key={g}>{g}</option>)}
            </select></label>
          <label className="field"><span>Diet</span>
            <select value={form.diet} onChange={(e) => set('diet', e.target.value)}>
              {DIETS.map((d) => <option key={d}>{d}</option>)}
            </select></label>
          <label className="field"><span>Meals per day</span>
            <select value={form.meals_per_day} onChange={(e) => set('meals_per_day', e.target.value)}>
              {[3, 4, 5].map((n) => <option key={n}>{n}</option>)}
            </select></label>
          <label className="field"><span>Cuisine (optional)</span>
            <input value={form.cuisine} maxLength={60} placeholder="e.g. Egyptian, Mediterranean"
                   onChange={(e) => set('cuisine', e.target.value)} /></label>
          <label className="field"><span>Allergies (we will avoid these)</span>
            <input value={form.allergies} maxLength={200} placeholder="e.g. peanuts, shellfish"
                   onChange={(e) => set('allergies', e.target.value)} /></label>
          <label className="field"><span>Foods you dislike</span>
            <input value={form.dislikes} maxLength={200} placeholder="e.g. mushrooms"
                   onChange={(e) => set('dislikes', e.target.value)} /></label>
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Creating your 7-day personalized plan...' : 'Create my meal plan'}
        </button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}

      {result && (
        <div className="plan">
          <p className="lead">{result.plan.overview}</p>
          <h3>Guidelines behind this plan</h3>
          <Principles items={result.plan.principles} />

          {result.plan.days.map((d) => (
            <div className="day" key={d.day}>
              <h3>Day {d.day}</h3>
              {d.meals.map((m) => (
                <article className="meal" key={m.type + m.name}>
                  <span className="chip">{m.type}</span>
                  <h4>{m.name}</h4>
                  <p>{m.description}</p>
                  <p className="muted"><strong>Ingredients:</strong> {m.ingredients.join(', ')}</p>
                  <p className="muted">{m.why_it_fits}</p>
                </article>
              ))}
            </div>
          ))}

          <p className="note">{result.plan.safety_note}</p>
          <Sources sources={result.sources} />
          <p className="muted">{PLAN_DISCLAIMER}</p>
        </div>
      )}
    </section>
  )
}
