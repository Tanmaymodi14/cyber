import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Shield, Check, ArrowRight } from 'lucide-react';
import { useState } from 'react';

interface FrameworkSelectionProps {
  onNavigate: (page: string) => void;
  onFrameworkSelect?: (frameworkId: string, frameworkData: {id: string, title: string}) => void;
}

export function FrameworkSelection({ onNavigate, onFrameworkSelect }: FrameworkSelectionProps) {
  const [selectedFramework, setSelectedFramework] = useState<string | null>(null);

  const frameworks = [
    {
      id: 'fedramp-low',
      title: 'FedRAMP Low',
      description: 'Systems that process public information with low impact',
      controls: 125,
      category: 'Government',
      popular: false
    },
    {
      id: 'fedramp-moderate',
      title: 'FedRAMP Moderate',
      description: 'Systems with moderate impact on operations and assets (22 AC controls)',
      controls: 325,
      category: 'Government',
      popular: true
    },
    {
      id: 'fedramp-high',
      title: 'FedRAMP High',
      description: 'Systems with high impact requiring maximum security',
      controls: 421,
      category: 'Government',
      popular: false
    },
    {
      id: 'nist',
      title: 'NIST Cybersecurity Framework',
      description: 'Comprehensive framework for managing cybersecurity risk',
      controls: 108,
      category: 'Industry Standard',
      popular: true
    },
    {
      id: 'iso27001',
      title: 'ISO 27001',
      description: 'International standard for information security management',
      controls: 114,
      category: 'International',
      popular: false
    },
    {
      id: 'pci-dss',
      title: 'PCI DSS',
      description: 'Payment Card Industry Data Security Standard',
      controls: 78,
      category: 'Industry Specific',
      popular: false
    }
  ];

  const getSelectedFramework = () => {
    return frameworks.find(f => f.id === selectedFramework);
  };

  const handleFrameworkSelect = (frameworkId: string) => {
    setSelectedFramework(frameworkId);
  };

  const handleContinue = () => {
    if (selectedFramework) {
      const frameworkData = frameworks.find(f => f.id === selectedFramework);
      if (onFrameworkSelect && frameworkData) {
        onFrameworkSelect(selectedFramework, {id: frameworkData.id, title: frameworkData.title});
      } else {
        onNavigate('upload');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-card">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">proTecht</span>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant="outline">Step 1 of 3</Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 lg:py-12">
        <div className="max-w-6xl mx-auto">
          {/* Title Section */}
          <div className="text-center mb-8 lg:mb-12">
            <h1 className="text-2xl lg:text-3xl font-bold mb-4">
              Select Your Compliance Framework
            </h1>
            <p className="text-base lg:text-lg text-muted-foreground max-w-2xl mx-auto">
              Choose the cybersecurity compliance framework for Access Control (AC) family assessment.
            </p>
          </div>

          {/* Framework Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6 mb-8">
            {frameworks.map((framework) => (
              <Card
                key={framework.id}
                className={`cursor-pointer transition-all duration-200 hover:shadow-lg border-2 h-full ${
                  selectedFramework === framework.id
                    ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                    : 'border-border hover:border-primary/50'
                }`}
                onClick={() => handleFrameworkSelect(framework.id)}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start flex-wrap gap-2 mb-3">
                        <CardTitle className="text-base lg:text-lg leading-tight">
                          {framework.title}
                        </CardTitle>
                        {framework.popular && (
                          <Badge variant="secondary" className="text-xs whitespace-nowrap">
                            Popular
                          </Badge>
                        )}
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {framework.category}
                      </Badge>
                    </div>
                    {selectedFramework === framework.id && (
                      <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                        <Check className="h-4 w-4 text-primary-foreground" />
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <CardDescription className="mb-4 text-sm">
                    {framework.description}
                  </CardDescription>
                  <div className="text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">{framework.controls}</span> controls to assess
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Selected Framework Summary */}
          {selectedFramework && (
            <Card className="bg-primary/5 border-primary/20 mb-6">
              <CardContent className="pt-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="font-semibold mb-2">
                      Selected: {getSelectedFramework()?.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Ready to begin Access Control (AC) family assessment with{' '}
                      <span className="font-medium">22 AC controls</span> from {getSelectedFramework()?.controls} total controls
                    </p>
                  </div>
                  <Button onClick={handleContinue} size="lg" className="w-full sm:w-auto">
                    Continue to Upload
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* No Selection Message */}
          {!selectedFramework && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                Select a framework above to continue with your compliance assessment
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}