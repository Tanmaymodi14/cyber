import React, { useEffect, useState } from 'react';
import { getAWSServices, getPolicies, getServiceDetail, recollectAWS, uploadPolicy, reanalyzePolicy, exportService, exportServices, exportControls } from '../services/api';
import { toast } from 'sonner@2.0.3';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { ScrollArea } from './ui/scroll-area';
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from './ui/drawer';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ControlBadge } from './ControlBadge';
import { 
  Shield, 
  Search,
  Cloud,
  FileText,
  Upload,
  Download,
  ExternalLink,
  ArrowLeft,
  Menu,
  X,
  Database,
  CheckCircle,
  AlertTriangle,
  BarChart3,
  Settings,
  User,
  LogOut,
  ChevronRight,
  Bell,
  Copy,
  RefreshCw,
  Filter,
  CloudCog,
  Key,
  Lock,
  Eye,
  Activity,
  AlertCircle,
  ShieldCheck,
  Globe,
  Clock,
  FileX
} from 'lucide-react';

interface EvidenceManagementProps {
  onNavigate: (page: string) => void;
  selectedFramework?: {id: string, title: string} | null;
}

export function EvidenceManagement({ onNavigate, selectedFramework }: EvidenceManagementProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJsonData, setSelectedJsonData] = useState<any>(null);
  const [isJsonDialogOpen, setIsJsonDialogOpen] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState<any>(null);
  const [isPolicyDrawerOpen, setIsPolicyDrawerOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('aws');
  const [uploading, setUploading] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedControl, setSelectedControl] = useState('all');
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  // State: services and policies (fetched)
  const [awsServices, setAwsServices] = useState<any[]>([]);
  const [uploadedPolicies, setUploadedPolicies] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      try {
        toast.loading('Loading evidence...', { id: 'load-evidence' });
        const services = await getAWSServices();
        setAwsServices(services);
        const policies = await getPolicies();
        setUploadedPolicies(policies);
        toast.success('Evidence loaded', { id: 'load-evidence' });
      } catch (e) {
        console.error('Failed to load data', e);
        toast.error('Failed to load evidence', { id: 'load-evidence' });
      }
    })();
  }, []);

  // Example fallback sample if API not yet running
  const sampleServices = [
    {
      id: 'iam-config',
      title: 'IAM Configuration',
      lastUpdated: '2024-01-15',
      status: 'Current',
      kpis: {
        Users: 47,
        Roles: 23,
        Policies: 156
      },
      mappedControls: ['AC-3', 'AC-5', 'AC-6', 'AC-7', 'AC-9'],
      icon: Key,
      evidenceSnippet: 'Password policy enforces 14+ characters, MFA enabled for 89% of users, 0 users with console access without MFA'
    },
    {
      id: 'identity-center',
      title: 'Identity Center (SSO)',
      lastUpdated: '2024-01-14',
      status: 'Current',
      kpis: {
        PermissionSets: 12,
        SessionTimeout: '8h',
        MFA: 'Required'
      },
      mappedControls: ['AC-10', 'AC-11', 'AC-12'],
      icon: ShieldCheck,
      evidenceSnippet: 'Session timeout configured to 8 hours, MFA required for all access, 12 permission sets with least privilege'
    },
    {
      id: 'aws-config',
      title: 'AWS Config',
      lastUpdated: '2024-01-15',
      status: 'Current',
      kpis: {
        RulesTotal: 45,
        LockoutRules: 8
      },
      mappedControls: ['AC-7'],
      icon: CloudCog,
      evidenceSnippet: '45 config rules active, 8 account lockout rules enforced, 100% compliance for critical configurations'
    },
    {
      id: 's3-policies',
      title: 'S3 Bucket Policies',
      lastUpdated: '2024-01-13',
      status: 'Warning',
      kpis: {
        Buckets: 8,
        PublicBuckets: 0,
        Encrypted: 6,
        ObjectLockBuckets: 3
      },
      mappedControls: ['AC-15', 'AC-16', 'AC-21'],
      icon: Lock,
      evidenceSnippet: '8 buckets total, 0 public buckets, 6/8 encrypted, object lock enabled on 3 critical buckets'
    },
    {
      id: 'kms',
      title: 'KMS',
      lastUpdated: '2024-01-14',
      status: 'Current',
      kpis: {
        Keys: 15,
        RotationEnabled: 12
      },
      mappedControls: ['AC-16'],
      icon: Key,
      evidenceSnippet: '15 KMS keys managed, 12 with automatic rotation, key usage audited via CloudTrail'
    },
    {
      id: 'cloudtrail',
      title: 'CloudTrail',
      lastUpdated: '2024-01-15',
      status: 'Current',
      kpis: {
        Trails: 3,
        Events: 15420,
        RetentionDays: 90
      },
      mappedControls: ['AC-9'],
      icon: Activity,
      evidenceSnippet: '3 trails configured, 15,420 events logged today, 90-day retention, file validation enabled'
    },
    {
      id: 'waf',
      title: 'WAF',
      lastUpdated: '2024-01-14',
      status: 'Current',
      kpis: {
        WebACLs: 4,
        Blocked7d: 1247
      },
      mappedControls: ['AC-4', 'AC-21'],
      icon: Shield,
      evidenceSnippet: '4 Web ACLs protecting applications, 1,247 requests blocked in last 7 days'
    },
    {
      id: 'guardduty',
      title: 'GuardDuty',
      lastUpdated: '2024-01-15',
      status: 'Current',
      kpis: {
        Detector: 'Enabled',
        'Critical/High': 2
      },
      mappedControls: ['AC-13'],
      icon: AlertCircle,
      evidenceSnippet: 'Threat detection enabled, 2 high/critical findings under investigation, ML-based monitoring active'
    },
    {
      id: 'security-hub',
      title: 'Security Hub',
      lastUpdated: '2024-01-15',
      status: 'Warning',
      kpis: {
        Enabled: 'Yes',
        OpenFindings: 23
      },
      mappedControls: ['AC-13'],
      icon: ShieldCheck,
      evidenceSnippet: 'Security Hub enabled across all regions, 23 open findings, automated remediation for 67% of issues'
    },
    {
      id: 'vpc-cloudfront',
      title: 'VPC/CloudFront',
      lastUpdated: '2024-01-14',
      status: 'Current',
      kpis: {
        FlowLogs: 'On',
        Distributions: 6,
        TLSPolicy: 'v1.2+'
      },
      mappedControls: ['AC-4', 'AC-11', 'AC-12', 'AC-21'],
      icon: Globe,
      evidenceSnippet: 'VPC Flow Logs enabled, 6 CloudFront distributions, TLS 1.2+ enforced, geo-restrictions configured'
    }
  ];

  // Sample policies used only if API returns none
  const samplePolicies = [
    {
      id: 'policy-001',
      name: 'Access Control Policy v2.1',
      controlsMapped: ['AC-1', 'AC-14'],
      lastAnalyzed: '2024-01-10',
      status: 'Compliant',
      type: 'non-technical',
      summary: 'Comprehensive access control policy covering organizational procedures, roles, and responsibilities.',
      reasons: ['Policy includes all required elements', 'Annual review process documented', 'Roles and responsibilities clearly defined'],
      missing: [],
      recommendations: ['Consider adding remote access provisions', 'Include AI/ML system access controls'],
      citations: ['Section 3.1: User Access Management', 'Section 4.2: Privileged Access Controls']
    },
    {
      id: 'policy-002',
      name: 'System Access Control Procedure',
      controlsMapped: ['AC-2', 'AC-8'],
      lastAnalyzed: '2024-01-08',
      status: 'Partial',
      type: 'mixed',
      summary: 'Defines user account management and system access procedures with some technical implementation gaps.',
      reasons: ['Account provisioning process documented', 'User access review procedures defined'],
      missing: ['Technical implementation details for automated provisioning', 'Integration with identity management systems'],
      recommendations: ['Add technical specifications for account automation', 'Include API access management procedures'],
      citations: ['Section 2.1: Account Provisioning', 'Section 5.3: Access Reviews']
    },
    {
      id: 'policy-003',
      name: 'Remote Access Policy',
      controlsMapped: ['AC-17', 'AC-18', 'AC-19'],
      lastAnalyzed: '2024-01-05',
      status: 'Needs Technical Evidence',
      type: 'mixed',
      summary: 'Policy framework for remote access with references to technical controls that require validation.',
      reasons: ['Remote access policy framework established', 'VPN usage requirements defined'],
      missing: ['Technical evidence of VPN configuration', 'Mobile device management implementation', 'Wireless access point configurations'],
      recommendations: ['Collect VPN logs and configurations', 'Document MDM policies and technical implementation', 'Validate wireless security controls'],
      citations: ['Section 1.2: VPN Requirements', 'Section 3.4: Mobile Device Controls']
    },
    {
      id: 'policy-004',
      name: 'Information Flow Policy',
      controlsMapped: ['AC-20', 'AC-22'],
      lastAnalyzed: '2024-01-03',
      status: 'Compliant',
      type: 'non-technical',
      summary: 'Organizational policy for information sharing and external system connections.',
      reasons: ['Information sharing agreements documented', 'External connection approval process defined', 'Data classification requirements included'],
      missing: [],
      recommendations: ['Consider cloud service provider agreements', 'Add data residency requirements'],
      citations: ['Section 2.3: External Connections', 'Section 4.1: Information Sharing Agreements']
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'current':
      case 'compliant':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'warning':
      case 'partial':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200';
      case 'needs technical evidence':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'current':
      case 'compliant':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
      case 'partial':
        return <AlertTriangle className="h-4 w-4 text-amber-500" />;
      case 'needs technical evidence':
        return <AlertCircle className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const handleViewJson = async (service: any) => {
    try {
      toast.loading('Fetching evidence...', { id: 'svc-detail' });
      const detail = await getServiceDetail(service.id);
      setSelectedJsonData({ type: service.title, id: service.id, data: detail });
      setIsJsonDialogOpen(true);
      toast.success('Evidence fetched', { id: 'svc-detail' });
    } catch (e) {
      console.error('Failed to load service detail', e);
      toast.error('Failed to fetch evidence', { id: 'svc-detail' });
    }
  };

  const handlePolicyView = (policy: any) => {
    setSelectedPolicy(policy);
    setIsPolicyDrawerOpen(true);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      console.log('JSON copied to clipboard');
    });
  };

  const servicesToShow = awsServices && awsServices.length > 0 ? awsServices : sampleServices;
  const policiesToShow = uploadedPolicies && uploadedPolicies.length > 0 ? uploadedPolicies : samplePolicies;

  // Fallback icon mapping for API items that don't include an icon component
  const iconMap: Record<string, any> = {
    'iam-config': Key,
    'identity-center': ShieldCheck,
    'aws-config': CloudCog,
    's3-policies': Lock,
    'kms': Key,
    'cloudtrail': Activity,
    'waf': Shield,
    'guardduty': AlertCircle,
    'security-hub': ShieldCheck,
    'vpc-cloudfront': Globe,
  };

  const filteredServices = servicesToShow.filter(service => {
    const matchesSearch = service.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         service.mappedControls.some(control => control.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = selectedStatus === 'all' || service.status.toLowerCase() === selectedStatus.toLowerCase();
    const matchesControl = selectedControl === 'all' || service.mappedControls.includes(selectedControl);
    
    return matchesSearch && matchesStatus && matchesControl;
  });

  const filteredPolicies = policiesToShow.filter(policy => {
    const matchesSearch = policy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         policy.controlsMapped.some(control => control.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  });

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, current: false },
    { id: 'evidence', label: 'Evidence', icon: Database, current: true },
    { id: 'controls', label: 'Controls', icon: Shield, current: false },
    { id: 'ssp', label: 'SSP Generator', icon: FileText, current: false },
    { id: 'reports', label: 'Reports', icon: BarChart3, current: false },
    { id: 'settings', label: 'Settings', icon: Settings, current: false }
  ];

  // Get unique control values for filter
  const allControls = [...new Set(awsServices.flatMap(s => s.mappedControls))].sort();

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
                  <h1>Evidence Management</h1>
                  <p className="text-sm text-muted-foreground">Manage and organize compliance evidence</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Button variant="ghost" size="sm" className="relative">
                  <Bell className="h-5 w-5" />
                </Button>
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Evidence
                </Button>
              </div>
            </div>
          </header>

          {/* Evidence content */}
          <main className="flex-1 p-6 space-y-6 overflow-y-auto">
            {/* Search and Export */}
            <div className="flex gap-4 items-center">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search evidence..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => exportServices()}
                >
                  <Download className="h-4 w-4 mr-1" />
                  Export Services
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => exportControls()}
                >
                  <Download className="h-4 w-4 mr-1" />
                  Export Controls
                </Button>
              </div>
            </div>

            {/* Evidence Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="aws" className="flex items-center space-x-2">
                  <Cloud className="h-4 w-4" />
                  <span>AWS Data</span>
                </TabsTrigger>
                <TabsTrigger value="uploaded" className="flex items-center space-x-2">
                  <FileText className="h-4 w-4" />
                  <span>Uploaded Policies</span>
                </TabsTrigger>
              </TabsList>

              {/* AWS Data Tab */}
              <TabsContent value="aws" className="space-y-6">
                {/* Filters */}
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex flex-wrap gap-4">
                      <div className="flex items-center space-x-2">
                        <Filter className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Filters:</span>
                      </div>
                      <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                        <SelectTrigger className="w-32">
                          <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Status</SelectItem>
                          <SelectItem value="current">Current</SelectItem>
                          <SelectItem value="warning">Warning</SelectItem>
                        </SelectContent>
                      </Select>
                      <Select value={selectedControl} onValueChange={setSelectedControl}>
                        <SelectTrigger className="w-32">
                          <SelectValue placeholder="Control" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Controls</SelectItem>
                          {allControls.map(control => (
                            <SelectItem key={control} value={control}>{control}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>

                {/* Service Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {filteredServices.map((service) => {
                    const Icon = (service as any).icon || iconMap[service.id] || Cloud;
                    return (
                      <Card 
                        key={service.id} 
                        className="hover:shadow-lg hover:shadow-primary/5 transition-all duration-200 relative"
                        onMouseEnter={() => setHoveredCard(service.id)}
                        onMouseLeave={() => setHoveredCard(null)}
                      >
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <CardTitle className="flex items-center space-x-2">
                                <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
                                  <Icon className="h-4 w-4 text-primary" />
                                </div>
                                <span>{service.title}</span>
                              </CardTitle>
                              <CardDescription className="mt-2">
                                Last updated: {service.lastUpdated}
                              </CardDescription>
                            </div>
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(service.status)}
                              <Badge className={getStatusColor(service.status)}>
                                {service.status}
                              </Badge>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          {/* KPIs */}
                          <div className="grid grid-cols-2 gap-3">
                            {Object.entries(service.kpis).map(([key, value]) => (
                              <div key={key} className="text-center p-3 bg-secondary/20 rounded-lg">
                                <div className="font-bold text-primary">{value}</div>
                                <div className="text-xs text-muted-foreground">{key}</div>
                              </div>
                            ))}
                          </div>

                          {/* Mapped Controls */}
                          <div>
                            <p className="text-sm font-medium mb-2">Mapped Controls:</p>
                            <div className="flex flex-wrap gap-1">
                              {service.mappedControls.map((control) => (
                                <button
                                  key={control}
                                  onClick={() => {
                                    try {
                                      // Deep link to Controls with control filter
                                      const url = new URL(window.location.href);
                                      url.hash = `#/controls?control=${encodeURIComponent(control)}`;
                                      window.location.replace(url.toString());
                                    } catch (e) {
                                      console.error('Deep link failed', e);
                                    }
                                  }}
                                  className="focus:outline-none"
                                  title={`Filter Controls by ${control}`}
                                >
                                  <ControlBadge controlId={control} size="sm" />
                                </button>
                              ))}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex space-x-2">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="flex-1"
                              onClick={() => handleViewJson(service)}
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              View JSON
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="flex-1"
                              onClick={() => exportService(service.id)}
                            >
                              <Download className="h-4 w-4 mr-1" />
                              Export
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              title="Re-collect from AWS"
                              className="px-3"
                              onClick={async () => {
                                try {
                                  toast.loading('Re-collecting from AWS...', { id: 'recollect' });
                                  await recollectAWS();
                                  const refreshed = await getAWSServices();
                                  setAwsServices(refreshed);
                                  toast.success('Re-collect complete', { id: 'recollect' });
                                } catch (e) {
                                  console.error('Re-collect failed', e);
                                  toast.error('Re-collect failed', { id: 'recollect' });
                                }
                              }}
                            >
                              <RefreshCw className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>

                        {/* Hover tooltip */}
                        {hoveredCard === service.id && (
                          <div className="absolute z-10 top-full left-0 right-0 mt-2 p-3 bg-card border border-border rounded-lg shadow-lg">
                            <p className="text-sm">{service.evidenceSnippet}</p>
                          </div>
                        )}
                      </Card>
                    );
                  })}
                </div>
              </TabsContent>

              {/* Uploaded Policies Tab */}
              <TabsContent value="uploaded" className="space-y-6">
                <Card>
                  <CardContent className="p-0">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Policy Name</TableHead>
                          <TableHead>Controls Mapped</TableHead>
                          <TableHead>Last Analyzed</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredPolicies.map((policy) => (
                          <TableRow key={policy.id}>
                            <TableCell>
                              <div className="flex items-center space-x-3">
                                <FileText className="h-4 w-4 text-primary" />
                                <span className="font-medium">{policy.name}</span>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex flex-wrap gap-1">
                                {policy.controlsMapped.map((control) => (
                                  <ControlBadge key={control} controlId={control} size="sm" />
                                ))}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                <Clock className="h-4 w-4 text-muted-foreground" />
                                <span>{policy.lastAnalyzed}</span>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                {getStatusIcon(policy.status)}
                                <Badge className={getStatusColor(policy.status)}>
                                  {policy.status}
                                </Badge>
                                {policy.type === 'mixed' && (
                                  <Badge variant="outline" className="text-xs">
                                    Requires technical evidence
                                  </Badge>
                                )}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex space-x-2">
                                <Button 
                                  variant="outline" 
                                  size="sm"
                                  onClick={() => handlePolicyView(policy)}
                                >
                                  <Eye className="h-4 w-4 mr-1" />
                                  View Report
                                </Button>
                                <Button 
                                  variant="outline" 
                                  size="sm"
                                  onClick={async () => {
                                    try {
                                      toast.loading('Re-analyzing policy...', { id: 'reanalyze-policy' });
                                      await reanalyzePolicy(policy.id);
                                      const refreshed = await getPolicies();
                                      setPolicies(refreshed);
                                      toast.success('Policy re-analyzed successfully', { id: 'reanalyze-policy' });
                                    } catch (e) {
                                      console.error('Policy reanalysis failed', e);
                                      toast.error('Policy reanalysis failed', { id: 'reanalyze-policy' });
                                    }
                                  }}
                                >
                                  <RefreshCw className="h-4 w-4 mr-1" />
                                  Re-analyze
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>

                {/* Upload Area */}
                <Card className="border-2 border-dashed border-border hover:border-primary/50 transition-colors">
                  <CardContent className="py-12">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <Upload className="h-8 w-8 text-primary" />
                      </div>
                      <h3 className="font-semibold mb-2">Upload Policy Documents</h3>
                      <p className="text-muted-foreground mb-6">
                        Drag & drop policy files here or click to browse
                      </p>
                            <label className="inline-flex items-center px-4 py-2 bg-secondary/50 rounded cursor-pointer">
                              <Upload className="h-4 w-4 mr-2" />
                              <span>{uploading ? 'Uploading...' : 'Choose Files'}</span>
                              <input
                                type="file"
                                multiple
                                accept=".pdf,.doc,.docx,.txt"
                                className="hidden"
                                onChange={async (e) => {
                                  if (!e.target.files?.length) return;
                                  
                                  // Validate files before uploading
                                  const files = Array.from(e.target.files);
                                  const maxSize = 10 * 1024 * 1024; // 10MB
                                  const validTypes = ['.pdf', '.doc', '.docx', '.txt'];
                                  
                                  // Check file types and sizes
                                  const invalidFiles = files.filter(file => {
                                    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
                                    const validType = validTypes.includes(extension);
                                    const validSize = file.size <= maxSize;
                                    return !validType || !validSize;
                                  });
                                  
                                  if (invalidFiles.length > 0) {
                                    const tooLarge = invalidFiles.filter(f => f.size > maxSize);
                                    const wrongType = invalidFiles.filter(f => {
                                      const ext = '.' + f.name.split('.').pop()?.toLowerCase();
                                      return !validTypes.includes(ext);
                                    });
                                    
                                    if (tooLarge.length > 0) {
                                      toast.error(`${tooLarge.length} file(s) exceed the 10MB size limit`);
                                    }
                                    
                                    if (wrongType.length > 0) {
                                      toast.error(`${wrongType.length} file(s) have invalid types. Allowed: PDF, DOC, DOCX, TXT`);
                                    }
                                    
                                    e.currentTarget.value = '';
                                    return;
                                  }
                                  
                                  setUploading(true);
                                  toast.loading('Uploading policy documents...', { id: 'policy-upload' });
                                  
                                  try {
                                    let successCount = 0;
                                    let failCount = 0;
                                    
                                    for (const file of files) {
                                      try {
                                        await uploadPolicy(file, file.name);
                                        successCount++;
                                      } catch (uploadErr) {
                                        console.error(`Failed to upload ${file.name}:`, uploadErr);
                                        failCount++;
                                      }
                                    }
                                    
                                    if (successCount > 0 && failCount === 0) {
                                      toast.success(`Successfully uploaded ${successCount} policy document(s)`, { id: 'policy-upload' });
                                    } else if (successCount > 0 && failCount > 0) {
                                      toast.warning(`Uploaded ${successCount} document(s), but ${failCount} failed`, { id: 'policy-upload' });
                                    } else {
                                      toast.error('All policy uploads failed', { id: 'policy-upload' });
                                    }
                                    
                                    // Refresh policies list
                                    const pol = await getPolicies();
                                    setUploadedPolicies(pol);
                                  } catch (err) {
                                    console.error('Policy upload error:', err);
                                    toast.error('Policy upload failed', { id: 'policy-upload' });
                                  } finally {
                                    setUploading(false);
                                    e.currentTarget.value = '';
                                  }
                                }}
                              />
                            </label>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            {/* JSON Viewer Dialog */}
            <Dialog open={isJsonDialogOpen} onOpenChange={setIsJsonDialogOpen}>
              <DialogContent className="max-w-4xl max-h-[80vh]">
                <DialogHeader>
                  <DialogTitle className="flex items-center space-x-2">
                    <Cloud className="h-5 w-5 text-primary" />
                    <span>{selectedJsonData?.type} - Evidence Data</span>
                  </DialogTitle>
                  <DialogDescription>
                    Raw evidence data for compliance assessment and audit purposes.
                  </DialogDescription>
                </DialogHeader>
                
                <div className="space-y-4">
                  <div className="flex justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(JSON.stringify(selectedJsonData?.data, null, 2))}
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy JSON
                    </Button>
                  </div>
                  
                  <ScrollArea className="h-[500px] w-full">
                    <pre className="text-sm bg-muted p-4 rounded-lg overflow-x-auto font-mono">
                      <code>
                        {selectedJsonData?.data && JSON.stringify(selectedJsonData.data, null, 2)}
                      </code>
                    </pre>
                  </ScrollArea>
                </div>
              </DialogContent>
            </Dialog>

            {/* Policy Analysis Drawer */}
            <Drawer open={isPolicyDrawerOpen} onOpenChange={setIsPolicyDrawerOpen}>
              <DrawerContent className="max-h-[80vh]">
                <DrawerHeader>
                  <DrawerTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-primary" />
                    <span>{selectedPolicy?.name}</span>
                  </DrawerTitle>
                  <DrawerDescription>
                    AI-powered policy analysis and compliance assessment
                  </DrawerDescription>
                </DrawerHeader>
                
                {selectedPolicy && (
                  <div className="p-6 space-y-6">
                    {/* Summary */}
                    <div>
                      <h4 className="font-semibold mb-2">Summary</h4>
                      <p className="text-sm text-muted-foreground">{selectedPolicy.summary}</p>
                    </div>

                    {/* Reasons */}
                    <div>
                      <h4 className="font-semibold mb-2">Assessment Reasons</h4>
                      <ul className="space-y-1">
                        {selectedPolicy.reasons.map((reason: string, index: number) => (
                          <li key={index} className="flex items-start space-x-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Missing Requirements */}
                    {selectedPolicy.missing.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Missing Requirements</h4>
                        <ul className="space-y-1">
                          {selectedPolicy.missing.map((item: string, index: number) => (
                            <li key={index} className="flex items-start space-x-2 text-sm">
                              <FileX className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Recommendations */}
                    <div>
                      <h4 className="font-semibold mb-2">Recommendations</h4>
                      <ul className="space-y-1">
                        {selectedPolicy.recommendations.map((rec: string, index: number) => (
                          <li key={index} className="flex items-start space-x-2 text-sm">
                            <AlertCircle className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Citations */}
                    <div>
                      <h4 className="font-semibold mb-2">Citations</h4>
                      <ul className="space-y-1">
                        {selectedPolicy.citations.map((citation: string, index: number) => (
                          <li key={index} className="text-sm p-2 bg-secondary/20 rounded border-l-2 border-primary">
                            {citation}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </DrawerContent>
            </Drawer>
          </main>
        </div>
      </div>
    </div>
  );
}