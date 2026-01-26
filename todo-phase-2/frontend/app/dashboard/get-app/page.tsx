"use client";

import Image from "next/image";
import Link from "next/link";

const features = [
  {
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    title: "Lightning Fast",
    description: "Native performance with instant task creation and updates",
  },
  {
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
    title: "Smart Notifications",
    description: "Get reminded at the right time with intelligent push notifications",
  },
  {
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
    title: "Secure & Private",
    description: "Your data is protected with industry-standard encryption",
  },
  {
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    title: "Real-time Sync",
    description: "Seamlessly sync across all your devices instantly",
  },
  {
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
    ),
    title: "Dark Mode",
    description: "Easy on the eyes with beautiful dark and light themes",
  },
];

export default function GetAppPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-blue-500/10 blur-3xl" />
          <div className="absolute top-40 -left-40 h-80 w-80 rounded-full bg-indigo-500/10 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-16 lg:items-center">
            {/* Left content */}
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 dark:bg-blue-900/30 px-4 py-1.5 mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                </span>
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">New Release Available</span>
              </div>

              <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl lg:text-6xl">
                DoneKaro
                <span className="block text-blue-600 dark:text-blue-400">Mobile App</span>
              </h1>

              <p className="mt-6 text-lg text-gray-600 dark:text-gray-300 max-w-xl mx-auto lg:mx-0">
                Take your productivity everywhere. Get the DoneKaro mobile app for the fastest,
                most seamless task management experience on your Android device.
              </p>

              {/* Download Button */}
              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <a
                  href="/donekaro-1.0.apk"
                  download
                  className="group inline-flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-4 text-lg font-semibold text-white shadow-xl shadow-blue-500/25 hover:shadow-2xl hover:shadow-blue-500/30 transition-all duration-300 hover:scale-105"
                >
                  <svg className="h-7 w-7" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.523 2.047c-.34-.34-.773-.507-1.3-.507H7.777c-.527 0-.96.168-1.3.507-.34.34-.507.773-.507 1.3v17.306c0 .527.168.96.507 1.3.34.34.773.507 1.3.507h8.446c.527 0 .96-.168 1.3-.507.34-.34.507-.773.507-1.3V3.347c0-.527-.168-.96-.507-1.3zM12 20.83c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25zm4.17-4.17H7.83V4.83h8.34v11.83z"/>
                  </svg>
                  <span>Download for Android</span>
                  <svg className="h-5 w-5 group-hover:translate-y-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </a>

                <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <svg className="h-5 w-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span>Safe & Verified</span>
                </div>
              </div>

              {/* Version info */}
              <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                Version 1.0 • Requires Android 8.0 or higher • 15MB
              </p>
            </div>

            {/* Right - Phone mockup with actual screenshot */}
            <div className="mt-16 lg:mt-0 flex justify-center">
              <div className="relative">
                {/* Glow effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-[2.5rem] blur-3xl opacity-20 scale-110" />

                {/* Phone frame - adjusted for typical mobile screenshot ratio (9:20) */}
                <div className="relative bg-gray-900 rounded-[2.5rem] p-2 shadow-2xl">
                  {/* Inner bezel */}
                  <div className="bg-black rounded-[2.2rem] p-1 overflow-hidden">
                    {/* Notch/Dynamic Island */}
                    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 w-20 h-6 bg-black rounded-full" />

                    {/* Screenshot container - maintains aspect ratio */}
                    <div className="relative w-[280px] h-[600px] rounded-[2rem] overflow-hidden bg-gray-900">
                      <Image
                        src="/DoneKaro App.png"
                        alt="DoneKaro App Screenshot"
                        fill
                        className="object-cover object-top"
                        priority
                      />
                    </div>
                  </div>

                  {/* Side buttons */}
                  <div className="absolute right-[-3px] top-24 w-1 h-12 bg-gray-700 rounded-l-sm" />
                  <div className="absolute left-[-3px] top-20 w-1 h-8 bg-gray-700 rounded-r-sm" />
                  <div className="absolute left-[-3px] top-32 w-1 h-16 bg-gray-700 rounded-r-sm" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">
            Why you&apos;ll love the app
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Built for speed and reliability, the DoneKaro app brings all your tasks right to your fingertips.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group relative bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-lg hover:border-blue-200 dark:hover:border-blue-800 transition-all duration-300"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
                {feature.icon}
              </div>
              <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
                {feature.title}
              </h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 px-8 py-16 shadow-2xl">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-10">
            <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <defs>
                <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                  <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100" height="100" fill="url(#grid)" />
            </svg>
          </div>

          <div className="relative text-center">
            <h2 className="text-3xl font-bold text-white sm:text-4xl">
              Ready to get more done?
            </h2>
            <p className="mt-4 text-lg text-blue-100 max-w-2xl mx-auto">
              Download DoneKaro now and experience the future of task management. It&apos;s free and always will be.
            </p>
            <div className="mt-8">
              <a
                href="/donekaro-1.0.apk"
                download
                className="inline-flex items-center justify-center gap-3 rounded-xl bg-white px-8 py-4 text-lg font-semibold text-blue-600 shadow-lg hover:bg-blue-50 transition-colors"
              >
                <svg className="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.523 2.047c-.34-.34-.773-.507-1.3-.507H7.777c-.527 0-.96.168-1.3.507-.34.34-.507.773-.507 1.3v17.306c0 .527.168.96.507 1.3.34.34.773.507 1.3.507h8.446c.527 0 .96-.168 1.3-.507.34-.34.507-.773.507-1.3V3.347c0-.527-.168-.96-.507-1.3zM12 20.83c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25zm4.17-4.17H7.83V4.83h8.34v11.83z"/>
                </svg>
                Download APK
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Installation Guide */}
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            How to install
          </h2>
        </div>

        <div className="max-w-3xl mx-auto">
          <div className="space-y-6">
            <div className="flex gap-4">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold">
                1
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Download the APK</h3>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  Click the download button above to get the latest version of DoneKaro app.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold">
                2
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Enable unknown sources</h3>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  Go to Settings &rarr; Security &rarr; Enable &quot;Install from unknown sources&quot; for your browser.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold">
                3
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Install & enjoy</h3>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  Open the downloaded file and follow the installation prompts. You&apos;re all set!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer note */}
      <div className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
        <div className="text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            DoneKaro is available for Android devices. iOS version coming soon.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 mt-4 text-blue-600 dark:text-blue-400 hover:underline"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
