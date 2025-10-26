"use client";

import Link from "next/link";
import { 
  FileText, 
  BookOpen, 
  Play, 
  AlertCircle, 
  CheckCircle, 
  RotateCcw, 
  BarChart3,
  ArrowRight
} from "lucide-react";

const features = [
  {
    title: "Upload Documents",
    description: "Upload legal contracts (NDA, MSA, DPA) for automated review and risk assessment.",
    icon: FileText,
    href: "/documents",
    color: "bg-blue-500",
  },
  {
    title: "Manage Playbooks",
    description: "Create and configure policy playbooks that guide the review process.",
    icon: BookOpen,
    href: "/playbooks",
    color: "bg-purple-500",
  },
  {
    title: "Start Review",
    description: "Initiate multi-agent review workflows with different orchestration patterns.",
    icon: Play,
    href: "/run",
    color: "bg-green-500",
  },
  {
    title: "Risk Gate (HITL)",
    description: "Human-in-the-loop approval for high-risk clauses before proceeding.",
    icon: AlertCircle,
    href: "/hitl",
    color: "bg-orange-500",
  },
  {
    title: "Final Approval",
    description: "Review and approve the final redlined document and summary memo.",
    icon: CheckCircle,
    href: "/finalize",
    color: "bg-teal-500",
  },
  {
    title: "Replay & Debug",
    description: "Replay previous runs to debug and analyze agent behavior.",
    icon: RotateCcw,
    href: "/replay",
    color: "bg-indigo-500",
  },
  {
    title: "Reports & Metrics",
    description: "View SLOs, quality metrics, and cost analysis across all reviews.",
    icon: BarChart3,
    href: "/reports",
    color: "bg-pink-500",
  },
];

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Legal Document Review Orchestrator
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Exercise 8: Multi-agent HITL contract redlining with Manager–Worker, 
          Reviewer/Referee, and Blackboard patterns
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.href}
              href={feature.href}
              className="card hover:shadow-xl transition-shadow group"
            >
              <div className="flex items-start space-x-4">
                <div className={`${feature.color} p-3 rounded-lg text-white`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {feature.description}
                  </p>
                  <div className="flex items-center text-primary-600 text-sm font-medium">
                    <span>Get started</span>
                    <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick Start Section */}
      <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Start Guide</h2>
        <ol className="space-y-3 text-gray-700">
          <li className="flex items-start">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
              1
            </span>
            <div>
              <strong>Upload a document</strong> – Start by uploading a legal contract (NDA, MSA, or DPA)
            </div>
          </li>
          <li className="flex items-start">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
              2
            </span>
            <div>
              <strong>Create a playbook</strong> – Define policies and rules for the review process
            </div>
          </li>
          <li className="flex items-start">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
              3
            </span>
            <div>
              <strong>Start a review</strong> – Select an agent path and initiate the multi-agent workflow
            </div>
          </li>
          <li className="flex items-start">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
              4
            </span>
            <div>
              <strong>Approve at gates</strong> – Review and approve at Risk Gate and Final Approval stages
            </div>
          </li>
          <li className="flex items-start">
            <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
              5
            </span>
            <div>
              <strong>Export results</strong> – Download the redlined document and summary memo
            </div>
          </li>
        </ol>
      </div>

      {/* Patterns Section */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Agent Patterns</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Manager–Worker (task decomposition)
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Reviewer/Referee (checklist-driven)
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Planner–Executor (multi-step plans)
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
              Tool Router (policy lookup vs LLM)
            </li>
          </ul>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Features</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Blackboard/Shared Memory
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Human-in-the-Loop Gates
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Clause-level Risk Assessment
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Replay & Observability
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
