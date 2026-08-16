'use client';

import React, { useState } from 'react';
import { reportsAPI } from '@/utils/api';
import { useRouter } from 'next/navigation';

export default function ReportIssuePage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    latitude: 0,
    longitude: 0,
    category: '',
    severity: 3,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);

  // Get current location on mount
  React.useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setLocation(loc);
          setFormData((prev) => ({
            ...prev,
            latitude: loc.lat,
            longitude: loc.lng,
          }));
        },
        (err) => {
          console.error('Error getting location:', err);
          // Default to a sample location
          const defaultLoc = { lat: 40.7128, lng: -74.0060 };
          setLocation(defaultLoc);
          setFormData((prev) => ({
            ...prev,
            latitude: defaultLoc.lat,
            longitude: defaultLoc.lng,
          }));
        }
      );
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await reportsAPI.create(formData);
      setSuccess(true);
      setTimeout(() => {
        router.push('/');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit report');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-green-50">
        <div className="card text-center">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-green-800 mb-2">Report Submitted!</h2>
          <p className="text-gray-600">Redirecting you back...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="card">
          <h1 className="text-2xl font-bold mb-6 text-gray-900">Report an Issue</h1>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="input-field"
                placeholder="e.g., Large pothole on Main Street"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input-field"
                rows={4}
                placeholder="Describe the issue in detail..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="input-field"
                >
                  <option value="">Let AI categorize</option>
                  <option value="pothole">Pothole</option>
                  <option value="garbage">Garbage/Waste</option>
                  <option value="streetlight">Street Light</option>
                  <option value="drain">Drain/Sewer</option>
                  <option value="graffiti">Graffiti</option>
                  <option value="road_damage">Road Damage</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Severity (1-5)
                </label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: parseInt(e.target.value) })}
                  className="input-field"
                >
                  <option value={1}>1 - Low</option>
                  <option value={2}>2 - Minor</option>
                  <option value={3}>3 - Moderate</option>
                  <option value={4}>4 - High</option>
                  <option value={5}>5 - Critical</option>
                </select>
              </div>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <label className="block text-sm font-medium text-blue-900 mb-2">
                Location
              </label>
              {location ? (
                <div className="text-sm text-blue-700">
                  <p>Latitude: {location.lat.toFixed(6)}</p>
                  <p>Longitude: {location.lng.toFixed(6)}</p>
                  <p className="mt-2 text-xs">📍 Auto-captured from your device GPS</p>
                </div>
              ) : (
                <p className="text-sm text-blue-700">Getting your location...</p>
              )}
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                disabled={loading || !location}
                className="btn-primary flex-1"
              >
                {loading ? 'Submitting...' : 'Submit Report'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
