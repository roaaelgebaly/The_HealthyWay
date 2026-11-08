const yn = [
  { value: 'yes', label: 'Yes' },
  { value: 'no', label: 'No' },
]

const freq = [
  { value: 'no', label: 'No' },
  { value: 'Sometimes', label: 'Sometimes' },
  { value: 'Frequently', label: 'Frequently' },
  { value: 'Always', label: 'Always' },
]



export const SECTIONS = [
  {
    title: 'About you',
    fields: [
      { name: 'Gender', label: 'Gender', type: 'select', options: ['Female', 'Male'], def: 'Female' },
      { name: 'Age', label: 'Age', type: 'number', min: 1, max: 100, step: 1, def: 23 },
      { name: 'Height', label: 'Height (meters)', type: 'number', min: 0.5, max: 2.5, step: 0.01, def: 1.65 },
      { name: 'Weight', label: 'Weight (kg)', type: 'number', min: 10, max: 300, step: 0.5, def: 75 },
      { name: 'family_history_with_overweight', label: 'Family history of overweight', type: 'select', options: yn, def: 'yes' },
      { name: 'SMOKE', label: 'Smoking Habits', type: 'select', options: yn, def: 'no' },
    ],
  },
  {
    title: 'Eating habits',
    fields: [
      { name: 'FAVC', label: 'Frequently eat high-calorie food', type: 'select', options: yn, def: 'yes' },
      { name: 'FCVC', label: 'Vegetables with meals', hint: '1 = Never, 2 = Sometimes, 3 = Always', type: 'number', min: 1, max: 3, step: 1, def: 2 },
      { name: 'NCP', label: 'Daily Meals', type: 'number', min: 1, max: 4, step: 1, def: 3 },
      { name: 'CAEC', label: 'Between-Meal Eating', type: 'select', options: freq, def: 'Sometimes' },
      { name: 'CH2O', label: 'Daily water intake', hint: '1 = under 1 L || 2 = 1-2 L || 3 = over 2 L', type: 'number', min: 1, max: 3, step: 1, def: 2 },
      { name: 'SCC', label: 'Calorie Tracking', type: 'select', options: yn, def: 'no' },
      { name: 'CALC', label: 'Alcohol consumption', type: 'select', options: freq, def: 'no' },
    ],
  },
  {
    title: 'Daily movement',
    fields: [
      { name: 'FAF', label: 'Physical activity', hint: '0 = None || 1 = 1-2 days/week || 2 = 2-4 days || 3 = 4-5 days' ,type: 'number', min: 0, max: 3, step: 0.5, def: 1 },
      { name: 'TUE', label: 'Screen Time', hint: '0 = 0-2 hours/day || 1 = 3-5 hours || 2 = over 5 hours', type: 'number', min: 0, max: 2, step: 0.5, def: 1 },
      { name: 'MTRANS', label: 'Transportation Style', type: 'select', options: ['Public_Transportation', 'Automobile', 'Walking', 'Motorbike', 'Bike'], def: 'Public_Transportation' },
    ],
  },
]

export const DEFAULTS = Object.fromEntries(SECTIONS.flatMap((s) => s.fields).map((f) => [f.name, f.def]))
export const NUMERIC = new Set(SECTIONS.flatMap((s) => s.fields).filter((f) => f.type === 'number').map((f) => f.name))
