export function Principles({ items }) {
  return (
    <ul className="principles">
      {items.map((p) => (
        <li key={p.text}>
          {p.text}
          {p.source_ids.length > 0 && <sup className="cite"> [{p.source_ids.join(', ')}]</sup>}
        </li>
      ))}
    </ul>
  )
}

export function Sources({ sources }) {
  if (!sources?.length) return null
  return (
    <div className="sources">
      <h3>Sources</h3>
      <ol>
        {sources.map((s) => (
          <li key={s.id} value={s.id}>
            <a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a>
          </li>
        ))}
      </ol>
    </div>
  )
}

export const PLAN_DISCLAIMER =
  'General lifestyle guidance based on public health sources. It is not medical advice. Check with a doctor or registered dietitian before making changes, especially if you have a health condition.'
