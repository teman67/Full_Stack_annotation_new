import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AppLayout } from "@/components/layout/AppLayout";
import { FileText, Users, Zap, Shield } from "lucide-react";

export default function Home() {
  return (
    <AppLayout>
      <div className="flex flex-col min-h-screen">
        {/* Hero Section */}
        <section className="flex-1 flex items-center justify-center relative overflow-hidden">
          {/* Subtle background decoration without conflicting gradients */}
          <div className="absolute inset-0 bg-grid-blue-200/[0.03] bg-[size:50px_50px]" />
          <div className="absolute inset-0">
            <div className="absolute top-20 left-20 w-32 h-32 bg-blue-300/15 rounded-full blur-3xl" />
            <div className="absolute bottom-20 right-20 w-40 h-40 bg-blue-400/20 rounded-full blur-3xl" />
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-blue-200/5 to-blue-300/10 rounded-full blur-3xl" />
          </div>

          <div className="container px-4 md:px-6 relative z-10 max-w-5xl mx-auto">
            <div className="flex flex-col items-center space-y-8 text-center">
              <div className="space-y-6">
                <div className="inline-flex items-center rounded-full bg-primary/10 px-4 py-2 text-sm text-primary font-medium">
                  ✨ AI-Powered Research Platform
                </div>
                <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl bg-gradient-to-br from-foreground via-foreground to-foreground/70 bg-clip-text text-transparent leading-[1.1]">
                  Scientific Text
                  <br />
                  <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    Annotator
                  </span>
                </h1>
                <p className="mx-auto max-w-[680px] text-muted-foreground text-lg md:text-xl leading-relaxed">
                  Transform your research workflow with intelligent text
                  processing, collaborative annotation tools, and AI-powered
                  insights for scientific documents.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  asChild
                  size="lg"
                  className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white shadow-lg shadow-primary/25"
                >
                  <Link href="/auth/register">
                    Get Started Free
                    <span className="ml-2">→</span>
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  asChild
                  size="lg"
                  className="border-primary/20 hover:bg-primary/5"
                >
                  <Link href="/auth/login">Sign In</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="w-full py-16 md:py-24 lg:py-32 relative">
          {/* Subtle overlay to enhance the main gradient */}
          <div className="absolute inset-0 bg-blue-50/20" />
          <div className="container px-4 md:px-6 mx-auto relative z-10">
            <div className="section-center space-y-12 w-full">
              <div className="section-center space-y-6 w-full max-w-5xl mx-auto">
                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl leading-tight text-center-force w-full">
                  Powerful Features for Modern Research
                </h2>
                <p className="max-w-[700px] text-muted-foreground text-lg md:text-xl leading-relaxed mx-auto text-center-force w-full">
                  Everything you need to accelerate your scientific research and
                  collaboration with cutting-edge AI technology
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-6xl items-start gap-8 py-12 lg:grid-cols-2 lg:gap-12">
              <div className="grid gap-6">
                <Card className="group hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 border-border/50 hover:border-primary/20 h-full">
                  <CardHeader className="space-y-4 text-left">
                    <CardTitle className="flex items-start space-x-3 text-xl">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-white group-hover:scale-110 transition-transform duration-300 flex-shrink-0 mt-1">
                        <Zap className="h-5 w-5" />
                      </div>
                      <span className="leading-tight">
                        AI-Powered Annotation
                      </span>
                    </CardTitle>
                    <CardDescription className="text-muted-foreground leading-relaxed text-base">
                      Leverage advanced language models to automatically
                      identify and annotate entities in your scientific texts
                      with unprecedented accuracy and speed.
                    </CardDescription>
                  </CardHeader>
                </Card>
                <Card className="group hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 border-border/50 hover:border-primary/20 h-full">
                  <CardHeader className="space-y-4 text-left">
                    <CardTitle className="flex items-start space-x-3 text-xl">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-accent to-primary text-white group-hover:scale-110 transition-transform duration-300 flex-shrink-0 mt-1">
                        <Users className="h-5 w-5" />
                      </div>
                      <span className="leading-tight">Team Collaboration</span>
                    </CardTitle>
                    <CardDescription className="text-muted-foreground leading-relaxed text-base">
                      Work together with your research team in real-time with
                      shared projects, collaborative annotation tools, and
                      seamless communication.
                    </CardDescription>
                  </CardHeader>
                </Card>
              </div>
              <div className="grid gap-6">
                <Card className="group hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 border-border/50 hover:border-primary/20 h-full">
                  <CardHeader className="space-y-4 text-left">
                    <CardTitle className="flex items-start space-x-3 text-xl">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-white group-hover:scale-110 transition-transform duration-300 flex-shrink-0 mt-1">
                        <FileText className="h-5 w-5" />
                      </div>
                      <span className="leading-tight">Multiple Formats</span>
                    </CardTitle>
                    <CardDescription className="text-muted-foreground leading-relaxed text-base">
                      Support for various document formats including TXT, PDF,
                      and DOCX with easy export to CoNLL and JSON formats for
                      analysis.
                    </CardDescription>
                  </CardHeader>
                </Card>
                <Card className="group hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 border-border/50 hover:border-primary/20 h-full">
                  <CardHeader className="space-y-4 text-left">
                    <CardTitle className="flex items-start space-x-3 text-xl">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-accent to-primary text-white group-hover:scale-110 transition-transform duration-300 flex-shrink-0 mt-1">
                        <Shield className="h-5 w-5" />
                      </div>
                      <span className="leading-tight">Quality Validation</span>
                    </CardTitle>
                    <CardDescription className="text-muted-foreground leading-relaxed text-base">
                      Built-in validation tools to ensure annotation quality and
                      consistency across your research projects with automated
                      checks.
                    </CardDescription>
                  </CardHeader>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full py-16 md:py-24 lg:py-32 relative">
          {/* Subtle overlay to enhance the main gradient at the bottom */}
          <div className="absolute inset-0 bg-blue-100/30" />
          <div className="container px-4 md:px-6 mx-auto relative z-10">
            <div className="section-center space-y-6 w-full max-w-4xl mx-auto">
              <div className="section-center space-y-4 w-full">
                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-center-force w-full">
                  Ready to Transform Your Research?
                </h2>
                <p className="max-w-[600px] text-muted-foreground text-lg md:text-xl/relaxed text-center-force mx-auto w-full">
                  Join researchers worldwide who are using our platform to
                  accelerate their scientific discovery and collaboration.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  asChild
                  size="lg"
                  className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white shadow-lg shadow-primary/25"
                >
                  <Link href="/auth/register">
                    Start Free Trial
                    <span className="ml-2">→</span>
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  asChild
                  size="lg"
                  className="border-primary/20 hover:bg-primary/5"
                >
                  <Link href="/demo">View Demo</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
