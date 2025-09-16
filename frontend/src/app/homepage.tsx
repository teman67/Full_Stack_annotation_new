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
        <section className="flex-1 flex items-center justify-center bg-gradient-to-b from-background to-background/80">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                  Scientific Text Annotator
                </h1>
                <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                  AI-powered annotation platform for scientific documents.
                  Streamline your research workflow with intelligent text
                  processing and collaborative annotation tools.
                </p>
              </div>
              <div className="space-x-4">
                <Button asChild size="lg">
                  <Link href="/auth/register">Get Started</Link>
                </Button>
                <Button variant="outline" asChild size="lg">
                  <Link href="/auth/login">Sign In</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-50 dark:bg-gray-900">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
                  Powerful Features
                </h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
                  Everything you need to annotate scientific texts efficiently
                  and accurately.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl items-center gap-6 py-12 lg:grid-cols-2 lg:gap-12">
              <div className="grid gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Zap className="h-5 w-5" />
                      <span>AI-Powered Annotation</span>
                    </CardTitle>
                    <CardDescription>
                      Leverage advanced language models to automatically
                      identify and annotate entities in your scientific texts.
                    </CardDescription>
                  </CardHeader>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Users className="h-5 w-5" />
                      <span>Team Collaboration</span>
                    </CardTitle>
                    <CardDescription>
                      Work together with your research team in real-time with
                      shared projects and collaborative annotation tools.
                    </CardDescription>
                  </CardHeader>
                </Card>
              </div>
              <div className="grid gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <FileText className="h-5 w-5" />
                      <span>Multiple Formats</span>
                    </CardTitle>
                    <CardDescription>
                      Support for various document formats including TXT, PDF,
                      and DOCX with easy export to CoNLL and JSON formats.
                    </CardDescription>
                  </CardHeader>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Shield className="h-5 w-5" />
                      <span>Quality Validation</span>
                    </CardTitle>
                    <CardDescription>
                      Built-in validation tools to ensure annotation quality and
                      consistency across your research projects.
                    </CardDescription>
                  </CardHeader>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
                  Ready to Transform Your Research?
                </h2>
                <p className="max-w-[600px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
                  Join researchers worldwide who are using our platform to
                  accelerate their scientific discovery.
                </p>
              </div>
              <div className="space-x-4">
                <Button asChild size="lg">
                  <Link href="/auth/register">Start Free Trial</Link>
                </Button>
                <Button variant="outline" asChild size="lg">
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
