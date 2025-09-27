import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Shield, Upload, Cloud, FileText, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import { useState } from 'react';

interface UploadPageProps {
  onNavigate: (page: string) => void;
  selectedFramework?: {id: string, title: string} | null;
}

export function UploadPage({ onNavigate, selectedFramework }: UploadPageProps) {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [awsConnected, setAwsConnected] = useState(false);
  const [awsRoleArn, setAwsRoleArn] = useState('');

  const handleFileUpload = (files: FileList | null) => {
    if (!files) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    
    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          const newFiles = Array.from(files).map(file => file.name);
          setUploadedFiles(prev => [...prev, ...newFiles]);
          return 100;
        }
        return prev + 20;
      });
    }, 500);
  };

  const handleAwsConnect = () => {
    if (awsRoleArn) {
      setAwsConnected(true);
    }
  };

  const canContinue = uploadedFiles.length > 0 || awsConnected;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-card">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">proTecht</span>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant="outline">Step 2 of 3</Badge>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold mb-4">
              Upload Evidence & Connect Infrastructure
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Upload your policies and procedures, and connect your cloud infrastructure for automated Access Control (AC) compliance assessment.
            </p>
            <div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg max-w-2xl mx-auto">
              <p className="text-sm text-muted-foreground">
                <strong>Focus:</strong> This assessment will analyze 22 Access Control (AC) controls including account management, 
                access enforcement, session controls, and information flow enforcement using both your policies and AWS infrastructure.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Document Upload */}
            <Card>
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-primary" />
                  <CardTitle>Policy & Document Upload</CardTitle>
                </div>
                <CardDescription>
                  Upload AC-related policies like Access Control Policy, Remote Access Policy, and System Access Procedures (PDF, DOCX)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer">
                  <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Drag & drop files here</p>
                    <p className="text-xs text-muted-foreground">or click to browse</p>
                  </div>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.docx,.doc"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    onChange={(e) => handleFileUpload(e.target.files)}
                  />
                </div>

                {isUploading && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Uploading...</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <Progress value={uploadProgress} />
                  </div>
                )}

                {uploadedFiles.length > 0 && (
                  <div className="space-y-2">
                    <Label>Uploaded Files</Label>
                    <div className="space-y-2">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center space-x-2 p-2 bg-secondary/20 rounded">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{file}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* AWS Integration */}
            <Card>
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <Cloud className="h-5 w-5 text-primary" />
                  <CardTitle>Cloud Infrastructure</CardTitle>
                </div>
                <CardDescription>
                  Connect your AWS account to analyze IAM, VPC, S3, WAF, and other services for AC controls
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {!awsConnected ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="aws-role">AWS IAM Role ARN</Label>
                      <Input
                        id="aws-role"
                        placeholder="arn:aws:iam::123456789012:role/proTecht-ReadOnly"
                        value={awsRoleArn}
                        onChange={(e) => setAwsRoleArn(e.target.value)}
                      />
                    </div>

                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" className="w-full">
                          How to set up AWS Role
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>AWS IAM Role Setup</DialogTitle>
                          <DialogDescription>
                            Follow these steps to create a read-only IAM role for proTecht:
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 text-sm">
                          <div>
                            <p className="font-medium">1. Create IAM Role</p>
                            <p className="text-muted-foreground">In AWS Console, go to IAM → Roles → Create Role</p>
                          </div>
                          <div>
                            <p className="font-medium">2. Set Trust Policy</p>
                            <p className="text-muted-foreground">Allow external account access with proper conditions</p>
                          </div>
                          <div>
                            <p className="font-medium">3. Attach Policies</p>
                            <p className="text-muted-foreground">Attach ReadOnlyAccess and SecurityAudit policies</p>
                          </div>
                          <div>
                            <p className="font-medium">4. Copy ARN</p>
                            <p className="text-muted-foreground">Copy the role ARN and paste it above</p>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>

                    <Button 
                      onClick={handleAwsConnect} 
                      className="w-full"
                      disabled={!awsRoleArn}
                    >
                      Connect AWS Account
                    </Button>
                  </>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <div>
                        <p className="font-medium text-green-700 dark:text-green-300">AWS Connected</p>
                        <p className="text-sm text-green-600 dark:text-green-400">Infrastructure scanning enabled</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="bg-secondary/20 p-3 rounded">
                        <p className="font-medium">EC2 Instances</p>
                        <p className="text-2xl font-bold text-primary">12</p>
                      </div>
                      <div className="bg-secondary/20 p-3 rounded">
                        <p className="font-medium">S3 Buckets</p>
                        <p className="text-2xl font-bold text-primary">8</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Continue Button */}
          <Card className={canContinue ? "bg-primary/5 border-primary/20" : "bg-muted/20"}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold mb-2">
                    {canContinue ? "Ready for Analysis" : "Upload Required"}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {canContinue 
                      ? "Evidence uploaded successfully. Ready to begin compliance analysis."
                      : "Please upload documents or connect AWS to continue."
                    }
                  </p>
                </div>
                <Button 
                  onClick={() => onNavigate('dashboard')} 
                  size="lg"
                  disabled={!canContinue}
                >
                  Start Analysis
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Warning for demo */}
          <Card className="mt-6 border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/20">
            <CardContent className="pt-6">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-amber-800 dark:text-amber-200">Demo Mode</h4>
                  <p className="text-sm text-amber-700 dark:text-amber-300">
                    This is a demonstration. No actual files are uploaded or AWS connections made. 
                    Real implementation would include secure file storage and proper AWS integration.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}