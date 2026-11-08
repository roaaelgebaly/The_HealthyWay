import { useState } from 'react'
import { generateFitnessPlan } from '../api'
import { PLAN_DISCLAIMER, Principles, Sources } from './PlanParts'

const GOALS = [
  'Build an Exercise Routine',
  'Improve Endurance',
  'Lose Weight',
  'Maintain Fitness',
  'Stay Active'
]
const SETTINGS = [
  'Home Workouts',
  'Outdoor Activities',
  'Gym Workouts',
  'Mixed Activities'
]
export default function FitnessPlanner({ profile, label }) {
  const [form, setForm] = useState({ goal: GOALS[0], minutes_per_day: 30, setting: SETTINGS[0], limitations: '' })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    setLoading(true); setError(null)
    try { setResult(await generateFitnessPlan({ profile, label, ...form, minutes_per_day: Number(form.minutes_per_day) })) }
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
          <label className="field"><span>Minutes available per day</span>
            <input type="number" min={10} max={90} step={5} required value={form.minutes_per_day}
                   onChange={(e) => set('minutes_per_day', e.target.value)} /></label>
          <label className="field"><span>Where do you prefer to move?</span>
            <select value={form.setting} onChange={(e) => set('setting', e.target.value)}>
              {SETTINGS.map((s) => <option key={s}>{s}</option>)}
            </select></label>
          <label className="field"><span>Injuries or limitations (optional)</span>
            <input value={form.limitations} maxLength={200} placeholder="e.g. sore knee"
                   onChange={(e) => set('limitations', e.target.value)} /></label>
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Finding sources and building your plan...' : 'Create my fitness tasks'}
        </button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}

      {result && (
        <div className="plan">
          <p className="lead">{result.plan.overview}</p>
          <h3>Guidelines behind this plan</h3>
          <Principles items={result.plan.principles} />

          {result.plan.weeks.map((w) => (
            <div className="day" key={w.week}>
              <h3>Week {w.week}: {w.focus}</h3>
              <p className="muted">About {w.weekly_minutes} minutes this week</p>
              {w.tasks.map((t) => (
                <article className="meal" key={t.title}>
                  <span className="chip">{t.intensity}</span>
                  <h4>{t.title}</h4>
                  <p>{t.description}</p>
                  <p className="muted">{t.duration_minutes} minutes, {t.times_per_week}x per week</p>
                </article>
              ))}
            </div>
          ))}

          <ul className="principles">{result.plan.safety_notes.map((n) => <li key={n}>{n}</li>)}</ul>
          <Sources sources={result.sources} />
          <p className="muted">{PLAN_DISCLAIMER}</p>
        </div>
      )}
    </section>
  )
}
