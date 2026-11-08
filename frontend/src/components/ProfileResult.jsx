const pretty = (s) => s.replaceAll('_', ' ')

export default function ProfileResult({ data }) {
  const { label, bmi, narrative: n, llm_error } = data

  return (
    <section>
      <div className="result">
        <div className="orb" aria-hidden="true">{bmi}</div>
        <div>
          <small>Estimate for your profile</small>
          <h2>{pretty(label)}</h2>
          <small>BMI {bmi}, calculated from your height and weight</small>
        </div>
      </div>

      {llm_error && (
        <p className="note" role="status">
          The detailed explanation is in basic mode because the AI service is unavailable ({llm_error}).
          Your result above is unaffected.
        </p>
      )}

      <p className="lead">{n.summary}</p>

      <h3>What influenced this result most</h3>
      {n.key_factors.map((f) => (
        <div className="factor" key={f.factor}>
          <b>{f.factor}</b>
          <br />
          {f.note}
          {f.tip && <span className="tip"><strong>Tip:</strong> {f.tip}</span>}
        </div>
      ))}

      <p className="note">{n.when_to_talk_to_a_professional}</p>
    </section>
  )
}
