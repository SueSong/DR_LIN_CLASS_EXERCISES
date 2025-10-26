"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-gray-800">
          Legal Document Review System
        </h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            Multi-Agent Document Analysis
          </h2>
          <p className="text-gray-600 mb-4">
            A comprehensive legal document review system featuring:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-600 mb-6">
            <li><strong>Classifier Agent:</strong> Determines document type and sensitivity level</li>
            <li><strong>Extractor Agent:</strong> Identifies clauses, PII, and key terms</li>
            <li><strong>Reviewer Agent:</strong> Assesses risks and policy compliance</li>
            <li><strong>Drafter Agent:</strong> Creates redacted and edited versions</li>
          </ul>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-blue-50 rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-3 text-blue-800">
              🛡️ PII Protection
            </h3>
            <p className="text-gray-700 mb-4">
              Automatic detection and redaction of sensitive personal information including SSN, credit cards, bank accounts, and more.
            </p>
            <ul className="list-disc list-inside text-sm text-gray-600">
              <li>Multiple redaction modes: mask, generalize, refuse</li>
              <li>Context-aware PII detection</li>
              <li>Risk-based classification</li>
            </ul>
          </div>

          <div className="bg-green-50 rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-3 text-green-800">
              ✅ Policy Enforcement
            </h3>
            <p className="text-gray-700 mb-4">
              Automated policy compliance checking with customizable rules and required disclaimers.
            </p>
            <ul className="list-disc list-inside text-sm text-gray-600">
              <li>Forbidden advice detection</li>
              <li>Required disclaimer validation</li>
              <li>Third-party sharing controls</li>
            </ul>
          </div>

          <div className="bg-yellow-50 rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-3 text-yellow-800">
              👥 Human-in-the-Loop (HITL)
            </h3>
            <p className="text-gray-700 mb-4">
              Critical decisions require human approval with complete audit trails.
            </p>
            <ul className="list-disc list-inside text-sm text-gray-600">
              <li>High-risk item review</li>
              <li>Approval workflows</li>
              <li>Decision tracking</li>
            </ul>
          </div>

          <div className="bg-red-50 rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-3 text-red-800">
              🔴 Red Team Testing
            </h3>
            <p className="text-gray-700 mb-4">
              Comprehensive security testing to prevent data leaks and bypass attempts.
            </p>
            <ul className="list-disc list-inside text-sm text-gray-600">
              <li>PII reconstruction attacks</li>
              <li>Encoding bypass detection</li>
              <li>Persona-based attacks</li>
            </ul>
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-semibold mb-3 text-purple-800">
            💬 NEW: AI Chat Assistant
          </h3>
          <p className="text-gray-700 mb-4">
            Interactive Q&A with legal documents featuring real-time security monitoring and prompt injection detection!
          </p>
          <Link 
            href="/chat"
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 inline-block font-medium"
          >
            Try Chat Assistant →
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">
            Quick Start
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Link 
              href="/documents"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 text-center font-medium"
            >
              Upload Document
            </Link>
            <Link 
              href="/chat"
              className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 text-center font-medium"
            >
              Chat Q&A
            </Link>
            <Link 
              href="/review"
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 text-center font-medium"
            >
              Start Review
            </Link>
            <Link 
              href="/hitl"
              className="bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 text-center font-medium"
            >
              HITL Queue
            </Link>
          </div>
        </div>

        <div className="mt-8 bg-gray-100 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2 text-gray-800">
            📊 Key Performance Indicators (KPIs)
          </h3>
          <ul className="list-disc list-inside text-gray-600 space-y-1">
            <li>Clause extraction accuracy</li>
            <li>PII F1 score</li>
            <li>Zero unauthorized disclosure rate</li>
            <li>Review SLA hit-rate</li>
            <li>Red team test pass rate</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

