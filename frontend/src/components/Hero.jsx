export default function Hero() {
  return (
    <header className="hero">
      <div className="hero-copy">
        <span className="hero-kicker"><span aria-hidden="true">✦</span> A HEALTHIER YOU, ONE ORBIT AT A TIME</span>
        <h1>Your wellbeing<br /><em>is a universe.</em></h1>
        <p>Get to know your habits and discover small, caring ways to feel your best.</p>
        <span className="hero-note"><span aria-hidden="true">✧</span> Personal insights · Gentle guidance · Your pace</span>
      </div>
      <div className="hero-planet" aria-hidden="true">
        <span className="planet-ring" />
        <span className="planet-core"><span>✦</span></span>
        <i className="planet-star star-one">✦</i>
        <i className="planet-star star-two">·</i>
        <i className="planet-star star-three">✧</i>
        <span className="planet-leaf">⌁</span>
      </div>
    </header>
  )
}
