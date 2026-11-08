import { useState } from 'react'
import Hero from './components/Hero'
import FitnessPlanner from './components/FitnessPlanner'
import MealPlanner from './components/MealPlanner'
import ProfileForm from './components/ProfileForm'
import ProfileResult from './components/ProfileResult'
import { analyzeProfile } from './api'

const PAGES = [
  { id: 'profile', title: 'My profile', icon: '✦', hint: 'Your wellness information' },
  { id: 'meals', title: 'Meal planner', icon: '◉', hint: 'Create and manage your meal plans' },
  { id: 'fitness', title: 'Move your way', icon: '↗', hint: 'Create and manage your meal plans' },
]

const DISCLAIMER =
  'The Healthy Way offers general lifestyle information and model-based estimates. It is not medical advice, a diagnosis, or a treatment plan. Talk to a doctor or registered dietitian about your personal health.'

export default function App() {
  const [data, setData] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [page, setPage] = useState('profile')
  const profileKey = profile ? JSON.stringify(profile) : ''

  async function onSubmit(values) {
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeProfile(values)
      setProfile(values)
      setData(result)
      setPage('profile')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="site-shell">
      <header className="topbar">
        <button className="brand" type="button" onClick={() => setPage('profile')} aria-label="The Healthy Way home">
          <span className="brand-orbit" aria-hidden="true"><span /></span>
          <span>The Healthy <b>Way</b></span>
        </button>
        <nav className="main-nav" aria-label="Main navigation">
          {PAGES.map((item) => (
            <button
              key={item.id}
              type="button"
              className="nav-link"
              aria-current={page === item.id ? 'page' : undefined}
              disabled={item.id !== 'profile' && !data}
              title={!data && item.id !== 'profile' ? 'Analyze your profile to unlock this page' : undefined}
              onClick={() => setPage(item.id)}
            >
              <span aria-hidden="true">{item.icon}</span> {item.title}
            </button>
          ))}
        </nav>
      </header>

      <main className="page">
        <section hidden={page !== 'profile'}>
          <Hero />

          <div className="welcome-row">
            <div>
              <h2 className="eyebrow">Your health, Your goals, Your way.</h2>
              <p className="muted">Start with your profile, then explore ideas made to fit your everyday life.</p>
            </div>
            <span className="welcome-spark" aria-hidden="true">✦</span>
          </div>

          <div className="profile-layout">
            <div className="profile-main">
              <div className="section-heading">
                <span className="section-orbit" aria-hidden="true">01</span>
                <div>
                  <span className="eyebrow">FIRST, LET’S GET TO KNOW YOU</span>
                  <h2>Your health profile</h2>
                </div>
              </div>
              <ProfileForm onSubmit={onSubmit} loading={loading} />
              {error && <p className="error" role="alert">{error}</p>}
              {data && <div className="results card"><ProfileResult data={data} /></div>}
            </div>

            <aside className="feature-sidebar" aria-label="Explore The Healthy Way">
              <span className="eyebrow">YOUR NEXT STEPS</span>
              {PAGES.slice(1).map((item, index) => (
                <button
                  className={`feature-card feature-card-${index + 1}`}
                  key={item.id}
                  type="button"
                  disabled={!data}
                  onClick={() => setPage(item.id)}
                >
                  <span className="feature-icon" aria-hidden="true">{item.icon}</span>
                  <span className="feature-copy">
                    <strong>{item.title}</strong>
                    <small>{data ? item.hint : 'Complete your data to unlock'}</small>
                  </span>
                  <span className="feature-arrow" aria-hidden="true">↗</span>
                </button>
              ))}
              <p className="sidebar-note">Your plans are tailored to your profile and preferences.</p>
            </aside>
          </div>
        </section>

        {data && (
          <>
            <section className="planner-page" hidden={page !== 'meals'}>
              <PageHeading icon="◉" eyebrow="NOURISH YOUR JOURNEY" title="Meal planner"
                description="Simple, balanced meal ideas shaped around your preferences." />
              <MealPlanner key={`meals-${profileKey}`} profile={profile} label={data.label} />
            </section>
            <section className="planner-page" hidden={page !== 'fitness'}>
              <PageHeading icon="↗" eyebrow="FIND YOUR OWN RHYTHM" title="Move your way"
                description="A gradual activity plan that starts where you are." />
              <FitnessPlanner key={`fitness-${profileKey}`} profile={profile} label={data.label} />
            </section>
          </>
        )}

        <footer className="muted">{DISCLAIMER}</footer>
      </main>
    </div>
  )
}

function PageHeading({ icon, eyebrow, title, description }) {
  return (
    <div className="page-heading">
      <span className="page-heading-icon" aria-hidden="true">{icon}</span>
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <span className="heading-star" aria-hidden="true">✦</span>
    </div>
  )
}
