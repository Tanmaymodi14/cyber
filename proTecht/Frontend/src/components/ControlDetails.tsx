import React, { useEffect } from 'react';
import { getACControls, getACControlDetail, getAIAnalysisControls, getAIAnalysisControl } from '../services/api';
import { toast } from 'sonner@2.0.3';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { ControlBadge } from './ControlBadge';
import { 
  Shield, 
  Search, 
  Filter,
  ChevronDown,
  CheckCircle,
  AlertTriangle,
  XCircle,
  FileText,
  ExternalLink,
  ArrowLeft,
  Menu,
  X,
  Database,
  BarChart3,
  Settings,
  User,
  LogOut,
  ChevronRight,
  Bell,
  RefreshCw
} from 'lucide-react';
import { useState } from 'react';

interface ControlDetailsProps {
  onNavigate: (page: string) => void;
  selectedFramework?: {id: string, title: string} | null;
}

export function ControlDetails({ onNavigate, selectedFramework }: ControlDetailsProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [deepLinkControl, setDeepLinkControl] = useState<string | null>(null);

  const [controls, setControls] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      try {
        toast.loading('Loading controls...', { id: 'load-controls' });
        
        // Get basic control data
        const list = await getACControls();
        
        // Try to get AI-enhanced data if available
        let aiAnalysis = [];
        try {
          aiAnalysis = await getAIAnalysisControls();
        } catch (err) {
          console.warn('AI analysis not available:', err);
          // Continue with basic data
        }
        
        // Map to current UI shape minimally
        const mapped = list.map((c) => {
          // Find matching AI analysis if available
          const aiData = aiAnalysis.find(ai => ai.controlId === c.id);
          
          return {
            id: c.id,
            title: c.name || controlNames[c.id] || c.id,
            status: c.status,
            score: c.score,
            evidenceSources: c.evidenceSources ?? [],
            whatWeChecked: aiData?.whatWeChecked || [],
            reasons: aiData?.reasons || c.reasons || [],
            missing: aiData?.missing || c.missingEvidence || [],
            linkedPolicySections: [],
            family: 'Access Control',
            type: 'technical',
            aiRecommendations: aiData?.recommendations || [],
          };
        });
        setControls(mapped);
        toast.success('Controls loaded', { id: 'load-controls' });
      } catch (e) {
        console.error('Failed to load controls', e);
        toast.error('Failed to load controls', { id: 'load-controls' });
      }
    })();
  }, []);

  // Apply deep-link control filter if present (#/controls?control=AC-15)
  useEffect(() => {
    const hash = window.location.hash || '';
    if (hash.startsWith('#/controls')) {
      const params = new URLSearchParams(hash.split('?')[1] || '');
      const control = params.get('control');
      if (control) {
        setSearchTerm(control);
        setDeepLinkControl(control);
      }
    }
  }, []);

  const controlsSample = [
    {
      id: 'AC-1',
      title: 'Access Control Policy and Procedures',
      status: 'pass',
      score: 95,
      evidenceSources: ['Policy'],
      whatWeChecked: ['Policy document completeness', 'Annual review process', 'Roles and responsibilities definition'],
      reasons: ['Policy includes all required elements', 'Annual review process documented', 'Roles and responsibilities clearly defined'],
      missing: [],
      linkedPolicySections: ['Access Control Policy v2.1 - Section 3.1'],
      family: 'Access Control',
      type: 'non-technical'
    },
    {
      id: 'AC-2',
      title: 'Account Management',
      status: 'partial',
      score: 78,
      evidenceSources: ['IAM', 'Policy'],
      whatWeChecked: ['IAM user provisioning', 'Account lifecycle management', 'Privileged account controls'],
      reasons: ['IAM user provisioning automated', 'Account review process documented'],
      missing: ['Automated deprovisioning for terminated employees', 'Guest account management procedures'],
      linkedPolicySections: ['System Access Control Procedure - Section 2.1'],
      family: 'Access Control',
      type: 'mixed'
    },
    {
      id: 'AC-3',
      title: 'Access Enforcement',
      status: 'pass',
      score: 92,
      evidenceSources: ['IAM', 'SSO'],
      whatWeChecked: ['Role-based access controls', 'Permission boundaries', 'Access enforcement mechanisms'],
      reasons: ['RBAC implemented via IAM roles', 'Permission boundaries configured', 'Access enforcement at application layer'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-4',
      title: 'Information Flow Enforcement',
      status: 'pass',
      score: 88,
      evidenceSources: ['WAF', 'VPC'],
      whatWeChecked: ['Network segmentation', 'Traffic filtering', 'Data flow controls'],
      reasons: ['WAF rules configured', 'VPC security groups restrict traffic', 'Network ACLs implemented'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-5',
      title: 'Separation of Duties',
      status: 'pass',
      score: 85,
      evidenceSources: ['IAM'],
      whatWeChecked: ['Role segregation', 'Administrative access controls', 'Approval workflows'],
      reasons: ['Administrative roles separated', 'Dual control for sensitive operations', 'Approval workflows implemented'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-6',
      title: 'Least Privilege',
      status: 'partial',
      score: 72,
      evidenceSources: ['IAM'],
      whatWeChecked: ['Permission sets', 'Role permissions', 'Access reviews'],
      reasons: ['Minimal permission sets defined', 'Regular access reviews conducted'],
      missing: ['Some users have excessive permissions', 'Temporary access not properly managed'],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-7',
      title: 'Unsuccessful Logon Attempts',
      status: 'pass',
      score: 94,
      evidenceSources: ['IAM', 'Config'],
      whatWeChecked: ['Account lockout policies', 'Failed login monitoring', 'Lockout duration settings'],
      reasons: ['Account lockout after 5 failed attempts', 'Lockout duration configured', 'Failed login alerts enabled'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-8',
      title: 'System Use Notification',
      status: 'partial',
      score: 76,
      evidenceSources: ['Policy'],
      whatWeChecked: ['Login banners', 'Usage notifications', 'Legal warnings'],
      reasons: ['Login banners configured', 'Usage notification policy exists'],
      missing: ['Technical implementation of system use notifications', 'Consent acknowledgment tracking'],
      linkedPolicySections: ['System Access Control Procedure - Section 3.2'],
      family: 'Access Control',
      type: 'mixed'
    },
    {
      id: 'AC-9',
      title: 'Previous Logon Notification',
      status: 'pass',
      score: 87,
      evidenceSources: ['IAM', 'CloudTrail'],
      whatWeChecked: ['Login history tracking', 'Previous logon notifications', 'Anomaly detection'],
      reasons: ['CloudTrail logs all authentication events', 'Login history available to users', 'Anomaly detection enabled'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-10',
      title: 'Concurrent Session Control',
      status: 'pass',
      score: 90,
      evidenceSources: ['SSO'],
      whatWeChecked: ['Session limits', 'Concurrent session controls', 'Session management'],
      reasons: ['Concurrent session limits configured', 'Session timeout implemented', 'Single sign-on enforced'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-11',
      title: 'Session Lock',
      status: 'pass',
      score: 89,
      evidenceSources: ['SSO', 'VPC'],
      whatWeChecked: ['Session timeout settings', 'Auto-lock mechanisms', 'Re-authentication requirements'],
      reasons: ['Session timeout after 8 hours', 'Auto-lock on inactivity', 'Re-authentication required'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-12',
      title: 'Session Termination',
      status: 'pass',
      score: 91,
      evidenceSources: ['SSO', 'VPC'],
      whatWeChecked: ['Session termination policies', 'Automatic logout', 'Resource cleanup'],
      reasons: ['Automatic session termination configured', 'Resource cleanup on logout', 'Session state cleared'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-13',
      title: 'Supervision and Review — Access Control',
      status: 'partial',
      score: 74,
      evidenceSources: ['GD', 'SH'],
      whatWeChecked: ['Access monitoring', 'Review processes', 'Compliance checks'],
      reasons: ['GuardDuty monitoring enabled', 'Security Hub provides centralized view'],
      missing: ['Formal access review schedule', 'Automated compliance reporting'],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-14',
      title: 'Permitted Actions Without Identification or Authentication',
      status: 'pass',
      score: 93,
      evidenceSources: ['Policy'],
      whatWeChecked: ['Public access policies', 'Anonymous access controls', 'Guest access procedures'],
      reasons: ['Public access policy documented', 'Anonymous access restricted', 'Guest access procedures defined'],
      missing: [],
      linkedPolicySections: ['Access Control Policy v2.1 - Section 4.3'],
      family: 'Access Control',
      type: 'non-technical'
    },
    {
      id: 'AC-15',
      title: 'Automated Marking',
      status: 'partial',
      score: 67,
      evidenceSources: ['S3'],
      whatWeChecked: ['Data classification markings', 'Automated tagging', 'Metadata management'],
      reasons: ['S3 bucket tagging implemented', 'Data classification framework exists'],
      missing: ['Automated marking for all data types', 'Classification metadata enforcement'],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-16',
      title: 'Security Attributes',
      status: 'pass',
      score: 84,
      evidenceSources: ['S3', 'KMS'],
      whatWeChecked: ['Security attribute assignment', 'Attribute-based access control', 'Encryption key management'],
      reasons: ['Security attributes assigned to resources', 'KMS key policies enforce attributes', 'S3 bucket policies use attributes'],
      missing: [],
      linkedPolicySections: [],
      family: 'Access Control',
      type: 'technical'
    },
    {
      id: 'AC-17',
      title: 'Remote Access',
      status: 'partial',
      score: 71,
      evidenceSources: ['Policy'],
      whatWeChecked: ['Remote access policies', 'VPN requirements', 'Authentication mechanisms'],
      reasons: ['Remote access policy framework established', 'VPN usage requirements defined'],
      missing: ['Technical evidence of VPN configuration', 'Multi-factor authentication for all remote access'],
      linkedPolicySections: ['Remote Access Policy - Section 1.2'],
      family: 'Access Control',
      type: 'mixed'
    },
    {
      id: 'AC-18',
      title: 'Wireless Access',
      status: 'partial',
      score: 69,
      evidenceSources: ['Policy'],
      whatWeChecked: ['Wireless access policies', 'Security configurations', 'Guest network controls'],
      reasons: ['Wireless access policy exists', 'Guest network procedures documented'],
      missing: ['Technical validation of wireless security settings', 'Wireless access point configurations'],
      linkedPolicySections: ['Remote Access Policy - Section 2.4'],
      family: 'Access Control',
      type: 'mixed'
    },
    {
      id: 'AC-19',
      title: 'Access Control for Mobile Devices',
      status: 'partial',
      score: 68,
      evidenceSources: ['Policy'],
      whatWeChecked: ['Mobile device policies', 'MDM implementation', 'Security controls'],
      reasons: ['Mobile device management policy exists', 'Security requirements documented'],
      missing: ['Technical MDM implementation evidence', 'Mobile device compliance monitoring'],
      linkedPolicySections: ['Remote Access Policy - Section 3.4'],
      family: 'Access Control',
      type: 'mixed'
    },
    {
      id: 'AC-20',
      title: 'Use of External Information Systems',
      status: 'pass',
      score: 86,
      evidenceSources: ['Policy'],
      whatWeChecked: ['External system usage policies', 'Security agreements', 'Risk assessments'],
      reasons: ['External system policy comprehensive', 'Security agreements in place', 'Risk assessment process documented'],
      missing: [],
      linkedPolicySections: ['Information Flow Policy - Section 2.3'],
      family: 'Access Control',
      type: 'non-technical'
    },
    {
      id: 'AC-21',
      title: 'Information Sharing',
      status: 'pass',
      score: 88,
      evidenceSources: ['S3', 'WAF', 'VPC'],
      whatWeChecked: ['Information sharing controls', 'Data transfer restrictions', 'Third-party access'],
      reasons: ['S3 bucket policies control sharing', 'WAF restricts data access', 'VPC controls network sharing'],
      missing: [],
      linkedPolicySections: ['Information Flow Policy - Section 4.1'],
      family: 'Access Control',
      type: 'mixed'
    },
    {
      id: 'AC-22',
      title: 'Publicly Accessible Content',
      status: 'pass',
      score: 92,
      evidenceSources: ['Policy'],
      whatWeChecked: ['Public content policies', 'Review processes', 'Approval workflows'],
      reasons: ['Public content policy established', 'Review and approval process documented', 'Regular content audits conducted'],
      missing: [],
      linkedPolicySections: ['Information Flow Policy - Section 5.2'],
      family: 'Access Control',
      type: 'non-technical'
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'partial':
        return <AlertTriangle className="h-4 w-4 text-amber-500" />;
      case 'fail':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      pass: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      partial: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
      fail: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    };
    
    return (
      <Badge className={variants[status as keyof typeof variants]}>
        {status.toUpperCase()}
      </Badge>
    );
  };

  const getRiskColor = (score: number) => {
    if (score <= 3) return 'text-green-600';
    if (score <= 6) return 'text-amber-600';
    return 'text-red-600';
  };

  const rows = controls && controls.length > 0 ? controls : controlsSample;
  const filteredControls = rows.filter(control => {
    const matchesSearch = control.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         control.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || control.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const toggleRow = async (id: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
      try {
        toast.loading('Loading control details...', { id: `ctrl-${id}` });
        
        // Get technical control details
        const detail = await getACControlDetail(id);
        
        // Try to get AI-enhanced analysis if available
        let aiDetail = null;
        try {
          aiDetail = await getAIAnalysisControl(id);
        } catch (err) {
          console.warn(`AI analysis for ${id} not available:`, err);
          // Continue with basic data
        }
        
        // Merge detail into current row state with AI data if available
        setControls(prev => prev.map(c => c.id === id ? {
          ...c,
          whatWeChecked: aiDetail?.whatWeChecked || detail.whatWeChecked || c.whatWeChecked || [],
          reasons: aiDetail?.reasons || detail.technicalResult?.reasons || c.reasons || [],
          missing: aiDetail?.missing || detail.technicalResult?.missing_evidence || c.missing || [],
          aiRecommendations: aiDetail?.recommendations || []
        } : c));
        
        toast.success('Control details loaded', { id: `ctrl-${id}` });
      } catch (e) {
        console.error(`Failed to load details for ${id}:`, e);
        toast.error('Failed to load control details', { id: `ctrl-${id}` });
      }
    }
    setExpandedRows(newExpanded);
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, current: false },
    { id: 'evidence', label: 'Evidence', icon: Database, current: false },
    { id: 'controls', label: 'Controls', icon: Shield, current: true },
    { id: 'ssp', label: 'SSP Generator', icon: FileText, current: false },
    { id: 'reports', label: 'Reports', icon: BarChart3, current: false },
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
                <h1 className="text-2xl font-bold">Control Details</h1>
                <p className="text-sm text-muted-foreground">Review and manage compliance controls</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5" />
              </Button>
              <Badge variant="secondary" className="px-3 py-1">
                22 AC Controls
              </Badge>
            </div>
          </div>
        </header>

        {/* Controls content */}
        <main className="flex-1 p-6 space-y-8 bg-background/50">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Filter Controls</CardTitle>
              <CardDescription>
                Search and filter controls by status and keywords
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search controls..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border border-border rounded-md bg-background"
                  >
                    <option value="all">All Status</option>
                    <option value="pass">Pass</option>
                    <option value="partial">Partial</option>
                    <option value="fail">Fail</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Controls Table */}
          <Card>
            <CardHeader>
              <CardTitle>Control Assessment Results</CardTitle>
              <CardDescription>
                Detailed view of compliance control assessments with AI recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="min-w-[300px]">Control ID</TableHead>
                      <TableHead className="min-w-[120px]">Status</TableHead>
                      <TableHead className="min-w-[100px]">Score</TableHead>
                      <TableHead className="min-w-[150px]">Evidence Sources</TableHead>
                      <TableHead className="w-[50px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredControls.map((control) => (
                      <React.Fragment key={control.id}>
                        <TableRow className="cursor-pointer hover:bg-muted/50">
                          <TableCell className="font-medium">
                            <div>
                              <div className="font-semibold">{control.id}</div>
                              <div className="text-sm text-muted-foreground mt-1">{control.title}</div>
                              <div className="mt-2">
                                <ControlBadge controlId={control.id} size="sm" />
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(control.status)}
                              {getStatusBadge(control.status)}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-center">
                              <span className={`font-semibold text-lg ${getRiskColor(100 - control.score)}`}>
                                {control.score}
                              </span>
                              <span className="text-sm text-muted-foreground">/100</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-wrap gap-1">
                              {control.evidenceSources.map((source, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {source}
                                </Badge>
                              ))}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Collapsible>
                              <CollapsibleTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => toggleRow(control.id)}
                                >
                                  <ChevronDown className={`h-4 w-4 transition-transform ${
                                    expandedRows.has(control.id) ? 'rotate-180' : ''
                                  }`} />
                                </Button>
                              </CollapsibleTrigger>
                            </Collapsible>
                          </TableCell>
                        </TableRow>
                        
                        {expandedRows.has(control.id) && (
                          <TableRow>
                            <TableCell colSpan={5} className="bg-muted/20 p-0">
                              <div className="p-6 space-y-6">
                                {/* What we checked */}
                                <div>
                                  <h4 className="font-semibold mb-3 flex items-center">
                                    <div className="w-6 h-6 bg-primary/10 rounded flex items-center justify-center mr-2">
                                      <CheckCircle className="h-4 w-4 text-primary" />
                                    </div>
                                    What we checked
                                  </h4>
                                  <ul className="space-y-1">
                                    {control.whatWeChecked.map((item, index) => (
                                      <li key={index} className="flex items-center space-x-2 text-sm">
                                        <div className="w-1.5 h-1.5 bg-primary rounded-full flex-shrink-0"></div>
                                        <span>{item}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {/* Reasons */}
                                <div>
                                  <h4 className="font-semibold mb-3 flex items-center">
                                    <div className="w-6 h-6 bg-green-500/10 rounded flex items-center justify-center mr-2">
                                      <CheckCircle className="h-4 w-4 text-green-500" />
                                    </div>
                                    Reasons (Pass/Partial)
                                  </h4>
                                  <ul className="space-y-1">
                                    {control.reasons.map((reason, index) => (
                                      <li key={index} className="flex items-start space-x-2 text-sm">
                                        <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                        <span>{reason}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {/* Missing evidence */}
                                {control.missing.length > 0 && (
                                  <div>
                                    <h4 className="font-semibold mb-3 flex items-center">
                                      <div className="w-6 h-6 bg-red-500/10 rounded flex items-center justify-center mr-2">
                                        <XCircle className="h-4 w-4 text-red-500" />
                                      </div>
                                      Missing Evidence
                                    </h4>
                                    <ul className="space-y-1">
                                      {control.missing.map((item, index) => (
                                        <li key={index} className="flex items-start space-x-2 text-sm">
                                          <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                                          <span>{item}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                                
                                {/* AI Recommendations */}
                                {control.aiRecommendations && control.aiRecommendations.length > 0 && (
                                  <div>
                                    <h4 className="font-semibold mb-3 flex items-center">
                                      <div className="w-6 h-6 bg-blue-500/10 rounded flex items-center justify-center mr-2">
                                        <Shield className="h-4 w-4 text-blue-500" />
                                      </div>
                                      AI Recommendations
                                    </h4>
                                    <ul className="space-y-1">
                                      {control.aiRecommendations.map((item, index) => (
                                        <li key={index} className="flex items-start space-x-2 text-sm">
                                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                          <span>{item}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {/* Linked policy sections */}
                                {control.linkedPolicySections.length > 0 && (
                                  <div>
                                    <h4 className="font-semibold mb-3 flex items-center">
                                      <div className="w-6 h-6 bg-blue-500/10 rounded flex items-center justify-center mr-2">
                                        <FileText className="h-4 w-4 text-blue-500" />
                                      </div>
                                      Linked Policy Sections
                                    </h4>
                                    <div className="space-y-2">
                                      {control.linkedPolicySections.map((section, index) => (
                                        <div key={index} className="p-2 bg-blue-50 dark:bg-blue-950/20 rounded border-l-2 border-blue-500 text-sm">
                                          {section}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Mixed controls note */}
                                {control.type === 'mixed' && (
                                  <div className="bg-amber-50 dark:bg-amber-950/20 p-3 rounded-lg border border-amber-200 dark:border-amber-800">
                                    <p className="text-sm text-amber-800 dark:text-amber-200">
                                      <strong>Mixed Control:</strong> This control requires both technical and policy evidence for full compliance.
                                    </p>
                                  </div>
                                )}

                                {/* Action buttons */}
                                <div className="flex space-x-2 pt-4 border-t">
                                  <Button variant="outline" size="sm">
                                    <ExternalLink className="h-4 w-4 mr-2" />
                                    View JSON Evidence
                                  </Button>
                                  <Button variant="outline" size="sm">
                                    <ExternalLink className="h-4 w-4 mr-2" />
                                    Export
                                  </Button>
                                  <Button variant="outline" size="sm">
                                    <RefreshCw className="h-4 w-4 mr-2" />
                                    Re-collect AWS
                                  </Button>
                                  <Button variant="outline" size="sm">
                                    <Search className="h-4 w-4 mr-2" />
                                    Re-analyze
                                  </Button>
                                </div>
                              </div>
                            </TableCell>
                          </TableRow>
                        )}
                      </React.Fragment>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}