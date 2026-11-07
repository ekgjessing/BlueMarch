// The 48 contiguous states, keyed by the FIPS id used in us-atlas.
export const STATES: Record<string, { code: string; name: string }> = {
  '01': { code: 'AL', name: 'Alabama' }, '04': { code: 'AZ', name: 'Arizona' }, '05': { code: 'AR', name: 'Arkansas' },
  '06': { code: 'CA', name: 'California' }, '08': { code: 'CO', name: 'Colorado' }, '09': { code: 'CT', name: 'Connecticut' },
  '10': { code: 'DE', name: 'Delaware' }, '12': { code: 'FL', name: 'Florida' }, '13': { code: 'GA', name: 'Georgia' },
  '16': { code: 'ID', name: 'Idaho' }, '17': { code: 'IL', name: 'Illinois' }, '18': { code: 'IN', name: 'Indiana' },
  '19': { code: 'IA', name: 'Iowa' }, '20': { code: 'KS', name: 'Kansas' }, '21': { code: 'KY', name: 'Kentucky' },
  '22': { code: 'LA', name: 'Louisiana' }, '23': { code: 'ME', name: 'Maine' }, '24': { code: 'MD', name: 'Maryland' },
  '25': { code: 'MA', name: 'Massachusetts' }, '26': { code: 'MI', name: 'Michigan' }, '27': { code: 'MN', name: 'Minnesota' },
  '28': { code: 'MS', name: 'Mississippi' }, '29': { code: 'MO', name: 'Missouri' }, '30': { code: 'MT', name: 'Montana' },
  '31': { code: 'NE', name: 'Nebraska' }, '32': { code: 'NV', name: 'Nevada' }, '33': { code: 'NH', name: 'New Hampshire' },
  '34': { code: 'NJ', name: 'New Jersey' }, '35': { code: 'NM', name: 'New Mexico' }, '36': { code: 'NY', name: 'New York' },
  '37': { code: 'NC', name: 'North Carolina' }, '38': { code: 'ND', name: 'North Dakota' }, '39': { code: 'OH', name: 'Ohio' },
  '40': { code: 'OK', name: 'Oklahoma' }, '41': { code: 'OR', name: 'Oregon' }, '42': { code: 'PA', name: 'Pennsylvania' },
  '44': { code: 'RI', name: 'Rhode Island' }, '45': { code: 'SC', name: 'South Carolina' }, '46': { code: 'SD', name: 'South Dakota' },
  '47': { code: 'TN', name: 'Tennessee' }, '48': { code: 'TX', name: 'Texas' }, '49': { code: 'UT', name: 'Utah' },
  '50': { code: 'VT', name: 'Vermont' }, '51': { code: 'VA', name: 'Virginia' }, '53': { code: 'WA', name: 'Washington' },
  '54': { code: 'WV', name: 'West Virginia' }, '55': { code: 'WI', name: 'Wisconsin' }, '56': { code: 'WY', name: 'Wyoming' },
}

export const NAME: Record<string, string> = Object.fromEntries(Object.values(STATES).map((s) => [s.code, s.name]))

/** Pacific states you can start in. */
export const START = ['WA', 'OR', 'CA']
/** Atlantic states that end the march. */
export const GOAL = ['ME', 'NH', 'MA', 'RI', 'CT', 'NY', 'NJ', 'DE', 'MD', 'VA', 'NC', 'SC', 'GA', 'FL']
