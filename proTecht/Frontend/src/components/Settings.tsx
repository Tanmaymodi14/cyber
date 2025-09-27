import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Switch } from './ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Separator } from './ui/separator';
import { 
  Shield, 
  User,
  Key,
  Bell,
  Cloud,
  Settings as SettingsIcon,
  ArrowLeft,
  Menu,
  X,
  Save,
  Trash2,
  Eye,
  EyeOff,
  Database,
  BarChart3,
  FileText,
  LogOut,
  ChevronRight
} from 'lucide-react';
import { useState } from 'react';

interface SettingsProps {
  onNavigate: (page: string) => void;
  selectedFramework?: {id: string, title: string} | null;
}

export function Settings({ onNavigate, selectedFramework }: SettingsProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    compliance: true,
    evidence: false,
    reports: true
  });

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, current: false },
    { id: 'evidence', label: 'Evidence', icon: Database, current: false },
    { id: 'controls', label: 'Controls', icon: Shield, current: false },
    { id: 'ssp', label: 'SSP Generator', icon: FileText, current: false },
    { id: 'reports', label: 'Reports', icon: BarChart3, current: false },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, current: true }
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
                <h1 className="text-2xl font-bold">Settings</h1>
                <p className="text-sm text-muted-foreground">Manage your account and preferences</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </header>

        {/* Settings content */}
        <main className="flex-1 p-6 space-y-8 bg-background/50">
          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="integrations">Integrations</TabsTrigger>
              <TabsTrigger value="notifications">Notifications</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
            </TabsList>

            {/* Profile Settings */}
            <TabsContent value="profile" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Profile Information</CardTitle>
                  <CardDescription>
                    Update your personal information and organization details
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="firstName">First Name</Label>
                      <Input id="firstName" defaultValue="John" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="lastName">Last Name</Label>
                      <Input id="lastName" defaultValue="Doe" />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input id="email" type="email" defaultValue="john.doe@company.com" />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="company">Organization</Label>
                    <Input id="company" defaultValue="Example Corp" />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Input id="role" defaultValue="Compliance Manager" />
                  </div>

                  <Separator />

                  <div className="flex justify-end space-x-3">
                    <Button variant="outline">Cancel</Button>
                    <Button>
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Integrations */}
            <TabsContent value="integrations" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Cloud Integrations</CardTitle>
                  <CardDescription>
                    Manage connections to your cloud infrastructure
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* AWS Integration */}
                  <div className="flex items-center justify-between p-4 border rounded-lg bg-secondary/20">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center">
                        <Cloud className="h-6 w-6 text-orange-500" />
                      </div>
                      <div>
                        <h3 className="font-semibold">Amazon Web Services</h3>
                        <p className="text-sm text-muted-foreground">Connected via IAM Role</p>
                      </div>
                    </div>
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      Connected
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="awsRole">AWS IAM Role ARN</Label>
                    <div className="flex space-x-3">
                      <Input 
                        id="awsRole" 
                        defaultValue="arn:aws:iam::123456789012:role/proTecht-ReadOnly"
                        className="flex-1"
                      />
                      <Button variant="outline">Test Connection</Button>
                    </div>
                  </div>

                  <Separator />

                  {/* Future Integrations */}
                  <div className="space-y-4">
                    <h4 className="font-medium">Available Integrations</h4>
                    
                    <div className="flex items-center justify-between p-4 border rounded-lg opacity-50">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
                          <Cloud className="h-6 w-6 text-blue-500" />
                        </div>
                        <div>
                          <h3 className="font-semibold">Microsoft Azure</h3>
                          <p className="text-sm text-muted-foreground">Coming soon</p>
                        </div>
                      </div>
                      <Badge variant="outline">Soon</Badge>
                    </div>

                    <div className="flex items-center justify-between p-4 border rounded-lg opacity-50">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
                          <Cloud className="h-6 w-6 text-green-500" />
                        </div>
                        <div>
                          <h3 className="font-semibold">Google Cloud Platform</h3>
                          <p className="text-sm text-muted-foreground">Coming soon</p>
                        </div>
                      </div>
                      <Badge variant="outline">Soon</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Notifications */}
            <TabsContent value="notifications" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Notification Preferences</CardTitle>
                  <CardDescription>
                    Configure how and when you receive notifications
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-6">
                    <div className="flex items-center justify-between py-2">
                      <div className="space-y-0.5">
                        <Label>Email Notifications</Label>
                        <p className="text-sm text-muted-foreground">
                          Receive notifications via email
                        </p>
                      </div>
                      <Switch 
                        checked={notifications.email}
                        onCheckedChange={(checked) => 
                          setNotifications(prev => ({ ...prev, email: checked }))
                        }
                      />
                    </div>

                    <Separator />

                    <div className="flex items-center justify-between py-2">
                      <div className="space-y-0.5">
                        <Label>Compliance Alerts</Label>
                        <p className="text-sm text-muted-foreground">
                          Alerts for compliance status changes
                        </p>
                      </div>
                      <Switch 
                        checked={notifications.compliance}
                        onCheckedChange={(checked) => 
                          setNotifications(prev => ({ ...prev, compliance: checked }))
                        }
                      />
                    </div>

                    <Separator />

                    <div className="flex items-center justify-between py-2">
                      <div className="space-y-0.5">
                        <Label>Evidence Reminders</Label>
                        <p className="text-sm text-muted-foreground">
                          Reminders for missing evidence
                        </p>
                      </div>
                      <Switch 
                        checked={notifications.evidence}
                        onCheckedChange={(checked) => 
                          setNotifications(prev => ({ ...prev, evidence: checked }))
                        }
                      />
                    </div>

                    <Separator />

                    <div className="flex items-center justify-between py-2">
                      <div className="space-y-0.5">
                        <Label>Report Generation</Label>
                        <p className="text-sm text-muted-foreground">
                          Notifications when reports are ready
                        </p>
                      </div>
                      <Switch 
                        checked={notifications.reports}
                        onCheckedChange={(checked) => 
                          setNotifications(prev => ({ ...prev, reports: checked }))
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="notificationEmail">Notification Email</Label>
                    <Input 
                      id="notificationEmail" 
                      type="email" 
                      defaultValue="john.doe@company.com"
                    />
                  </div>

                  <div className="flex justify-end">
                    <Button>
                      <Save className="h-4 w-4 mr-2" />
                      Save Preferences
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Security */}
            <TabsContent value="security" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>API Keys & Security</CardTitle>
                  <CardDescription>
                    Manage API keys and security settings
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="openaiKey">OpenAI API Key</Label>
                      <div className="flex space-x-3">
                        <div className="relative flex-1">
                          <Input
                            id="openaiKey"
                            type={showApiKey ? "text" : "password"}
                            defaultValue="sk-proj-..."
                            placeholder="Enter your OpenAI API key"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3"
                            onClick={() => setShowApiKey(!showApiKey)}
                          >
                            {showApiKey ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                        <Button variant="outline">Test</Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Used for AI-powered compliance analysis and recommendations
                      </p>
                    </div>

                    <Separator />

                    <div className="space-y-4">
                      <Label>Session Security</Label>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <span className="text-sm font-medium">Two-factor authentication</span>
                          <Badge variant="outline">Recommended</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <span className="text-sm font-medium">Session timeout</span>
                          <Badge variant="secondary">30 minutes</Badge>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div className="space-y-4">
                      <Label>Data Export</Label>
                      <p className="text-sm text-muted-foreground">
                        Download all your compliance data and configurations
                      </p>
                      <Button variant="outline">
                        <Key className="h-4 w-4 mr-2" />
                        Export Data
                      </Button>
                    </div>

                    <Separator />

                    <div className="space-y-4">
                      <Label className="text-red-600">Danger Zone</Label>
                      <p className="text-sm text-muted-foreground">
                        Permanently delete your account and all associated data
                      </p>
                      <Button variant="destructive" className="bg-red-600 hover:bg-red-700">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete Account
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}