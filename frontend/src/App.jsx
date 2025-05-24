import React, { useState } from 'react';

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const resp = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 10 }),
      });
      const data = await resp.json();
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-xl bg-white p-6 rounded-2xl shadow-lg">
        <h1 className="text-2xl font-bold mb-4 text-center">Legal Document Search</h1>
        <div className="flex gap-2">
          <input
            type="text"
            className="flex-grow p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your search query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        <ul className="mt-6 space-y-4">
          {results.map((res) => (
            <li key={res.id} className="p-4 border rounded-lg hover:shadow">
              <p className="font-mono text-sm text-gray-600">ID: {res.id}</p>
              <p>Score: {res.score.toFixed(3)}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
