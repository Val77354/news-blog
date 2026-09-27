import { CATEGORIES } from '../constants'
import './CategoryTabs.css'

export default function CategoryTabs({ active, onChange }) {
  const tabs = ['All', ...CATEGORIES]

  return (
    <div className="category-tabs">
      {tabs.map((tab) => {
        const isActive = tab === 'All' ? active === null : active === tab
        return (
          <button
            key={tab}
            type="button"
            className={`category-tab${isActive ? ' active' : ''}`}
            onClick={() => onChange(tab === 'All' ? null : tab)}
          >
            {tab}
          </button>
        )
      })}
    </div>
  )
}
