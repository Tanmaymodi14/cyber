import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ControlBadge } from './ControlBadge';
import { 
  Shield, 
  FileText,
  Download,
  TrendingUp,
  Calendar,
  BarChart3,
  PieChart,
  ArrowLeft,
  Menu,
  X,
  AlertTriangle,
  Database,
  Settings,
  User,
  LogOut,
  ChevronRight,
  Bell
} from 'lucide-react';
import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart as RechartsPieChart, Cell, Pie } from 'recharts';

interface ReportsProps {
  onNavigate: (page: string) => void;
  selectedFramework?: {id: string, title: string} | null;
}

export function Reports({ onNavigate, selectedFramework }: ReportsProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [timeRange, setTimeRange] = useState('30d');

  const complianceTrendData = [
    { date: '2024-01-01', compliance: 78, acCompliance: 75 },
    { date: '2024-01-05', compliance: 80, acCompliance: 78 },
    { date: '2024-01-10', compliance: 81, acCompliance: 80 },
    { date: '2024-01-15', compliance: 83, acCompliance: 82 },
    { date: '2024-01-20', compliance: 84, acCompliance: 83 },
    { date: '2024-01-25', compliance: 85, acCompliance: 84 },
    { date: '2024-01-30', compliance: 84, acCompliance: 84 }
  ];

  const acControlsData = [
    { priority: 'Pass', count: 17, color: '#10b981' },
    { priority: 'Partial', count: 4, color: '#f59e0b' },
    { priority: 'Fail', count: 1, color: '#ef4444' }
  ];

  // AC-specific breakdown
  const acControlBreakdown = [
    { control: 'AC-7', name: 'Unsuccessful Logon Attempts', score: 94, status: 'pass' },
    { control: 'AC-1', name: 'Access Control Policy', score: 95, status: 'pass' },
    { control: 'AC-14', name: 'Permitted Actions', score: 93, status: 'pass' },
    { control: 'AC-3', name: 'Access Enforcement', score: 92, status: 'pass' },
    { control: 'AC-22', name: 'Publicly Accessible Content', score: 92, status: 'pass' },
    { control: 'AC-12', name: 'Session Termination', score: 91, status: 'pass' },
    { control: 'AC-10', name: 'Concurrent Session Control', score: 90, status: 'pass' },
    { control: 'AC-11', name: 'Session Lock', score: 89, status: 'pass' },
    { control: 'AC-4', name: 'Information Flow Enforcement', score: 88, status: 'pass' },
    { control: 'AC-9', name: 'Previous Logon Notification', score: 87, status: 'pass' },
    { control: 'AC-21', name: 'Information Sharing', score: 88, status: 'pass' },
    { control: 'AC-20', name: 'Use of External Systems', score: 86, status: 'pass' },
    { control: 'AC-5', name: 'Separation of Duties', score: 85, status: 'pass' },
    { control: 'AC-16', name: 'Security Attributes', score: 84, status: 'pass' },
    { control: 'AC-2', name: 'Account Management', score: 78, status: 'partial' },
    { control: 'AC-8', name: 'System Use Notification', score: 76, status: 'partial' },
    { control: 'AC-13', name: 'Supervision and Review', score: 74, status: 'partial' },
    { control: 'AC-6', name: 'Least Privilege', score: 72, status: 'partial' },
    { control: 'AC-17', name: 'Remote Access', score: 71, status: 'partial' },
    { control: 'AC-18', name: 'Wireless Access', score: 69, status: 'partial' },
    { control: 'AC-19', name: 'Mobile Device Access', score: 68, status: 'partial' },
    { control: 'AC-15', name: 'Automated Marking', score: 67, status: 'partial' }
  ];

  const keyMetrics = [
    {
      title: 'AC Family Compliance',
      value: '84%',
      change: '+3%',
      trend: 'up',
      icon: BarChart3
    },
    {
      title: 'AC Controls Needing Attention',
      value: '4',
      change: '-1',
      trend: 'down',
      icon: AlertTriangle
    },
    {
      title: 'AC Controls Assessed',
      value: '22',
      change: '+22',
      trend: 'up',
      icon: Shield
    },
    {
      title: 'Evidence Sources Mapped',
      value: '8',
      change: '+3',
      trend: 'up',
      icon: FileText
    }
  ];

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, current: false },
    { id: 'evidence', label: 'Evidence', icon: Database, current: false },
    { id: 'controls', label: 'Controls', icon: Shield, current: false },
    { id: 'ssp', label: 'SSP Generator', icon: FileText, current: false },
    { id: 'reports', label: 'Reports', icon: BarChart3, current: true },
    { id: 'settings', label: 'Settings', icon: Settings, current: false }
  ];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 bg-card border-r border-border transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="h-6 w-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">proTecht</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <Button
                  key={item.id}
                  variant={item.current ? "secondary" : "ghost"}
                  className={`w-full justify-start h-12 px-4 ${
                    item.current ? 'bg-primary/10 text-primary hover:bg-primary/20' : 'hover:bg-secondary/80'
                  }`}
                  onClick={() => {
                    onNavigate(item.id);
                    setSidebarOpen(false);
                  }}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                  {item.current && <ChevronRight className="ml-auto h-4 w-4" />}
                </Button>
              );
            })}
          </div>
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-border">
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                  <User className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">John Doe</p>
                  <p className="text-sm text-muted-foreground truncate">Security Admin</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => onNavigate('landing')}
                  className="h-8 w-8 p-0"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="bg-card border-b border-border sticky top-0 z-30">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onNavigate('dashboard')}
                className="hidden lg:flex"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Compliance Reports</h1>
                <p className="text-sm text-muted-foreground">Comprehensive compliance analytics and insights</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5" />
              </Button>
              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                  <SelectItem value="1y">Last year</SelectItem>
                </SelectContent>
              </Select>
              <Button>
                <Download className="h-4 w-4 mr-2" />
                Export Report
              </Button>
            </div>
          </div>
        </header>

        {/* Reports content */}
        <main className="flex-1 p-6 space-y-8 bg-background/50">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            {keyMetrics.map((metric, index) => {
              const Icon = metric.icon;
              return (
                <Card key={index} className="bg-gradient-to-br from-card to-card/50">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                    <CardTitle className="font-medium">{metric.title}</CardTitle>
                    <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold mb-2">{metric.value}</div>
                    <div className="flex items-center space-x-1">
                      <TrendingUp className={`h-4 w-4 ${
                        metric.trend === 'up' ? 'text-green-500' : 'text-red-500'
                      }`} />
                      <span className={`text-sm font-medium ${
                        metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metric.change}
                      </span>
                      <span className="text-sm text-muted-foreground">vs last period</span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Charts */}
          <Tabs defaultValue="trends" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="trends">Compliance Trends</TabsTrigger>
              <TabsTrigger value="breakdown">Family Breakdown</TabsTrigger>
              <TabsTrigger value="remediation">Remediation Priority</TabsTrigger>
            </TabsList>

            {/* Compliance Trends */}
            <TabsContent value="trends" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Compliance Trend Over Time</CardTitle>
                  <CardDescription>
                    Track your compliance percentage changes over the selected time period
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={complianceTrendData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                        <XAxis 
                          dataKey="date" 
                          tickFormatter={(value) => new Date(value).toLocaleDateString()}
                          stroke="hsl(var(--muted-foreground))"
                        />
                        <YAxis 
                          domain={[75, 90]} 
                          stroke="hsl(var(--muted-foreground))"
                        />
                        <Tooltip 
                          labelFormatter={(value) => new Date(value).toLocaleDateString()}
                          formatter={(value) => [`${value}%`, 'Compliance']}
                          contentStyle={{
                            backgroundColor: 'hsl(var(--card))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                          }}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="compliance" 
                          stroke="#14b8a6" 
                          strokeWidth={3}
                          dot={{ fill: '#14b8a6', strokeWidth: 2, r: 6 }}
                          activeDot={{ r: 8, stroke: '#14b8a6', strokeWidth: 2 }}
                          name="Overall Compliance"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="acCompliance" 
                          stroke="#0891b2" 
                          strokeWidth={3}
                          dot={{ fill: '#0891b2', strokeWidth: 2, r: 6 }}
                          activeDot={{ r: 8, stroke: '#0891b2', strokeWidth: 2 }}
                          name="AC Compliance"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Family Breakdown */}
            <TabsContent value="breakdown" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Control Family Status Breakdown</CardTitle>
                  <CardDescription>
                    Detailed status breakdown by control family
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={[{ family: 'Access Control', pass: 17, partial: 4, fail: 1 }]} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                        <XAxis 
                          dataKey="family" 
                          angle={-45}
                          textAnchor="end"
                          height={100}
                          fontSize={12}
                          stroke="hsl(var(--muted-foreground))"
                        />
                        <YAxis stroke="hsl(var(--muted-foreground))" />
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: 'hsl(var(--card))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                          }}
                        />
                        <Bar dataKey="pass" stackId="a" fill="#10b981" name="Pass" radius={[0, 0, 0, 0]} />
                        <Bar dataKey="partial" stackId="a" fill="#f59e0b" name="Partial" radius={[0, 0, 0, 0]} />
                        <Bar dataKey="fail" stackId="a" fill="#ef4444" name="Fail" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Remediation Priority */}
            <TabsContent value="remediation" className="space-y-6">
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <Card>
                  <CardHeader>
                    <CardTitle>AC Control Status Distribution</CardTitle>
                    <CardDescription>
                      Breakdown of Access Control controls by compliance status
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <RechartsPieChart>
                          <Pie
                            data={acControlsData}
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            innerRadius={40}
                            dataKey="count"
                            label={({ priority, count }) => `${priority}: ${count}`}
                            labelLine={false}
                          >
                            {acControlsData.map((entry, index) => (
                              <Cell key={index} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip 
                            formatter={(value, name) => [value, 'Controls']}
                            contentStyle={{
                              backgroundColor: 'hsl(var(--card))',
                              border: '1px solid hsl(var(--border))',
                              borderRadius: '8px'
                            }}
                          />
                        </RechartsPieChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Control Status Summary</CardTitle>
                    <CardDescription>
                      AC control compliance status breakdown
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {acControlsData.map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-secondary/20 transition-colors">
                          <div className="flex items-center space-x-3">
                            <div 
                              className="w-4 h-4 rounded-full"
                              style={{ backgroundColor: item.color }}
                            />
                            <span className="font-medium">{item.priority} Controls</span>
                          </div>
                          <Badge variant="outline" className="font-medium">
                            {item.count} controls
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>

          {/* Export Options */}
          <Card>
            <CardHeader>
              <CardTitle>Export Reports</CardTitle>
              <CardDescription>
                Download comprehensive compliance reports in various formats
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Button variant="outline" className="h-24 flex flex-col justify-center space-y-2 hover:bg-secondary/80">
                  <FileText className="h-8 w-8 text-primary" />
                  <span className="font-medium">Executive Summary (PDF)</span>
                </Button>
                <Button variant="outline" className="h-24 flex flex-col justify-center space-y-2 hover:bg-secondary/80">
                  <BarChart3 className="h-8 w-8 text-primary" />
                  <span className="font-medium">Detailed Analytics (CSV)</span>
                </Button>
                <Button variant="outline" className="h-24 flex flex-col justify-center space-y-2 hover:bg-secondary/80">
                  <PieChart className="h-8 w-8 text-primary" />
                  <span className="font-medium">Raw Data (JSON)</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}