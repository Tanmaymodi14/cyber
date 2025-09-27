import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Shield, Zap, Upload, FileText, ChevronLeft, ChevronRight, Github, Linkedin, Sparkles, Lock, Target } from 'lucide-react';
import { useState, useEffect } from 'react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { motion, AnimatePresence } from 'motion/react';

interface LandingPageProps {
  onNavigate: (page: string) => void;
}

export function LandingPage({ onNavigate }: LandingPageProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Auto-advance carousel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % demoScreenshots.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Mouse tracking for hero section
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);
  
  const demoScreenshots = [
    {
      title: "Compliance Dashboard",
      image: "https://images.unsplash.com/photo-1748609160056-7b95f30041f0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkYXNoYm9hcmQlMjBhbmFseXRpY3MlMjBjaGFydHN8ZW58MXx8fHwxNzU4NDk0MjA4fDA&ixlib=rb-4.1.0&q=80&w=1080",
      description: "Real-time compliance monitoring and analytics"
    },
    {
      title: "Control Management",
      image: "https://images.unsplash.com/photo-1655393001768-d946c97d6fd1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb21wbGlhbmNlJTIwYXV0b21hdGlvbiUyMHdvcmtmbG93fGVufDF8fHx8MTc1ODQ5NDIxMHww&ixlib=rb-4.1.0&q=80&w=1080",
      description: "Automated control assessment and evidence mapping"
    },
    {
      title: "Evidence Collection",
      image: "https://images.unsplash.com/photo-1714964739533-79c5dfcb48bc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjbG91ZCUyMHNlY3VyaXR5JTIwc2hpZWxkfGVufDF8fHx8MTc1ODQ5NDIxMnww&ixlib=rb-4.1.0&q=80&w=1080",
      description: "Cloud infrastructure scanning and policy analysis"
    }
  ];

  const features = [
    {
      icon: Shield,
      title: "Multi-Framework Support",
      description: "FedRAMP Low, Moderate & High compliance automation with support for NIST, ISO, and PCI frameworks."
    },
    {
      icon: Zap,
      title: "AI-Powered Analysis",
      description: "Advanced machine learning algorithms analyze your infrastructure and policies for compliance gaps."
    },
    {
      icon: Upload,
      title: "Policy & Evidence Upload",
      description: "Seamlessly upload policies, procedures, and evidence documents with automated mapping to controls."
    },
    {
      icon: FileText,
      title: "Auto-Generated SSP Reports",
      description: "Generate comprehensive System Security Plans (SSP) in DOCX and OSCAL JSON formats automatically."
    }
  ];

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % demoScreenshots.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + demoScreenshots.length) % demoScreenshots.length);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-card relative overflow-hidden">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-primary/20 rounded-full"
            initial={{ 
              x: Math.random() * window.innerWidth, 
              y: Math.random() * window.innerHeight 
            }}
            animate={{
              x: mousePosition.x / 50 + Math.sin(Date.now() / 1000 + i) * 100,
              y: mousePosition.y / 50 + Math.cos(Date.now() / 1000 + i) * 100,
            }}
            transition={{ type: "spring", damping: 20, stiffness: 50 }}
          />
        ))}
      </div>

      {/* Header */}
      <motion.header 
        className="border-b border-border bg-card/50 backdrop-blur-sm relative z-10"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <motion.div 
            className="flex items-center space-x-2"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 400 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            >
              <Shield className="h-8 w-8 text-primary" />
            </motion.div>
            <span className="text-2xl font-bold">proTecht</span>
          </motion.div>
          <div className="flex items-center space-x-4">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button variant="ghost" onClick={() => onNavigate('login')}>
                Login
              </Button>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button onClick={() => onNavigate('signup')}>
                Get Started
              </Button>
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <section className="py-20 px-4 relative z-10">
        <div className="container mx-auto text-center max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.h1 
              className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent"
              animate={{ 
                backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
              }}
              transition={{ duration: 5, repeat: Infinity }}
            >
              proTecht – AI-Powered Compliance Automation
            </motion.h1>
          </motion.div>
          
          <motion.p 
            className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            Automate your cybersecurity compliance with advanced AI analysis. Support for FedRAMP, NIST, ISO, and PCI frameworks.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button 
              size="lg" 
              className="text-lg px-8 py-6 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 shadow-2xl shadow-primary/25" 
              onClick={() => onNavigate('signup')}
            >
              <motion.span className="flex items-center">
                Start Free Demo
                <motion.div
                  animate={{ x: [0, 4, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <Zap className="ml-2 h-5 w-5" />
                </motion.div>
              </motion.span>
            </Button>
          </motion.div>

          {/* Floating security badges */}
          <div className="mt-12 flex justify-center space-x-8">
            {[
              { icon: Shield, label: "FedRAMP", delay: 0.6 },
              { icon: Lock, label: "NIST", delay: 0.8 },
              { icon: Target, label: "ISO 27001", delay: 1.0 }
            ].map((badge, index) => (
              <motion.div
                key={badge.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: badge.delay }}
                className="flex flex-col items-center space-y-2"
              >
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity, delay: index * 0.3 }}
                  className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center"
                >
                  <badge.icon className="h-6 w-6 text-primary" />
                </motion.div>
                <span className="text-sm text-muted-foreground">{badge.label}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-card/30">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Powerful Features for Modern Compliance
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="group hover:shadow-lg transition-all duration-300 border-border/50 hover:border-primary/50">
                  <CardHeader>
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Demo Screenshots Carousel */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            See proTecht in Action
          </h2>
          <div className="relative max-w-4xl mx-auto">
            <div className="overflow-hidden rounded-lg border border-border">
              <div className="relative h-64 md:h-96">
                <ImageWithFallback
                  src={demoScreenshots[currentSlide].image}
                  alt={demoScreenshots[currentSlide].title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4">
                  <h3 className="text-xl font-bold text-white mb-2">
                    {demoScreenshots[currentSlide].title}
                  </h3>
                  <p className="text-gray-200">
                    {demoScreenshots[currentSlide].description}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Carousel Controls */}
            <Button
              variant="outline"
              size="sm"
              className="absolute left-4 top-1/2 -translate-y-1/2 bg-background/80 backdrop-blur-sm"
              onClick={prevSlide}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-background/80 backdrop-blur-sm"
              onClick={nextSlide}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            
            {/* Carousel Indicators */}
            <div className="flex justify-center mt-6 space-x-2">
              {demoScreenshots.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentSlide(index)}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    index === currentSlide ? 'bg-primary' : 'bg-muted'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary/10 to-accent/10">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">
            Ready to Automate Your Compliance?
          </h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join hundreds of organizations already using proTecht to streamline their cybersecurity compliance.
          </p>
          <Button size="lg" className="text-lg px-8 py-6" onClick={() => onNavigate('signup')}>
            Get Started Today
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-4">
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <Shield className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold">proTecht</span>
          </div>
          <div className="flex items-center space-x-6">
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors flex items-center space-x-2"
            >
              <Github className="h-5 w-5" />
              <span>GitHub</span>
            </a>
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors flex items-center space-x-2"
            >
              <Linkedin className="h-5 w-5" />
              <span>LinkedIn</span>
            </a>
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              Help & Documentation
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}