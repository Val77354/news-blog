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
              checked={selected.includes(country)}
              onChange={() => toggle(country)}
            />
            {country}
          </label>
        ))}
      </div>
    </div>
  )
}
