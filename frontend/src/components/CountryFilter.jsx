import { COUNTRIES } from '../constants'
import './CountryFilter.css'

export default function CountryFilter({ selected, onChange }) {
  function toggle(country) {
    if (selected.includes(country)) {
      onChange(selected.filter((c) => c !== country))
    } else {
      onChange([...selected, country])
    }
  }

  return (
    <div className="country-filter">
      <span className="country-filter-label">Countries</span>
      <div className="country-filter-list">
        {COUNTRIES.map((country) => (
          <label key={country} className="country-filter-item">
            <input
              type="checkbox"
              className="country-filter-checkbox"
              checked={selected.includes(country)}
              onChange={() => toggle(country)}
            />
            <span className="country-filter-box" aria-hidden="true">
              <svg viewBox="0 0 16 16" className="country-filter-check">
                <polyline points="3,8 7,12 13,4" />
              </svg>
            </span>
            {country}
          </label>
        ))}
      </div>
    </div>
  )
}
