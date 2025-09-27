import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ControlBadge } from './ControlBadge';
import { 
  Shield, 
  FileText,
  Download,
  CheckCircle,
  Clock,
  ArrowLeft,
  Menu,
  X,
  Save,
  RefreshCw,
  Database,
  BarChart3,
  Settings,
  User,
  LogOut,
  ChevronRight,
  Bell
} from 'lucide-react';
import { useState } from 'react';

interface SSPGeneratorProps {
  onNavigate: (page: string) => void;
  selectedFramework?: {id: string, title: string} | null;
}

export function SSPGenerator({ onNavigate, selectedFramework }: SSPGeneratorProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedControl, setSelectedControl] = useState<string | null>('AC-1');
  const [generationProgress, setGenerationProgress] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [controlResponses, setControlResponses] = useState<Record<string, string>>({});

  const controls = [
    {
      id: 'AC-1',
      title: 'Access Control Policy and Procedures',
      status: 'complete',
      response: 'The organization has established and maintains a comprehensive access control policy that addresses purpose, scope, roles, responsibilities, management commitment, coordination among organizational entities, and compliance. The policy is reviewed annually and updated when significant changes occur. Associated procedures facilitate implementation of the access control policy and related controls.',
      aiGenerated: true,
      evidenceSources: ['Policy'],
      score: 95
    },
    {
      id: 'AC-2',
      title: 'Account Management',
      status: 'complete',
      response: 'The organization manages information system accounts by identifying account types, establishing conditions for group membership, authorizing access to the system, and monitoring account usage. AWS IAM is used to implement automated account management including user provisioning, role assignment, and access reviews. Account lifecycle management procedures ensure timely provisioning and deprovisioning.',
      aiGenerated: true,
      evidenceSources: ['IAM', 'Policy'],
      score: 78
    },
    {
      id: 'AC-3',
      title: 'Access Enforcement',
      status: 'complete',
      response: 'The information system enforces approved authorizations for logical access to information and system resources in accordance with applicable access control policies. Role-based access control (RBAC) is implemented through AWS IAM roles and policies. Permission boundaries ensure users cannot exceed their authorized access levels.',
      aiGenerated: true,
      evidenceSources: ['IAM', 'SSO'],
      score: 92
    },
    {
      id: 'AC-4',
      title: 'Information Flow Enforcement',
      status: 'complete',
      response: 'The information system controls information flows within the system and between interconnected systems in accordance with security policies. AWS WAF and VPC security groups enforce traffic filtering and network segmentation. Network ACLs provide additional layer of flow control.',
      aiGenerated: true,
      evidenceSources: ['WAF', 'VPC'],
      score: 88
    },
    {
      id: 'AC-5',
      title: 'Separation of Duties',
      status: 'complete',
      response: 'The organization separates duties of individuals to reduce the risk of malevolent activity without collusion. Administrative functions are segregated through distinct IAM roles. Dual control mechanisms are implemented for sensitive operations including privilege escalation and critical system changes.',
      aiGenerated: true,
      evidenceSources: ['IAM'],
      score: 85
    },
    {
      id: 'AC-6',
      title: 'Least Privilege',
      status: 'draft',
      response: 'The organization employs the principle of least privilege, allowing only authorized accesses for users which are necessary to accomplish assigned tasks. IAM policies are designed with minimal required permissions. Regular access reviews ensure permissions remain appropriate.',
      aiGenerated: true,
      evidenceSources: ['IAM'],
      score: 72
    },
    {
      id: 'AC-7',
      title: 'Unsuccessful Logon Attempts',
      status: 'complete',
      response: 'The information system enforces account lockout after 5 consecutive unsuccessful logon attempts within a 15-minute period. Account lockout duration is set to 30 minutes or until unlocked by an administrator. Failed authentication events are logged and monitored.',
      aiGenerated: true,
      evidenceSources: ['IAM', 'Config'],
      score: 94
    },
    {
      id: 'AC-8',
      title: 'System Use Notification',
      status: 'draft',
      response: 'The information system displays system use notification messages before granting access. Login banners inform users of usage monitoring and legal requirements. User acknowledgment of terms is tracked and logged.',
      aiGenerated: true,
      evidenceSources: ['Policy'],
      score: 76
    },
    {
      id: 'AC-11',
      title: 'Session Lock',
      status: 'complete',
      response: 'The information system prevents further access by initiating a session lock after 8 hours of inactivity. Session locks remain in effect until the user reestablishes access using appropriate identification and authentication procedures.',
      aiGenerated: true,
      evidenceSources: ['SSO', 'VPC'],
      score: 89
    },
    {
      id: 'AC-12',
      title: 'Session Termination',
      status: 'complete',
      response: 'The information system automatically terminates user sessions after 8 hours or upon user logout. Session state is cleared and system resources are released. Users receive notification before automatic termination.',
      aiGenerated: true,
      evidenceSources: ['SSO', 'VPC'],
      score: 91
    },
    {
      id: 'AC-17',
      title: 'Remote Access',
      status: 'pending',
      response: 'Remote access implementation details are being finalized. VPN requirements and multi-factor authentication policies are established but technical validation is pending.',
      aiGenerated: false,
      evidenceSources: ['Policy'],
      score: 71
    },
    {
      id: 'AC-19',
      title: 'Access Control for Mobile Devices',
      status: 'pending',
      response: 'Mobile device management policies are documented but technical implementation evidence is required. MDM solution deployment is in progress.',
      aiGenerated: false,
      evidenceSources: ['Policy'],
      score: 68
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'complete':
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Complete</Badge>;
      case 'draft':
        return <Badge className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">Draft</Badge>;
      case 'pending':
        return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">Pending</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'draft':
      case 'pending':
        return <Clock className="h-4 w-4 text-amber-500" />;
      default:
        return null;
    }
  };

  const selectedControlData = controls.find(c => c.id === selectedControl);
  
  const handleResponseChange = (controlId: string, value: string) => {
    setControlResponses(prev => ({
      ...prev,
      [controlId]: value
    }));
  };
  
  const getCurrentResponse = (controlId: string) => {
    return controlResponses[controlId] || selectedControlData?.response || '';
  };

  const handleGenerateSSP = () => {
    setIsGenerating(true);
    setGenerationProgress(0);
    
    const interval = setInterval(() => {
      setGenerationProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsGenerating(false);
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, current: false },
    { id: 'evidence', label: 'Evidence', icon: Database, current: false },
    { id: 'controls', label: 'Controls', icon: Shield, current: false },
    { id: 'ssp', label: 'SSP Generator', icon: FileText, current: true },
    { id: 'reports', label: 'Reports', icon: BarChart3, current: false },
    { id: 'settings', label: 'Settings', icon: Settings, current: false }
  ];

  const completedControls = controls.filter(c => c.status === 'complete').length;
  const totalControls = controls.length;
  const completionPercentage = Math.round((completedControls / totalControls) * 100);

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
                <h1 className="text-2xl font-bold">SSP Generator</h1>
                <p className="text-sm text-muted-foreground">Generate System Security Plan documentation</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5" />
              </Button>
              <Badge variant="outline" className="px-3 py-1">
                {completedControls}/{totalControls} Complete
              </Badge>
              <Button onClick={handleGenerateSSP} disabled={isGenerating}>
                {isGenerating ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    Export SSP
                  </>
                )}
              </Button>
            </div>
          </div>
        </header>

        {/* SSP content */}
        <main className="flex-1 p-6 space-y-8 bg-background/50">
          {/* Progress Overview */}
          <Card>
            <CardHeader>
              <CardTitle>System Security Plan Progress</CardTitle>
              <CardDescription>
                Track completion status of all security controls
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Overall Completion</span>
                  <span className="text-muted-foreground">{completionPercentage}%</span>
                </div>
                <Progress value={completionPercentage} className="h-3" />
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                    <div className="text-3xl font-bold text-green-600">{completedControls}</div>
                    <div className="text-sm text-muted-foreground">Complete</div>
                  </div>
                  <div className="text-center p-4 bg-amber-500/10 rounded-lg border border-amber-500/20">
                    <div className="text-3xl font-bold text-amber-600">
                      {controls.filter(c => c.status === 'draft').length}
                    </div>
                    <div className="text-sm text-muted-foreground">Draft</div>
                  </div>
                  <div className="text-center p-4 bg-gray-500/10 rounded-lg border border-gray-500/20">
                    <div className="text-3xl font-bold text-gray-600">
                      {controls.filter(c => c.status === 'pending').length}
                    </div>
                    <div className="text-sm text-muted-foreground">Pending</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Generation Progress */}
          {isGenerating && (
            <Card className="border-primary/20 bg-primary/5">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="h-4 w-4 animate-spin text-primary" />
                    <span className="font-medium">Generating System Security Plan...</span>
                  </div>
                  <Progress value={generationProgress} className="h-2" />
                  <p className="text-sm text-muted-foreground">
                    Compiling control responses and evidence mappings
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Control Editor */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Control List */}
            <Card>
              <CardHeader>
                <CardTitle>Security Controls</CardTitle>
                <CardDescription>
                  Select a control to edit its response
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-1">
                  {controls.map((control) => (
                    <button
                      key={control.id}
                      onClick={() => setSelectedControl(control.id)}
                      className={`w-full text-left p-4 hover:bg-muted transition-colors border-l-4 ${
                        selectedControl === control.id 
                          ? 'border-primary bg-primary/5' 
                          : 'border-transparent hover:border-primary/20'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{control.id}</span>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(control.status)}
                          {getStatusBadge(control.status)}
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {control.title}
                      </p>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Control Editor */}
            <div className="xl:col-span-2 space-y-6">
              {selectedControlData && (
                <Card>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="flex items-center space-x-2">
                          <span>{selectedControlData.id}</span>
                          {selectedControlData.aiGenerated && (
                            <Badge variant="outline" className="text-xs">AI Generated</Badge>
                          )}
                        </CardTitle>
                        <CardDescription className="mt-2">
                          {selectedControlData.title}
                        </CardDescription>
                      </div>
                      {getStatusBadge(selectedControlData.status)}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <label className="font-medium mb-3 block">
                        Control Implementation Response
                      </label>
                      <Textarea
                        value={getCurrentResponse(selectedControlData.id)}
                        onChange={(e) => handleResponseChange(selectedControlData.id, e.target.value)}
                        placeholder="Describe how this control is implemented in your organization..."
                        rows={10}
                        className="min-h-[250px]"
                      />
                    </div>

                    <div className="flex space-x-3">
                      <Button variant="outline" className="flex-1">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Regenerate with AI
                      </Button>
                      <Button className="flex-1">
                        <Save className="h-4 w-4 mr-2" />
                        Save Response
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Export Options */}
              <Card>
                <CardHeader>
                  <CardTitle>Export Options</CardTitle>
                  <CardDescription>
                    Generate and download your System Security Plan
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="docx" className="space-y-6">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="docx">DOCX Format</TabsTrigger>
                      <TabsTrigger value="oscal">OSCAL JSON</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="docx" className="space-y-4">
                      <div className="p-4 bg-secondary/20 rounded-lg">
                        <h4 className="font-medium mb-2">Microsoft Word Document</h4>
                        <p className="text-sm text-muted-foreground">
                          Generate a formatted SSP document suitable for submission to authorization authorities.
                        </p>
                      </div>
                      <Button onClick={handleGenerateSSP} disabled={isGenerating} className="w-full">
                        <Download className="h-4 w-4 mr-2" />
                        Generate DOCX
                      </Button>
                    </TabsContent>
                    
                    <TabsContent value="oscal" className="space-y-4">
                      <div className="p-4 bg-secondary/20 rounded-lg">
                        <h4 className="font-medium mb-2">OSCAL JSON Format</h4>
                        <p className="text-sm text-muted-foreground">
                          Export in Open Security Controls Assessment Language format for tool interoperability.
                        </p>
                      </div>
                      <Button onClick={handleGenerateSSP} disabled={isGenerating} className="w-full">
                        <Download className="h-4 w-4 mr-2" />
                        Generate OSCAL JSON
                      </Button>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}