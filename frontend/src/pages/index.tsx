'use client';

import React, { useState, useEffect } from 'react';
import { reportsAPI } from '@/utils/api';
import { useAuthStore } from '@/hooks/useStore';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      // Try to load public reports (may fail if auth required)
      const response = await reportsAPI.list({ limit: 10 });
      setReports(response.data.reports || []);
    } catch (error) {
      console.log('Could not load reports (may need auth)');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-3xl">🏙️</span>
              <h1 className="text-2xl font-bold text-gray-900">CivicPulse</h1>
            </div>
            <nav className="flex items-center gap-4">
              {isAuthenticated ? (
                <>
                  <a href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</a>
                  <a href="/report" className="btn-primary">Report Issue</a>
                  <span className="text-sm text-gray-500">{user?.email}</span>
                  <a href="/login" className="text-gray-600 hover:text-gray-900">Logout</a>
                </>
              ) : (
                <>
                  <a href="/login" className="text-gray-600 hover:text-gray-900">Login</a>
                  <a href="/register" className="btn-primary">Sign Up</a>
                </>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Hero */}
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            Build Better Cities Together
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Report civic issues, track their resolution, and hold your municipality accountable. 
            A closed-loop system for transparent governance.
          </p>
          <div className="flex gap-4 justify-center">
            <a href="/report" className="btn-primary text-lg px-8 py-3">
              📸 Report an Issue
            </a>
            {!isAuthenticated && (
              <a href="/register" className="btn-secondary text-lg px-8 py-3">
                Get Started
              </a>
            )}
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="card text-center">
            <div className="text-4xl mb-4">📍</div>
            <h3 className="text-xl font-semibold mb-2">GPS-Accurate Reporting</h3>
            <p className="text-gray-600">
              Auto-capture your location and snap a photo. AI categorizes the issue instantly.
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">Smart Triage</h3>
            <p className="text-gray-600">
              AI-powered categorization with confidence scores. Duplicate detection prevents spam.
            </p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">✅</div>
            <h3 className="text-xl font-semibold mb-2">Verified Resolution</h3>
            <p className="text-gray-600">
              Field workers upload before/after photos. Citizens get notified when issues are fixed.
            </p>
          </div>
        </div>

        {/* Recent Reports */}
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold">Recent Reports</h3>
            <a href="/dashboard" className="text-blue-600 hover:underline">View All →</a>
          </div>
          
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : reports.length > 0 ? (
            <div className="space-y-4">
              {reports.slice(0, 5).map((report) => (
                <div key={report.id} className="border-b pb-4 last:border-0">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium text-gray-900">{report.title}</h4>
                      <p className="text-sm text-gray-500">
                        {report.category || 'Uncategorized'} • {new Date(report.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      report.status === 'resolved' ? 'bg-green-100 text-green-800' :
                      report.status === 'in_progress' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {report.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No reports yet. Be the first to report an issue!
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-gray-400">
              © 2024 CivicPulse. Building transparent, accountable cities.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
