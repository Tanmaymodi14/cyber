import { useState } from 'react';
import { LandingPage } from './components/LandingPage';
import { LoginPage } from './components/LoginPage';
import { SignupPage } from './components/SignupPage';
import { FrameworkSelection } from './components/FrameworkSelection';
import { UploadPage } from './components/UploadPage';
import { Dashboard } from './components/Dashboard';
import { ControlDetails } from './components/ControlDetails';
import { EvidenceManagement } from './components/EvidenceManagement';
import { SSPGenerator } from './components/SSPGenerator';
import { Reports } from './components/Reports';
import { Settings } from './components/Settings';
import { TooltipProvider } from './components/ui/tooltip';
import { Toaster } from './components/ui/sonner';
import { AnimatedBackground } from './components/AnimatedBackground';

type Page = 'landing' | 'login' | 'signup' | 'framework' | 'upload' | 'dashboard' | 'controls' | 'evidence' | 'ssp' | 'reports' | 'settings';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedFramework, setSelectedFramework] = useState<string | null>(null);
  const [selectedFrameworkData, setSelectedFrameworkData] = useState<{id: string, title: string} | null>(null);
  const [controlFilter, setControlFilter] = useState<string | null>(null);

  // Force dark mode for the cybersecurity theme
  if (typeof document !== 'undefined') {
    document.documentElement.classList.add('dark');
  }

  const handleAuth = () => {
    setIsAuthenticated(true);
    setCurrentPage('framework');
  };

  const handleFrameworkSelection = (frameworkId: string, frameworkData: {id: string, title: string}) => {
    setSelectedFramework(frameworkId);
    setSelectedFrameworkData(frameworkData);
    setCurrentPage('upload');
  };

  // Simple hash router + deep-link: #/controls?control=AC-15
  if (typeof window !== 'undefined') {
    window.onhashchange = () => {
      const hash = window.location.hash || '';
      if (hash.startsWith('#/controls')) {
        setCurrentPage('controls');
        const params = new URLSearchParams(hash.split('?')[1] || '');
        setControlFilter(params.get('control'));
      } else if (hash.startsWith('#/evidence')) {
        setCurrentPage('evidence');
      }
    };
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage onNavigate={setCurrentPage} />;
      case 'login':
        return <LoginPage onAuth={handleAuth} onNavigate={setCurrentPage} />;
      case 'signup':
        return <SignupPage onAuth={handleAuth} onNavigate={setCurrentPage} />;
      case 'framework':
        return <FrameworkSelection onNavigate={setCurrentPage} onFrameworkSelect={handleFrameworkSelection} />;
      case 'upload':
        return <UploadPage onNavigate={setCurrentPage} selectedFramework={selectedFrameworkData} />;
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentPage} selectedFramework={selectedFrameworkData} />;
      case 'controls':
        return <ControlDetails onNavigate={setCurrentPage} selectedFramework={selectedFrameworkData} />;
      case 'evidence':
        return <EvidenceManagement onNavigate={setCurrentPage} selectedFramework={selectedFrameworkData} />;
      case 'ssp':
        return <SSPGenerator onNavigate={setCurrentPage} selectedFramework={selectedFrameworkData} />;
      case 'reports':
        return <Reports onNavigate={setCurrentPage} selectedFramework={selectedFrameworkData} />;
      case 'settings':
        return <Settings onNavigate={setCurrentPage} selectedFramework={selectedFrameworkData} />;
      default:
        return <LandingPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <TooltipProvider delayDuration={300}>
      <div className="min-h-screen bg-background text-foreground relative">
        <AnimatedBackground />
        <div className="relative z-10">
          {renderPage()}
        </div>
        <Toaster richColors position="top-right" />
      </div>
    </TooltipProvider>
  );
}