import { Badge } from './ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';
import { Shield, Info } from 'lucide-react';

// Comprehensive control database
const controlsDatabase: Record<string, {
  family: string;
  name: string;
  description: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
}> = {
  // Access Control (AC) Family
  'AC-1': {
    family: 'Access Control',
    name: 'Access Control Policy and Procedures',
    description: 'Establishes organizational access control policy and procedures for implementing access control requirements.',
    riskLevel: 'MEDIUM'
  },
  'AC-2': {
    family: 'Access Control',
    name: 'Account Management',
    description: 'Manages information system accounts including identification, creation, enabling, modification, review, and removal.',
    riskLevel: 'HIGH'
  },
  'AC-3': {
    family: 'Access Control',
    name: 'Access Enforcement',
    description: 'Enforces approved authorizations for logical access to information and system resources.',
    riskLevel: 'HIGH'
  },
  'AC-4': {
    family: 'Access Control',
    name: 'Information Flow Enforcement',
    description: 'Controls information flows between system and interconnected systems based on approved authorizations.',
    riskLevel: 'HIGH'
  },
  'AC-5': {
    family: 'Access Control',
    name: 'Separation of Duties',
    description: 'Separates duties of individuals to reduce risk of malevolent activity without collusion.',
    riskLevel: 'MEDIUM'
  },
  'AC-6': {
    family: 'Access Control',
    name: 'Least Privilege',
    description: 'Employs principle of least privilege, allowing only authorized accesses necessary to accomplish assigned tasks.',
    riskLevel: 'HIGH'
  },
  'AC-7': {
    family: 'Access Control',
    name: 'Unsuccessful Logon Attempts',
    description: 'Enforces limits on consecutive invalid logon attempts and takes action when threshold is exceeded.',
    riskLevel: 'MEDIUM'
  },

  // Audit and Accountability (AU) Family
  'AU-1': {
    family: 'Audit and Accountability',
    name: 'Audit and Accountability Policy',
    description: 'Establishes organizational audit and accountability policy and procedures.',
    riskLevel: 'MEDIUM'
  },
  'AU-2': {
    family: 'Audit and Accountability',
    name: 'Event Logging',
    description: 'Ensures that the information system is capable of auditing specific events and content of audit records.',
    riskLevel: 'HIGH'
  },
  'AU-3': {
    family: 'Audit and Accountability',
    name: 'Content of Audit Records',
    description: 'Ensures audit records contain sufficient information to establish what events occurred and their outcomes.',
    riskLevel: 'HIGH'
  },
  'AU-4': {
    family: 'Audit and Accountability',
    name: 'Audit Storage Capacity',
    description: 'Allocates audit record storage capacity and configures auditing to reduce likelihood of capacity being exceeded.',
    riskLevel: 'MEDIUM'
  },
  'AU-5': {
    family: 'Audit and Accountability',
    name: 'Response to Audit Processing Failures',
    description: 'Alerts appropriate personnel in event of audit processing failure and takes corrective action.',
    riskLevel: 'HIGH'
  },
  'AU-6': {
    family: 'Audit and Accountability',
    name: 'Audit Review, Analysis, and Reporting',
    description: 'Reviews and analyzes information system audit records for indications of inappropriate activity.',
    riskLevel: 'MEDIUM'
  },
  'AU-12': {
    family: 'Audit and Accountability',
    name: 'Audit Generation',
    description: 'Provides audit record generation capability for auditable events at system components.',
    riskLevel: 'HIGH'
  },

  // System and Communications Protection (SC) Family
  'SC-7': {
    family: 'System and Communications Protection',
    name: 'Boundary Protection',
    description: 'Monitors and controls communications at external boundary and key internal boundaries.',
    riskLevel: 'HIGH'
  },
  'SC-8': {
    family: 'System and Communications Protection',
    name: 'Transmission Confidentiality and Integrity',
    description: 'Protects confidentiality and integrity of transmitted information.',
    riskLevel: 'HIGH'
  },
  'SC-13': {
    family: 'System and Communications Protection',
    name: 'Cryptographic Protection',
    description: 'Implements cryptographic mechanisms to prevent unauthorized disclosure and modification of information.',
    riskLevel: 'HIGH'
  },
  'SC-28': {
    family: 'System and Communications Protection',
    name: 'Protection of Information at Rest',
    description: 'Protects confidentiality and integrity of information at rest.',
    riskLevel: 'HIGH'
  },

  // Configuration Management (CM) Family
  'CM-1': {
    family: 'Configuration Management',
    name: 'Configuration Management Policy',
    description: 'Establishes organizational configuration management policy and procedures.',
    riskLevel: 'MEDIUM'
  },
  'CM-2': {
    family: 'Configuration Management',
    name: 'Baseline Configuration',
    description: 'Develops, documents, and maintains current baseline configuration of the information system.',
    riskLevel: 'MEDIUM'
  },
  'CM-6': {
    family: 'Configuration Management',
    name: 'Configuration Settings',
    description: 'Establishes and documents mandatory configuration settings for information technology products.',
    riskLevel: 'MEDIUM'
  },
  'CM-8': {
    family: 'Configuration Management',
    name: 'Information System Component Inventory',
    description: 'Develops and documents inventory of information system components.',
    riskLevel: 'MEDIUM'
  },

  // Incident Response (IR) Family
  'IR-1': {
    family: 'Incident Response',
    name: 'Incident Response Policy and Procedures',
    description: 'Establishes organizational incident response policy and procedures.',
    riskLevel: 'MEDIUM'
  },
  'IR-4': {
    family: 'Incident Response',
    name: 'Incident Handling',
    description: 'Implements incident handling capability for security incidents.',
    riskLevel: 'HIGH'
  },
  'IR-5': {
    family: 'Incident Response',
    name: 'Incident Monitoring',
    description: 'Tracks and documents information system security incidents.',
    riskLevel: 'MEDIUM'
  },
  'IR-6': {
    family: 'Incident Response',
    name: 'Incident Reporting',
    description: 'Requires personnel to report suspected security incidents to organizational incident response capability.',
    riskLevel: 'HIGH'
  },
  'IR-8': {
    family: 'Incident Response',
    name: 'Incident Response Plan',
    description: 'Develops incident response plan that provides organized approach to addressing and managing incidents.',
    riskLevel: 'HIGH'
  },

  // Risk Assessment (RA) Family
  'RA-1': {
    family: 'Risk Assessment',
    name: 'Risk Assessment Policy and Procedures',
    description: 'Establishes organizational risk assessment policy and procedures.',
    riskLevel: 'MEDIUM'
  },
  'RA-3': {
    family: 'Risk Assessment',
    name: 'Risk Assessment',
    description: 'Conducts assessment of risk arising from operation of information system and associated data processing.',
    riskLevel: 'HIGH'
  },
  'RA-5': {
    family: 'Risk Assessment',
    name: 'Vulnerability Scanning',
    description: 'Scans for vulnerabilities in the information system and hosted applications.',
    riskLevel: 'HIGH'
  },

  // Awareness and Training (AT) Family
  'AT-1': {
    family: 'Awareness and Training',
    name: 'Security Awareness and Training Policy',
    description: 'Establishes organizational security awareness and training policy and procedures.',
    riskLevel: 'LOW'
  },
  'AT-2': {
    family: 'Awareness and Training',
    name: 'Security Awareness Training',
    description: 'Provides basic security awareness training to information system users.',
    riskLevel: 'MEDIUM'
  },
  'AT-3': {
    family: 'Awareness and Training',
    name: 'Role-Based Security Training',
    description: 'Provides role-based security training to personnel with assigned security roles.',
    riskLevel: 'MEDIUM'
  }
};

interface ControlBadgeProps {
  controlId: string;
  variant?: 'default' | 'outline' | 'secondary' | 'destructive';
  size?: 'default' | 'sm' | 'lg';
  className?: string;
}

export function ControlBadge({ controlId, variant = 'outline', size = 'default', className = '' }: ControlBadgeProps) {
  const controlInfo = controlsDatabase[controlId];
  
  if (!controlInfo) {
    return (
      <Badge variant={variant} className={className}>
        {controlId}
      </Badge>
    );
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'HIGH':
        return 'text-red-500';
      case 'MEDIUM':
        return 'text-amber-500';
      case 'LOW':
        return 'text-green-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Badge 
          variant={variant} 
          size={size}
          className={`cursor-help transition-colors hover:bg-primary/10 hover:border-primary/50 ${className}`}
        >
          {controlId}
        </Badge>
      </TooltipTrigger>
      <TooltipContent 
        side="top"
        align="center"
        sideOffset={8}
        className="max-w-sm p-4 bg-popover text-popover-foreground border border-border shadow-xl rounded-lg z-[9999]"
      >
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-primary/10 rounded flex items-center justify-center">
              <Shield className="h-3 w-3 text-primary" />
            </div>
            <span className="font-semibold text-popover-foreground">{controlId}</span>
            <div className={`w-2 h-2 rounded-full ${getRiskColor(controlInfo.riskLevel)}`} />
          </div>
          
          {/* Family */}
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {controlInfo.family}
            </p>
            <p className="font-medium text-sm text-popover-foreground">
              {controlInfo.name}
            </p>
          </div>
          
          {/* Description */}
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Description:</p>
            <p className="text-xs text-popover-foreground leading-relaxed">
              {controlInfo.description}
            </p>
          </div>
          
          {/* Risk Level */}
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <span className="text-xs text-muted-foreground">Risk Level:</span>
            <Badge 
              variant="outline" 
              className={`text-xs ${getRiskColor(controlInfo.riskLevel)} border-current`}
            >
              {controlInfo.riskLevel}
            </Badge>
          </div>
        </div>
      </TooltipContent>
    </Tooltip>
  );
}

// Export the database for other components that might need it
export { controlsDatabase };