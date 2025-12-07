import React, { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`)
      const data = await response.json()
      setStats(data)
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResults([])

    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim(), limit: 20 }),
      })

      if (!response.ok) {
        throw new Error('Search failed')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError('Failed to search images. Make sure the backend is running and images are indexed.')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReindex = async () => {
    if (!confirm('This will reindex all images. This may take a while. Continue?')) {
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/reindex`, {
        method: 'POST',
      })
      if (response.ok) {
        await fetchStats()
        alert('Reindexing completed!')
      }
    } catch (err) {
      alert('Reindexing failed. Check console for details.')
      console.error('Reindex error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🔍 AI Photo Search</h1>
          <p className="subtitle">Search your photo library using natural language</p>
        </header>

        {stats && (
          <div className="stats">
            <span>
              {stats.indexed
                ? `📸 ${stats.total_images} images indexed`
                : '⚠️ No images indexed yet'}
            </span>
            {stats.indexed && (
              <span className="path">from {stats.photo_library_path}</span>
            )}
            <button onClick={handleReindex} className="reindex-btn" disabled={loading}>
              {loading ? 'Processing...' : 'Reindex'}
            </button>
          </div>
        )}

        <form onSubmit={handleSearch} className="search-form">
          <div className="search-box">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for photos... (e.g., 'sunset at the beach', 'dogs playing', 'birthday party')"
              className="search-input"
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading || !query.trim()}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && <div className="error">{error}</div>}

        {results.length > 0 && (
          <div className="results-header">
            <h2>Found {results.length} results</h2>
          </div>
        )}

        <div className="gallery">
          {results.map((result, index) => (
            <div key={index} className="image-card">
              <div className="image-wrapper">
                <img
                  src={`${API_BASE}/image?path=${encodeURIComponent(result.path)}`}
                  alt={`Result ${index + 1}`}
                  onError={(e) => {
                    e.target.style.display = 'none'
                    e.target.nextSibling.style.display = 'flex'
                  }}
                />
                <div className="image-error" style={{ display: 'none' }}>
                  <span>Unable to load image</span>
                  <small>{result.path}</small>
                </div>
              </div>
              <div className="image-info">
                <div className="score">Score: {result.score.toFixed(3)}</div>
                <div className="path-text" title={result.path}>
                  {result.path.split('/').pop()}
                </div>
              </div>
            </div>
          ))}
        </div>

        {!loading && results.length === 0 && query && (
          <div className="empty-state">
            <p>No results found. Try a different search query.</p>
          </div>
        )}

        {!loading && !query && results.length === 0 && (
          <div className="empty-state">
            <p>Enter a search query to find matching photos in your library.</p>
            <div className="examples">
              <strong>Example queries:</strong>
              <ul>
                <li>"sunset over mountains"</li>
                <li>"people smiling"</li>
                <li>"food on a table"</li>
                <li>"cats and dogs"</li>
                <li>"beach vacation"</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

