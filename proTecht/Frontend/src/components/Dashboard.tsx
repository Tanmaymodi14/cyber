import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { ControlBadge } from './ControlBadge';
import { 
  Shield, 
  BarChart3, 
  FileText, 
  Upload, 
  Settings, 
  Database,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Bell,
  User,
  LogOut,
  Menu,
  X,
  ChevronRight,
  TrendingUp,
  Activity,
  Zap
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getACControls } from '../services/api';
import { toast } from 'sonner';

interface DashboardProps {
  onNavigate: (page: string) => void;
  selectedFramework?: {id: string, title: string} | null;
}

export function Dashboard({ onNavigate, selectedFramework }: DashboardProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [controls, setControls] = useState<any[]>([]);
  
  // Derived state from controls
  const [complianceData, setComplianceData] = useState({
    overall: 0,
    pass: 0,
    partial: 0,
    fail: 0
  });
  
  const [chartData, setChartData] = useState([
    { name: 'Compliant', value: 0, color: '#10b981' },
    { name: 'Partial', value: 0, color: '#f59e0b' },
    { name: 'Non-Compliant', value: 0, color: '#ef4444' }
  ]);
  
  // Focus on Access Control family only for this demo
  const [controlFamilies, setControlFamilies] = useState([
    { name: 'Access Control (AC)', total: 22, compliant: 0, partial: 0, fail: 0, code: 'AC', avgScore: 0 }
  ]);
  
  const recentActivity = [
    { action: 'AC-13 evidence updated from GuardDuty', time: '1 hour ago', type: 'success' },
    { action: 'AC-17 policy analysis completed', time: '3 hours ago', type: 'warning' },
    { action: 'IAM Configuration re-collected', time: '6 hours ago', type: 'info' },
    { action: 'S3 bucket policies assessed', time: '1 day ago', type: 'warning' },
    { action: 'VPC flow logs validated', time: '1 day ago', type: 'success' }
  ];
  
  // Top AC controls by score and controls needing attention
  const [topControls, setTopControls] = useState<any[]>([]);
  const [needsAttention, setNeedsAttention] = useState<any[]>([]);
  
  // Control name mapping
  const controlNames: Record<string, string> = {
    'AC-1': 'Access Control Policy and Procedures',
    'AC-2': 'Account Management',
    'AC-3': 'Access Enforcement',
    'AC-4': 'Information Flow Enforcement',
    'AC-5': 'Separation of Duties',
    'AC-6': 'Least Privilege',
    'AC-7': 'Unsuccessful Logon Attempts',
    'AC-8': 'System Use Notification',
    'AC-9': 'Previous Logon Notification',
    'AC-10': 'Concurrent Session Control',
    'AC-11': 'Session Lock',
    'AC-12': 'Session Termination',
    'AC-13': 'Supervision and Review',
    'AC-14': 'Permitted Actions Without Identification',
    'AC-15': 'Automated Marking',
    'AC-16': 'Security Attributes',
    'AC-17': 'Remote Access',
    'AC-18': 'Wireless Access',
    'AC-19': 'Access Control for Mobile Devices',
    'AC-20': 'Use of External Information Systems',
    'AC-21': 'Information Sharing',
    'AC-22': 'Publicly Accessible Content'
  };
  
  // Load controls data
  useEffect(() => {
    const loadControls = async () => {
      setIsLoading(true);
      try {
        toast.loading('Loading compliance data...', { id: 'load-dashboard' });
        const response = await getACControls();
        
        // Handle no data state
        if (response.status === 'no_data') {
          toast.error('No AWS data available. Please collect real AWS data first.', { id: 'load-dashboard' });
          setControls([]);
          setIsLoading(false);
          return;
        }
        
        const data = response.data || response;
        setControls(data);
        
        // Process controls data
        const pass = data.filter(c => c.status === 'pass').length;
        const partial = data.filter(c => c.status === 'partial').length;
        const fail = data.filter(c => c.status === 'fail').length;
        const unknown = data.filter(c => c.status === 'unknown').length;
        
        // Calculate overall score (weighted average)
        const totalControls = data.length;
        const totalScore = data.reduce((sum, c) => sum + c.score, 0);
        const overall = Math.round(totalScore / totalControls);
        
        // Update compliance data
        setComplianceData({
          overall,
          pass,
          partial,
          fail: fail + unknown
        });
        
        // Update chart data
        setChartData([
          { name: 'Compliant', value: pass, color: '#10b981' },
          { name: 'Partial', value: partial, color: '#f59e0b' },
          { name: 'Non-Compliant', value: fail + unknown, color: '#ef4444' }
        ]);
        
        // Update control families
        setControlFamilies([
          { 
            name: 'Access Control (AC)', 
            total: totalControls, 
            compliant: pass, 
            partial: partial, 
            fail: fail + unknown, 
            code: 'AC', 
            avgScore: overall 
          }
        ]);
        
        // Update top controls (sort by score descending)
        const enhancedControls = data.map(c => ({
          ...c,
          name: controlNames[c.id] || c.id
        }));
        
        const sortedByScore = [...enhancedControls].sort((a, b) => b.score - a.score);
        setTopControls(sortedByScore.slice(0, 5));
        
        // Update needs attention (sort by score ascending, only non-passing)
        const needsWork = enhancedControls
          .filter(c => c.status !== 'pass')
          .sort((a, b) => a.score - b.score)
          .slice(0, 4)
          .map(c => ({
            ...c,
            issue: c.missingEvidence?.[0] || c.reasons?.[0] || 'Needs technical validation'
          }));
        setNeedsAttention(needsWork);
        
        toast.success('Dashboard data loaded', { id: 'load-dashboard' });
      } catch (error) {
        console.error('Failed to load controls', error);
        toast.error('Failed to load compliance data', { id: 'load-dashboard' });
      } finally {
        setIsLoading(false);
      }
    };
    
    loadControls();
  }, []);

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, current: true },
    { id: 'evidence', label: 'Evidence', icon: Database },
    { id: 'controls', label: 'Controls', icon: Shield },
    { id: 'ssp', label: 'SSP Generator', icon: FileText },
    { id: 'reports', label: 'Reports', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex h-screen">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-72 bg-card border-r border-border transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 flex flex-col`}>
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
                    {item.current && (
                      <ChevronRight className="ml-auto h-4 w-4" />
                    )}
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
          <header className="bg-card border-b border-border">
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
                <div>
                  <h1>Compliance Dashboard</h1>
                  <p className="text-sm text-muted-foreground">Monitor your compliance status and progress</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Button variant="ghost" size="sm" className="relative">
                  <Bell className="h-5 w-5" />
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full" />
                </Button>
                <Badge variant="secondary" className="px-3 py-1 bg-primary/10 text-primary border-primary/20">
                  <div className="w-2 h-2 bg-primary rounded-full mr-2" />
                  {selectedFramework?.title || 'FedRAMP Moderate'}
                </Badge>
              </div>
            </div>
          </header>

          {/* Dashboard content */}
          <main className="flex-1 p-6 space-y-8 overflow-y-auto">
            {/* No Data Notification */}
            {controls.length === 0 && !isLoading && (
              <Alert className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20">
                <Database className="h-5 w-5 text-blue-600" />
                <AlertDescription className="text-blue-800 dark:text-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">No AWS data available</p>
                      <p className="text-sm">Collect real AWS data to see compliance status</p>
                    </div>
                    <Button 
                      onClick={() => {
                        // Trigger AWS data collection
                        fetch('/api/evidence/aws/recollect', { method: 'POST' })
                          .then(() => {
                            toast.success('AWS data collection started');
                            window.location.reload();
                          })
                          .catch(() => toast.error('Failed to start data collection'));
                      }}
                      className="ml-4"
                    >
                      Collect AWS Data
                    </Button>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            {/* Regular Notification */}
            {controls.length > 0 && (
              <Alert className="border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/20">
                <AlertTriangle className="h-5 w-5 text-amber-600" />
                <AlertDescription className="text-amber-800 dark:text-amber-200 flex items-center gap-2">
                  {needsAttention.length} AC controls need technical evidence validation.
                  <Button 
                    variant="link" 
                    className="p-0 h-auto text-amber-800 dark:text-amber-200 underline font-medium"
                    onClick={() => onNavigate('controls')}
                  >
                    Review AC controls
                  </Button>
                </AlertDescription>
              </Alert>
            )}

            {/* Key metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              <Card className="bg-gradient-to-br from-card to-card/50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Overall Compliance</CardTitle>
                  <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center">
                    <Shield className="h-4 w-4 text-primary" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-baseline space-x-2">
                      <span className="text-2xl font-bold text-primary">{isLoading ? '...' : `${complianceData.overall}%`}</span>
                      <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                        Good
                      </Badge>
                    </div>
                    <Progress value={complianceData.overall} className="h-2" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Compliant Controls</CardTitle>
                  <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                    <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <span className="text-2xl font-bold">{isLoading ? '...' : complianceData.pass}</span>
                    <p className="text-xs text-muted-foreground">
                      77% of AC controls
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Partial Compliance</CardTitle>
                  <div className="w-8 h-8 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <span className="text-2xl font-bold text-orange-600">{isLoading ? '...' : complianceData.partial}</span>
                    <p className="text-xs text-muted-foreground">
                      18% of AC controls
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Non-Compliant</CardTitle>
                  <div className="w-8 h-8 bg-red-100 dark:bg-red-900 rounded-lg flex items-center justify-center">
                    <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <span className="text-2xl font-bold text-red-600">{isLoading ? '...' : complianceData.fail}</span>
                    <p className="text-xs text-muted-foreground">
                      5% of AC controls
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Charts and detailed views */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Compliance Overview Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Compliance Overview</CardTitle>
                  <CardDescription>Overall compliance status distribution</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="value"
                          stroke="none"
                        >
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* AC Control Family Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Access Control (AC) Family</CardTitle>
                  <CardDescription>Detailed breakdown of AC control compliance</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {controlFamilies.map((family) => (
                    <div key={family.code} className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                            <Shield className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <span className="font-medium">{family.name}</span>
                            <p className="text-sm text-muted-foreground">Average Score: {family.avgScore}%</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-muted-foreground">
                            {family.compliant} Pass • {family.partial} Partial • {family.fail} Fail
                          </div>
                          <div className="text-xs text-muted-foreground">{family.total} total controls</div>
                        </div>
                      </div>
                      <Progress 
                        value={(family.compliant / family.total) * 100} 
                        className="h-3"
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Top Performing and Needs Attention */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Top Performing Controls */}
              <Card>
                <CardHeader>
                  <CardTitle>Top Performing AC Controls</CardTitle>
                  <CardDescription>Highest scoring Access Control implementations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {topControls.map((control, index) => (
                      <div key={control.id} className="flex items-center space-x-3 p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                        <div className="w-6 h-6 bg-green-100 dark:bg-green-900 rounded flex items-center justify-center text-xs font-medium text-green-700 dark:text-green-300">
                          #{index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <ControlBadge controlId={control.id} size="sm" />
                            <span className="font-medium text-sm">{control.name}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-green-600 dark:text-green-400">{control.score}%</div>
                          <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 text-xs">
                            {control.status.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Controls Needing Attention */}
              <Card>
                <CardHeader>
                  <CardTitle>Controls Needing Attention</CardTitle>
                  <CardDescription>AC controls requiring immediate action</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {needsAttention.map((control) => (
                      <div key={control.id} className="flex items-start space-x-3 p-3 bg-amber-50 dark:bg-amber-950/20 rounded-lg">
                        <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <ControlBadge controlId={control.id} size="sm" />
                            <span className="font-medium text-sm">{control.name}</span>
                          </div>
                          <p className="text-xs text-muted-foreground">{control.issue}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-amber-600">{control.score}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent AC Control Activity</CardTitle>
                <CardDescription>Latest Access Control compliance activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-center space-x-4">
                      <div className={`w-2 h-2 rounded-full ${
                        activity.type === 'success' ? 'bg-green-500' :
                        activity.type === 'warning' ? 'bg-orange-500' :
                        'bg-blue-500'
                      }`} />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.action}</p>
                        <p className="text-xs text-muted-foreground">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button 
                className="h-24 flex flex-col space-y-2"
                onClick={() => onNavigate('upload')}
              >
                <Upload className="h-6 w-6" />
                <span>Upload Evidence</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-24 flex flex-col space-y-2"
                onClick={() => onNavigate('ssp')}
              >
                <FileText className="h-6 w-6" />
                <span>Generate SSP</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-24 flex flex-col space-y-2"
                onClick={() => onNavigate('reports')}
              >
                <BarChart3 className="h-6 w-6" />
                <span>View Reports</span>
              </Button>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}