import { useState } from 'react'
import { DEFAULTS, NUMERIC, SECTIONS } from '../fields'

export default function ProfileForm({ onSubmit, loading }) {
  const [values, setValues] = useState(DEFAULTS)
  const set = (name, v) => setValues((s) => ({ ...s, [name]: v }))

  function handle(e) {
    e.preventDefault()
    const payload = Object.fromEntries(
      Object.entries(values).map(([k, v]) => [k, NUMERIC.has(k) ? Number(v) : v]),
    )
    onSubmit(payload)
  }

  return (
    <form className="card form" onSubmit={handle}>
      {SECTIONS.map((section) => (
        <fieldset key={section.title}>
          <legend>{section.title}</legend>
          <div className="grid">
            {section.fields.map((f) => (
              <label key={f.name} className="field">
                <span>{f.label}</span>
                {f.type === 'select' ? (
                  <select value={values[f.name]} onChange={(e) => set(f.name, e.target.value)}>
                    {f.options.map((o) => {
                      const value = typeof o === 'string' ? o : o.value
                      const label = typeof o === 'string' ? o.replaceAll('_', ' ') : o.label

                      return (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      )
                    })}
                  </select>
                ) : (
                  <input
                    type="number" required min={f.min} max={f.max} step={f.step}
                    value={values[f.name]} onChange={(e) => set(f.name, e.target.value)}
                  />
                )}
                {f.hint && <small>{f.hint}</small>}
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      <button className="btn" type="submit" disabled={loading}>
        {loading ? 'Reading your profile...' : 'Analyze my profile'}
      </button>
    </form>
  )
}