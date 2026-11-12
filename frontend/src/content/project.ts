/**
 * All project copy in one place — edit text here, not in components.
 * Sections mirror the judging criteria (docs/JUDGING_CRITERIA.md).
 * Write for a coach / youth worker, not a data scientist.
 */
export const project = {
  name: 'Sustainable Sports Club',
  pitch:
    'We help community sports clubs in Bosnia and Herzegovina see where their carbon footprint comes from — electricity, away travel and kit — and pick the cheapest changes first, so that going green also makes sport cheaper and more accessible.',

  problem: {
    who: 'Community and youth sports clubs (volunteers, coaches, club boards)',
    decision: 'How to travel to away games, how to cut energy use, and whether to buy new kit',
  },

  data: [
    {
      label: 'Sources',
      value:
        'UK Government GHG Conversion Factors 2025 (OGL v3.0); Ember electricity data via Our World in Data (CC BY 4.0); Open-Meteo (CC BY 4.0); © OpenStreetMap contributors (ODbL); organisers’ synthetic data pack',
    },
    {
      label: 'Coverage',
      value: 'Grid CO₂ intensity for 238 countries 1990–2025; 56 emission factors',
    },
    { label: 'Cleaning', value: 'TBD – what was fixed in the club data, and why' },
  ],

  method: [
    {
      label: 'Approach',
      value:
        'Activity × official emission factor (kWh × grid intensity, km × vehicle factor, kg × material factor)',
    },
    { label: 'Validation', value: 'TBD – baseline vs our model, time-based split' },
    { label: 'Result', value: 'TBD – headline number in plain language' },
  ],

  limitations: [
    'UK vehicle factors used as a proxy for BiH (older fleet → likely underestimates)',
    'Kit weight, car occupancy and minibus size are assumptions — editable in the app',
    'Production (material) factors are averages, not brand-specific',
  ],

  impact: [
    { label: 'Who benefits', value: 'TBD' },
    { label: 'Inclusion', value: 'TBD – youth, girls/women, small or low-resource clubs…' },
    { label: 'Adoption', value: 'TBD – how a club would actually use this, and cost to run' },
  ],

  team: [{ name: 'TBD', role: 'TBD' }],
}
