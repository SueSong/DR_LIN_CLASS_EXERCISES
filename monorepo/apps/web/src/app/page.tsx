/**
 * AI Agent Console - Main Dashboard
 * Placeholder for Week 4 enhancement with full agent console functionality
 */

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Activity, Database, FileText, Globe, Settings, Zap } from 'lucide-react'

interface ToolLog {
  id: string
  timestamp: string
  tool: string
  operation: string
  status: 'success' | 'error' | 'pending'
  duration?: number
  details?: string
}

export default function AgentConsole() {
  const [toolLogs, setToolLogs] = useState<ToolLog[]>([])
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking')

  // Mock tool logs for demonstration
  useEffect(() => {
    const mockLogs: ToolLog[] = [
      {
        id: '1',
        timestamp: new Date().toISOString(),
        tool: 'http_fetch',
        operation: 'GET https://api.example.com/data',
        status: 'success',
        duration: 245,
        details: 'Retrieved 150 records'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 30000).toISOString(),
        tool: 'db_query',
        operation: 'SELECT * FROM users WHERE active = 1',
        status: 'success',
        duration: 12,
        details: 'Returned 42 rows'
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 60000).toISOString(),
        tool: 'file_ops',
        operation: 'write /workspace/output.json',
        status: 'success',
        duration: 8,
        details: 'File written successfully (2.3KB)'
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 120000).toISOString(),
        tool: 'http_fetch',
        operation: 'POST https://api.service.com/webhook',
        status: 'error',
        duration: 5000,
        details: 'Connection timeout after 3 retries'
      }
    ]
    
    setToolLogs(mockLogs)
    
    // Check API status
    checkApiStatus()
  }, [])

  const checkApiStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/health')
      if (response.ok) {
        setApiStatus('connected')
      } else {
        setApiStatus('disconnected')
      }
    } catch (error) {
      setApiStatus('disconnected')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-800'
      case 'error': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getToolIcon = (tool: string) => {
    switch (tool) {
      case 'http_fetch': return <Globe className="w-4 h-4" />
      case 'db_query': return <Database className="w-4 h-4" />
      case 'file_ops': return <FileText className="w-4 h-4" />
      default: return <Zap className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                AI Agent Console
              </h1>
              <p className="text-lg text-gray-600">
                Training Class - Week 1 Foundation
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Badge 
                variant={apiStatus === 'connected' ? 'default' : 'destructive'}
                className="px-3 py-1"
              >
                <Activity className="w-3 h-3 mr-1" />
                API {apiStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </Badge>
              <Button onClick={checkApiStatus} variant="outline">
                <Settings className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
              <Globe className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,247</div>
              <p className="text-xs text-muted-foreground">+12% from last hour</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">94.2%</div>
              <p className="text-xs text-muted-foreground">+2.1% from yesterday</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">127ms</div>
              <p className="text-xs text-muted-foreground">-15ms from last hour</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Tools</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">HTTP, DB, Files</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="logs" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="logs">Tool Logs</TabsTrigger>
            <TabsTrigger value="tools">Available Tools</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
          </TabsList>

          <TabsContent value="logs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Tool Executions</CardTitle>
                <CardDescription>
                  Real-time log of tool executions and their results
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {toolLogs.map((log) => (
                    <div
                      key={log.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2">
                          {getToolIcon(log.tool)}
                          <span className="font-medium">{log.tool}</span>
                        </div>
                        <Badge className={getStatusColor(log.status)}>
                          {log.status}
                        </Badge>
                      </div>
                      
                      <div className="flex-1 mx-4">
                        <div className="text-sm text-gray-900">{log.operation}</div>
                        {log.details && (
                          <div className="text-xs text-gray-500">{log.details}</div>
                        )}
                      </div>
                      
                      <div className="text-right text-sm text-gray-500">
                        <div>{new Date(log.timestamp).toLocaleTimeString()}</div>
                        {log.duration && (
                          <div className="text-xs">{log.duration}ms</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="tools" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Globe className="w-5 h-5" />
                    <span>HTTP Fetch</span>
                  </CardTitle>
                  <CardDescription>
                    HTTP requests with retry, rate limiting, and timeout
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm space-y-1">
                    <li>• Automatic retries with exponential backoff</li>
                    <li>• Rate limiting (10 req/sec default)</li>
                    <li>• Timeout protection (30s default)</li>
                    <li>• User-Agent identification</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Database className="w-5 h-5" />
                    <span>Database Query</span>
                  </CardTitle>
                  <CardDescription>
                    Safe database queries with validation
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm space-y-1">
                    <li>• Read-only SQL whitelist</li>
                    <li>• Parameter schema validation</li>
                    <li>• Query sanitization</li>
                    <li>• Connection pooling</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="w-5 h-5" />
                    <span>File Operations</span>
                  </CardTitle>
                  <CardDescription>
                    Sandboxed file system operations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm space-y-1">
                    <li>• Workspace sandbox protection</li>
                    <li>• Path traversal prevention</li>
                    <li>• File size limits</li>
                    <li>• Extension filtering</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="config" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>System Configuration</CardTitle>
                <CardDescription>
                  Current system settings and environment
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3">API Settings</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Endpoint:</span>
                        <span className="font-mono">http://localhost:8000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Version:</span>
                        <span>1.0.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Environment:</span>
                        <span>Development</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-3">Observability</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Tracing:</span>
                        <span className="text-green-600">Enabled</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Metrics:</span>
                        <span className="text-green-600">Enabled</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Console Export:</span>
                        <span className="text-green-600">Enabled</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Week 4 Preview</CardTitle>
                <CardDescription>
                  Features coming in the enhanced agent console
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg bg-blue-50">
                    <h5 className="font-semibold text-blue-900 mb-2">Interactive Agent Chat</h5>
                    <p className="text-sm text-blue-700">
                      Real-time conversation interface with AI agents
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg bg-green-50">
                    <h5 className="font-semibold text-green-900 mb-2">Tool Execution Playground</h5>
                    <p className="text-sm text-green-700">
                      Interactive tool testing and execution environment
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg bg-purple-50">
                    <h5 className="font-semibold text-purple-900 mb-2">Advanced Monitoring</h5>
                    <p className="text-sm text-purple-700">
                      Detailed metrics, traces, and performance analytics
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg bg-orange-50">
                    <h5 className="font-semibold text-orange-900 mb-2">Agent Workflows</h5>
                    <p className="text-sm text-orange-700">
                      Visual workflow builder and execution tracking
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}