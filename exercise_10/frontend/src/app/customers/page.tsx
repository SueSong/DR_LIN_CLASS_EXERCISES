'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, User, Mail, Phone, Package, Ticket, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  account_number: string;
  tier: string;
  status: string;
  lifetime_value: number;
  orders?: Order[];
  tickets?: Ticket[];
}

interface Order {
  id: number;
  order_number: string;
  product_name: string;
  amount: number;
  status: string;
  order_date: string;
}

interface Ticket {
  id: number;
  ticket_number: string;
  subject: string;
  status: string;
  priority: string;
  created_at: string;
}

export default function CustomersPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check authentication
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      router.push('/auth/signin');
      return;
    }
    setUser(JSON.parse(userData));
  }, [router]);

  const searchCustomer = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    setCustomer(null);

    try {
      // Get auth token from localStorage
      const userData = localStorage.getItem('user');
      const token = userData ? JSON.parse(userData).token : null;

      const response = await fetch(
        `http://localhost:8000/api/customers/search?q=${encodeURIComponent(searchQuery)}`,
        {
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.status === 401) {
        setError('Authentication required. Please sign in again.');
        router.push('/auth/signin');
        return;
      }

      if (response.status === 404 || response.status === 204) {
        setError('Customer not found');
        return;
      }

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data) {
        setCustomer(data);
      } else {
        setError('Customer not found');
      }
    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.message || 'Failed to search customer. Please check if the backend is running and database is enabled.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchCustomer();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6 flex items-center gap-4">
          <Link
            href="/"
            className="p-2 hover:bg-gray-200 rounded-lg transition"
          >
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Customer Search</h1>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Search by name, email, phone, or account number..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={searchCustomer}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Customer Details */}
        {customer && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Customer Info */}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <User className="w-6 h-6" />
                  Customer Information
                </h2>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <User className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Name</p>
                      <p className="font-semibold">{customer.name}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="font-semibold">{customer.email || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Phone className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Phone</p>
                      <p className="font-semibold">{customer.phone || 'N/A'}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Account Number</p>
                    <p className="font-semibold">{customer.account_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Tier</p>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                      customer.tier === 'platinum' ? 'bg-purple-100 text-purple-800' :
                      customer.tier === 'gold' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {customer.tier.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                      customer.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {customer.status.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Lifetime Value</p>
                    <p className="font-semibold text-lg">${customer.lifetime_value.toFixed(2)}</p>
                  </div>
                </div>
              </div>

              {/* Orders & Tickets */}
              <div className="space-y-6">
                {/* Recent Orders */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <Package className="w-5 h-5" />
                    Recent Orders
                  </h3>
                  {customer.orders && customer.orders.length > 0 ? (
                    <div className="space-y-2">
                      {customer.orders.map((order) => (
                        <div key={order.id} className="border border-gray-200 rounded-lg p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-semibold">{order.order_number}</p>
                              <p className="text-sm text-gray-600">{order.product_name}</p>
                              <p className="text-xs text-gray-500">{order.order_date}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold">${order.amount.toFixed(2)}</p>
                              <span className={`text-xs px-2 py-1 rounded ${
                                order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                                order.status === 'shipped' ? 'bg-blue-100 text-blue-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {order.status}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No recent orders</p>
                  )}
                </div>

                {/* Open Tickets */}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <Ticket className="w-5 h-5" />
                    Open Tickets
                  </h3>
                  {customer.tickets && customer.tickets.length > 0 ? (
                    <div className="space-y-2">
                      {customer.tickets.map((ticket) => (
                        <div key={ticket.id} className="border border-gray-200 rounded-lg p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-semibold">{ticket.ticket_number}</p>
                              <p className="text-sm text-gray-600">{ticket.subject}</p>
                              <p className="text-xs text-gray-500">{ticket.created_at}</p>
                            </div>
                            <div className="text-right">
                              <span className={`text-xs px-2 py-1 rounded ${
                                ticket.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                                ticket.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {ticket.priority}
                              </span>
                              <p className="text-xs text-gray-500 mt-1">{ticket.status}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No open tickets</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!customer && !loading && !error && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Search for a Customer</h3>
            <p className="text-gray-600">
              Enter a customer name, email, phone number, or account number to view their details
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

