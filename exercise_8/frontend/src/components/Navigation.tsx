"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  FileText, 
  BookOpen, 
  Play, 
  AlertCircle, 
  CheckCircle, 
  RotateCcw, 
  BarChart3,
  Home
} from "lucide-react";

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/playbooks", label: "Playbooks", icon: BookOpen },
  { href: "/run", label: "Start Review", icon: Play },
  { href: "/hitl", label: "Risk Gate", icon: AlertCircle },
  { href: "/finalize", label: "Final Approval", icon: CheckCircle },
  { href: "/replay", label: "Replay", icon: RotateCcw },
  { href: "/reports", label: "Reports", icon: BarChart3 },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-primary-600">
                Legal Document Review
              </h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-4">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || 
                  (item.href !== "/" && pathname.startsWith(item.href));
                
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? "bg-primary-100 text-primary-700"
                        : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className="sm:hidden border-t border-gray-200">
        <div className="px-2 pt-2 pb-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || 
              (item.href !== "/" && pathname.startsWith(item.href));
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center px-3 py-2 text-base font-medium rounded-md ${
                  isActive
                    ? "bg-primary-100 text-primary-700"
                    : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
